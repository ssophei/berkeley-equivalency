import json

from normalize_jsonl_files import main, normalized_output_path, write_normalized_file


RAW_FILE = (
    "data/articulations/"
    "year_76_sending_002_evergreen-valley-college_to_079_uc-berkeley.json"
)


def test_normalized_output_path_uses_raw_filename_stem(tmp_path):
    output = normalized_output_path(
        tmp_path / "year_76_sending_002_evergreen-valley-college_to_079_uc-berkeley.json",
        tmp_path / "normalized",
    )

    assert output == (
        tmp_path
        / "normalized"
        / "year_76_sending_002_evergreen-valley-college_to_079_uc-berkeley.jsonl"
    )


def test_write_normalized_file_creates_named_jsonl(tmp_path):
    count = write_normalized_file(RAW_FILE, tmp_path)

    output = (
        tmp_path
        / "year_76_sending_002_evergreen-valley-college_to_079_uc-berkeley.jsonl"
    )
    lines = output.read_text(encoding="utf-8").splitlines()
    first_record = json.loads(lines[0])

    assert count == len(lines)
    assert count > 0
    assert first_record["source_file"] == (
        "year_76_sending_002_evergreen-valley-college_to_079_uc-berkeley.json"
    )
    assert first_record["source_key"]["sending_institution_id"] == 2


def test_main_writes_one_jsonl_per_raw_capture(tmp_path):
    counts = main("data/articulations", tmp_path)

    assert counts
    assert all(count > 0 for count in counts.values())
    assert len(list(tmp_path.glob("*.jsonl"))) == len(counts)
