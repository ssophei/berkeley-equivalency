import asyncio
import argparse
import json
from pathlib import Path
from typing import Any

from playwright.async_api import async_playwright


DEFAULT_MANIFEST_PATH = Path("data/url_manifest.json")
DEFAULT_OUTPUT_DIR = Path("data/articulations")
DEFAULT_FAILURES_PATH = Path("data/articulation_failures.json")
DEFAULT_RETRIES = 3
SEM = asyncio.Semaphore(3)


def unwrap_nested_json(data: Any) -> dict | list:
    def _unwrap(val: Any) -> Any:
        if isinstance(val, dict):
            return {key: _unwrap(value) for key, value in val.items()}
        if isinstance(val, list):
            return [_unwrap(elem) for elem in val]
        if isinstance(val, str):
            try:
                return _unwrap(json.loads(val))
            except json.JSONDecodeError:
                return val
        return val

    unwrapped = _unwrap(data)
    if isinstance(unwrapped, (dict, list)):
        return unwrapped
    raise TypeError("Top-level data must unwrap to a dict or list")


def load_fetch_entries(path: str | Path = DEFAULT_MANIFEST_PATH) -> list[dict[str, Any]]:
    manifest_path = Path(path)
    entries = json.loads(manifest_path.read_text(encoding="utf-8"))

    if not isinstance(entries, list):
        raise TypeError("Fetch manifest must contain a list")

    normalized_entries = []
    for index, entry in enumerate(entries, start=1):
        if isinstance(entry, str):
            normalized_entries.append(
                {
                    "url": entry,
                    "output_file": f"assist_data_{index}.json",
                }
            )
            continue
        if not isinstance(entry, dict) or "url" not in entry:
            raise TypeError(f"Invalid manifest entry at position {index}")
        normalized_entries.append(entry)

    return normalized_entries


def validate_capture(data: dict[str, Any], entry: dict[str, Any]) -> None:
    result = data.get("result") or {}
    sending = result.get("sendingInstitution") or {}
    receiving = result.get("receivingInstitution") or {}
    academic_year = result.get("academicYear") or {}

    expected_sending = entry.get("sending_institution_id")
    expected_receiving = entry.get("receiving_institution_id")
    expected_year = entry.get("academic_year_id")

    if expected_sending is not None and sending.get("id") != expected_sending:
        raise ValueError(
            f"Captured sending institution {sending.get('id')} does not match "
            f"manifest sending institution {expected_sending}"
        )
    if expected_receiving is not None and receiving.get("id") != expected_receiving:
        raise ValueError(
            f"Captured receiving institution {receiving.get('id')} does not match "
            f"manifest receiving institution {expected_receiving}"
        )
    if expected_year is not None and academic_year.get("id") != expected_year:
        raise ValueError(
            f"Captured academic year {academic_year.get('id')} does not match "
            f"manifest academic year {expected_year}"
        )


async def intercept(browser, url: str) -> dict[str, Any]:
    match_substring = "Agreements?Key="
    context = await browser.new_context()
    page = await context.new_page()

    try:
        async with page.expect_response(
            lambda response: match_substring in response.url,
            timeout=20000,
        ) as response_info:
            await page.goto(url, wait_until="domcontentloaded")

        response = await response_info.value
        json_data = await response.json()
        parsed_data = unwrap_nested_json(json_data)
        assert isinstance(parsed_data, dict)
        return parsed_data
    finally:
        await context.close()


def output_path_for_entry(
    entry: dict[str, Any], output_dir: str | Path = DEFAULT_OUTPUT_DIR
) -> Path:
    output_file = entry.get("output_file")
    if not output_file:
        raise ValueError("Manifest entry is missing output_file")
    return Path(output_dir) / output_file


async def worker(browser, entry: dict[str, Any], sem, output_dir: str | Path) -> None:
    async with sem:
        data = await intercept(browser, entry["url"])
        validate_capture(data, entry)

        filename = output_path_for_entry(entry, output_dir)
        filename.parent.mkdir(parents=True, exist_ok=True)
        filename.write_text(json.dumps(data, indent=4), encoding="utf-8")

        print(f"Agreement saved to {filename}")


def capture_failure(entry: dict[str, Any], error: BaseException) -> dict[str, Any]:
    return {
        "academic_year_id": entry.get("academic_year_id"),
        "sending_institution_id": entry.get("sending_institution_id"),
        "sending_institution_name": entry.get("sending_institution_name"),
        "receiving_institution_id": entry.get("receiving_institution_id"),
        "output_file": entry.get("output_file"),
        "url": entry.get("url"),
        "error_type": type(error).__name__,
        "error": str(error),
    }


async def worker_with_retries(
    browser,
    entry: dict[str, Any],
    sem,
    output_dir: str | Path,
    retries: int = DEFAULT_RETRIES,
    skip_existing: bool = True,
) -> dict[str, Any] | None:
    filename = output_path_for_entry(entry, output_dir)
    if skip_existing and filename.exists() and filename.stat().st_size > 0:
        print(f"Skipping existing agreement at {filename}")
        return None

    last_error: BaseException | None = None
    for attempt in range(1, retries + 1):
        try:
            await worker(browser, entry, sem, output_dir)
            return None
        except Exception as error:
            last_error = error
            print(
                f"Attempt {attempt}/{retries} failed for "
                f"{entry.get('sending_institution_name', entry.get('output_file'))}: "
                f"{error}"
            )
            if attempt < retries:
                await asyncio.sleep(attempt * 2)

    assert last_error is not None
    return capture_failure(entry, last_error)


async def single_url(url: str, output_file: str = "assist_data_1.json") -> None:
    entry = {"url": url, "output_file": output_file}
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            await worker(browser, entry, asyncio.Semaphore(1), DEFAULT_OUTPUT_DIR)
        finally:
            await browser.close()


async def main(
    start: int = 0,
    manifest_path: str | Path = DEFAULT_MANIFEST_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    failures_path: str | Path = DEFAULT_FAILURES_PATH,
    retries: int = DEFAULT_RETRIES,
    skip_existing: bool = True,
) -> None:
    entries = load_fetch_entries(manifest_path)[start:]

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            tasks = [
                worker_with_retries(
                    browser,
                    entry,
                    SEM,
                    output_dir,
                    retries,
                    skip_existing,
                )
                for entry in entries
            ]
            failures = [
                failure
                for failure in await asyncio.gather(*tasks)
                if failure is not None
            ]
        finally:
            await browser.close()

    failures_output = Path(failures_path)
    if failures:
        failures_output.parent.mkdir(parents=True, exist_ok=True)
        failures_output.write_text(json.dumps(failures, indent=2), encoding="utf-8")
        print(f"{len(failures)} agreements failed; see {failures_output}")
    elif failures_output.exists():
        failures_output.unlink()
        print("All agreements captured; removed stale failure report")
    else:
        print("All agreements captured")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture ASSIST articulation JSON files from a URL manifest."
    )
    parser.add_argument(
        "--start",
        default=0,
        type=int,
        help="Zero-based manifest index to start from.",
    )
    parser.add_argument(
        "--manifest",
        default=DEFAULT_MANIFEST_PATH,
        type=Path,
        help="Path to the URL manifest JSON file.",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        type=Path,
        help="Directory where raw articulation JSON files will be written.",
    )
    parser.add_argument(
        "--failures",
        default=DEFAULT_FAILURES_PATH,
        type=Path,
        help="Path to write a JSON report of agreements that failed after retries.",
    )
    parser.add_argument(
        "--retries",
        default=DEFAULT_RETRIES,
        type=int,
        help="Attempts per agreement before recording a failure.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Fetch agreements even when the output file already exists.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(
        main(
            args.start,
            args.manifest,
            args.output_dir,
            args.failures,
            args.retries,
            not args.force,
        )
    )
