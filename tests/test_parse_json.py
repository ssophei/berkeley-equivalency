import json

from parse_json import main, normalize_sending_articulation, parse_file


def find_record(records, receiving_type=None, course_key=None):
    for record in records:
        receiving = record["receiving"]
        if receiving_type and receiving.get("type") != receiving_type:
            continue
        if course_key and receiving.get("course_key") != course_key:
            continue
        return record
    raise AssertionError("Expected normalized record was not found")


def test_parse_file_normalizes_course_articulation():
    records = parse_file(
        "data/articulations/"
        "year_76_sending_002_evergreen-valley-college_to_079_uc-berkeley.json"
    )

    record = find_record(records, receiving_type="Course", course_key="ANTHRO 1")

    assert record["academic_year"] == {"id": 76, "code": "2025-2026"}
    assert record["source_key"] == {
        "academic_year_id": 76,
        "sending_institution_id": 2,
        "receiving_institution_id": 79,
    }
    assert record["receiving_institution"]["name"] == "University of California, Berkeley"
    assert record["sending_institution"]["name"] == "Evergreen Valley College"
    assert record["group_name"] == "ANTH Anthropology"
    assert record["receiving"]["title"] == "Introduction to Biological Anthropology"
    assert record["sending"]["type"] == "SendingArticulation"
    assert record["sending"]["items"][0]["type"] == "CourseGroup"
    assert record["sending"]["items"][0]["course_conjunction"] == "And"
    assert record["sending"]["items"][0]["items"][0]["course_key"] == "ANTH 062"


def test_parse_file_normalizes_receiving_series():
    records = parse_file(
        "data/articulations/"
        "year_76_sending_002_evergreen-valley-college_to_079_uc-berkeley.json"
    )

    record = find_record(records, receiving_type="Series")

    assert record["receiving"]["conjunction"] == "And"
    assert record["receiving"]["courses"][0]["course_key"] == "BIOLOGY 1A"
    assert record["receiving"]["courses"][1]["course_key"] == "BIOLOGY 1AL"
    assert record["sending"]["items"][0]["items"][0]["course_key"] == "BIOL 004A"


def test_parse_file_preserves_or_group_conjunctions():
    records = parse_file(
        "data/articulations/"
        "year_76_sending_002_evergreen-valley-college_to_079_uc-berkeley.json"
    )

    record = find_record(records, receiving_type="Course", course_key="STAT 2")

    assert record["sending"]["items"][0]["course_conjunction"] == "And"
    assert record["sending"]["items"][1]["course_conjunction"] == "And"
    assert record["sending"]["group_conjunctions"] == [
        {"conjunction": "Or", "begin_position": 0, "end_position": 1}
    ]


def test_empty_sending_articulation_becomes_explicit_no_articulation():
    normalized = normalize_sending_articulation(
        {
            "noArticulationReason": "No Course Articulated",
            "items": [],
            "attributes": [],
        }
    )

    assert normalized == {
        "type": "NotArticulated",
        "reason": "No Course Articulated",
    }


def test_main_writes_valid_jsonl_for_existing_raw_files(tmp_path):
    output = tmp_path / "berkeley_articulations.jsonl"

    count = main("data/articulations", output)

    lines = output.read_text(encoding="utf-8").splitlines()
    assert count == len(lines)
    assert count > 0

    first_record = json.loads(lines[0])
    assert first_record["receiving_institution"]["id"] == 79
    assert first_record["sending_institution"]["id"] is not None
    assert first_record["source_key"] == {
        "academic_year_id": first_record["academic_year"]["id"],
        "sending_institution_id": first_record["sending_institution"]["id"],
        "receiving_institution_id": first_record["receiving_institution"]["id"],
    }
    assert first_record["receiving"]["type"] in {"Course", "Series"}
