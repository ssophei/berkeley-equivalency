import argparse
import json
from pathlib import Path

from parse_json import DEFAULT_INPUT_DIR, iter_input_files, parse_file


DEFAULT_OUTPUT_DIR = Path("data/normalized/articulations")


def normalized_output_path(input_path: Path, output_dir: Path) -> Path:
    return output_dir / f"{input_path.stem}.jsonl"


def write_normalized_file(input_path: str | Path, output_dir: str | Path) -> int:
    input_file = Path(input_path)
    output_path = normalized_output_path(input_file, Path(output_dir))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    records = parse_file(input_file)
    with output_path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, separators=(",", ":"), sort_keys=True))
            file.write("\n")

    return len(records)


def main(
    input_dir: str | Path = DEFAULT_INPUT_DIR,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, int]:
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    counts = {}
    for raw_file in iter_input_files(input_path):
        counts[raw_file.name] = write_normalized_file(raw_file, output_path)

    return counts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize each raw ASSIST articulation capture to its own JSONL file."
    )
    parser.add_argument(
        "--input-dir",
        default=DEFAULT_INPUT_DIR,
        type=Path,
        help="Directory containing raw ASSIST JSON captures.",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        type=Path,
        help="Directory where per-school normalized JSONL files will be written.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    file_counts = main(args.input_dir, args.output_dir)
    total = sum(file_counts.values())
    print(f"Wrote {total} normalized articulation records across {len(file_counts)} files")
    print(f"Output directory: {args.output_dir}")
