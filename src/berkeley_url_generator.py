import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote


BERKELEY_ID = 79
BERKELEY_NAME = "University of California, Berkeley"
DEFAULT_YEAR = 76
DEFAULT_INSTITUTIONS_PATH = Path("data/institutions.json")
DEFAULT_URLS_PATH = Path("data/urls.json")
DEFAULT_MANIFEST_PATH = Path("data/url_manifest.json")


def load_institutions(json_data: str) -> list[dict[str, Any]]:
    return json.loads(json_data)


def institution_name(institution: dict[str, Any]) -> str:
    names = institution.get("names")
    if isinstance(names, list) and names:
        first_name = names[0]
        if isinstance(first_name, dict) and first_name.get("name"):
            return first_name["name"]
    return institution.get("name") or f"institution-{institution['id']}"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return slug.strip("-")


def filter_community_colleges(institutions: list[dict[str, Any]]) -> list[int]:
    return [inst["id"] for inst in institutions if inst.get("isCommunityCollege", False)]


def community_colleges(institutions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [inst for inst in institutions if inst.get("isCommunityCollege", False)]


def generate_assist_url(year: int, ccc_id: int, dest_id: int = BERKELEY_ID) -> str:
    view_by_key = f"{year}/{ccc_id}/to/{dest_id}/AllSendingPrefixes"
    encoded_view_by_key = quote(view_by_key, safe="")

    return (
        "https://assist.org/transfer/results?"
        f"year={year}&"
        f"institution={ccc_id}&"
        f"agreement={dest_id}&"
        "agreementType=to&"
        "viewAgreementsOptions=true&"
        "view=agreement&"
        "viewBy=prefix&"
        "viewSendingAgreements=true&"
        f"viewByKey={encoded_view_by_key}"
    )


def generate_output_filename(
    year: int,
    sending_institution_id: int,
    sending_institution_name: str,
    receiving_institution_id: int = BERKELEY_ID,
    receiving_institution_name: str = BERKELEY_NAME,
) -> str:
    sending_slug = slugify(sending_institution_name)
    receiving_slug = "uc-berkeley"
    if receiving_institution_name != BERKELEY_NAME:
        receiving_slug = slugify(receiving_institution_name)

    return (
        f"year_{year}_sending_{sending_institution_id:03d}_{sending_slug}"
        f"_to_{receiving_institution_id:03d}_{receiving_slug}.json"
    )


def generate_assist_manifest(
    institutions_json: str,
    year: int = DEFAULT_YEAR,
    receiving_institution_id: int = BERKELEY_ID,
    receiving_institution_name: str = BERKELEY_NAME,
) -> list[dict[str, Any]]:
    institutions = load_institutions(institutions_json)
    entries = []

    for institution in community_colleges(institutions):
        sending_id = institution["id"]
        sending_name = institution_name(institution)
        entries.append(
            {
                "academic_year_id": year,
                "sending_institution_id": sending_id,
                "sending_institution_name": sending_name,
                "receiving_institution_id": receiving_institution_id,
                "receiving_institution_name": receiving_institution_name,
                "url": generate_assist_url(year, sending_id, receiving_institution_id),
                "output_file": generate_output_filename(
                    year,
                    sending_id,
                    sending_name,
                    receiving_institution_id,
                    receiving_institution_name,
                ),
            }
        )

    return entries


def generate_all_assist_urls(
    institutions_json: str, year: int = DEFAULT_YEAR
) -> list[str]:
    return [entry["url"] for entry in generate_assist_manifest(institutions_json, year)]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> None:
    institutions_json = DEFAULT_INSTITUTIONS_PATH.read_text(encoding="utf-8")
    manifest = generate_assist_manifest(institutions_json)
    urls = [entry["url"] for entry in manifest]

    write_json(DEFAULT_MANIFEST_PATH, manifest)
    write_json(DEFAULT_URLS_PATH, urls)

    print(f"Generated {len(manifest)} Berkeley ASSIST manifest entries")
    print(f"Manifest saved to {DEFAULT_MANIFEST_PATH}")
    print(f"Compatibility URL list saved to {DEFAULT_URLS_PATH}")
    print("\nFirst 5 entries:")
    for index, entry in enumerate(manifest[:5], start=1):
        print(f"{index}. {entry['output_file']} -> {entry['url']}")


if __name__ == "__main__":
    main()
