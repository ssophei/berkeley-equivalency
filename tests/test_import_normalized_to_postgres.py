import json
from pathlib import Path

import pytest

from import_normalized_to_postgres import (
    iter_jsonl_records,
    record_to_import_rows,
    receiving_requirement_id,
    receiving_requirement_from_record,
)


def sample_record():
    return {
        "academic_year": {"id": 76, "code": "2025-2026"},
        "receiving_institution": {
            "id": 79,
            "name": "University of California, Berkeley",
        },
        "sending_institution": {"id": 2, "name": "Evergreen Valley College"},
        "source_file": "year_76_sending_002_evergreen-valley-college_to_079_uc-berkeley.json",
        "source_key": {
            "academic_year_id": 76,
            "sending_institution_id": 2,
            "receiving_institution_id": 79,
        },
        "group_name": "ANTH Anthropology",
        "receiving": {
            "type": "Course",
            "id": 351696,
            "prefix": "ANTHRO",
            "course_number": 1,
            "course_key": "ANTHRO 1",
            "title": "Introduction to Biological Anthropology",
            "department": "Anthropology",
            "min_units": 4.0,
            "max_units": 4.0,
        },
        "sending": {
            "type": "SendingArticulation",
            "items": [
                {
                    "type": "CourseGroup",
                    "course_conjunction": "And",
                    "items": [{"type": "Course", "course_key": "ANTH 062"}],
                }
            ],
        },
    }


def test_record_to_import_rows_for_course():
    rows = record_to_import_rows(sample_record())

    assert rows.institutions == [
        {
            "id": 79,
            "name": "University of California, Berkeley",
            "is_community_college": False,
        },
        {
            "id": 2,
            "name": "Evergreen Valley College",
            "is_community_college": True,
        },
    ]
    assert rows.academic_year == {"id": 76, "code": "2025-2026"}
    assert rows.courses == [
        {
            "id": 351696,
            "institution_id": 79,
            "prefix": "ANTHRO",
            "course_number": "1",
            "course_key": "ANTHRO 1",
            "title": "Introduction to Biological Anthropology",
            "department": "Anthropology",
            "min_units": 4.0,
            "max_units": 4.0,
        }
    ]
    assert rows.receiving_requirement["id"] == "course:76:79:351696"
    assert rows.receiving_requirement["display_key"] == "ANTHRO 1"
    assert rows.articulation["receiving_requirement_id"] == "course:76:79:351696"
    assert rows.articulation["sending_json"]["items"][0]["course_conjunction"] == "And"


def test_receiving_requirement_from_series_uses_ordered_course_instance_ids():
    record = sample_record()
    record["receiving"] = {
        "type": "Series",
        "name": "BIOLOGY 1A, BIOLOGY 1AL",
        "courses": [
            {
                "id": 275173,
                "course_instance_id": "85ca7424-24fd-4a01-8f80-08ddbf3f4497",
                "course_key": "BIOLOGY 1A",
                "min_units": 3.0,
            },
            {
                "id": 326365,
                "course_instance_id": "229e646d-c917-40a8-8f81-08ddbf3f4497",
                "course_key": "BIOLOGY 1AL",
                "min_units": 2.0,
            },
        ],
    }

    requirement = receiving_requirement_from_record(record)

    assert requirement["id"] == (
        "series:76:79:"
        "85ca7424-24fd-4a01-8f80-08ddbf3f4497|"
        "229e646d-c917-40a8-8f81-08ddbf3f4497"
    )
    assert requirement["display_key"] == "BIOLOGY 1A, BIOLOGY 1AL"


def test_receiving_requirement_id_rejects_missing_ids():
    record = sample_record()
    record["receiving"] = {"type": "Course", "course_key": "BAD 1"}

    with pytest.raises(ValueError):
        receiving_requirement_id(record)


def test_iter_jsonl_records_reads_all_records(tmp_path):
    path = tmp_path / "sample.jsonl"
    path.write_text(
        json.dumps({"a": 1}) + "\n\n" + json.dumps({"b": 2}) + "\n",
        encoding="utf-8",
    )

    assert list(iter_jsonl_records(tmp_path)) == [{"a": 1}, {"b": 2}]


def test_schema_contains_expected_tables_and_indexes():
    schema = Path("db/schema.sql").read_text(encoding="utf-8")

    assert "CREATE TABLE IF NOT EXISTS institutions" in schema
    assert "CREATE TABLE IF NOT EXISTS academic_years" in schema
    assert "CREATE TABLE courses" in schema
    assert "CREATE TABLE receiving_requirements" in schema
    assert "CREATE TABLE articulations" in schema
    assert "receiving_requirement_id TEXT NOT NULL" in schema
    assert "gin_trgm_ops" in schema
    assert "sending_json JSONB NOT NULL" in schema
