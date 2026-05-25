import json
from pathlib import Path

import pytest

from import_normalized_to_postgres import (
    course_id_from_receiving,
    iter_jsonl_records,
    record_to_import_rows,
    searchable_course_from_receiving,
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
    assert rows.receiving_course["id"] == 351696
    assert rows.receiving_course["course_key"] == "ANTHRO 1"
    assert rows.receiving_course["institution_id"] == 79
    assert rows.articulation["sending_json"]["items"][0]["course_conjunction"] == "And"


def test_searchable_course_from_series_uses_stable_negative_id():
    receiving = {
        "type": "Series",
        "name": "BIOLOGY 1A, BIOLOGY 1AL",
        "courses": [
            {"id": 275173, "course_key": "BIOLOGY 1A", "min_units": 3.0},
            {"id": 326365, "course_key": "BIOLOGY 1AL", "min_units": 2.0},
        ],
    }

    course = searchable_course_from_receiving(receiving)

    assert course["id"] == -275173326365
    assert course["course_key"] == "BIOLOGY 1A, BIOLOGY 1AL"
    assert course["min_units"] == 5.0


def test_course_id_from_receiving_rejects_missing_ids():
    with pytest.raises(ValueError):
        course_id_from_receiving({"type": "Course", "course_key": "BAD 1"})


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
    assert "CREATE TABLE IF NOT EXISTS courses" in schema
    assert "CREATE TABLE IF NOT EXISTS articulations" in schema
    assert "gin_trgm_ops" in schema
    assert "sending_json JSONB NOT NULL" in schema
