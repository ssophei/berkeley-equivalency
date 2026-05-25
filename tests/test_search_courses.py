from search_courses import EXACT_SEARCH_SQL, FUZZY_SEARCH_SQL, grouped_results


def test_exact_search_sql_targets_receiving_course_key():
    assert "rr.receiving_institution_id = %(receiving_institution_id)s" in EXACT_SEARCH_SQL
    assert "rr.display_key = %(query)s" in EXACT_SEARCH_SQL


def test_fuzzy_search_sql_targets_course_key_and_title():
    assert "rr.display_key ILIKE %(pattern)s" in FUZZY_SEARCH_SQL
    assert "rr.title ILIKE %(pattern)s" in FUZZY_SEARCH_SQL
    assert "LIMIT %(limit)s" in FUZZY_SEARCH_SQL


def test_grouped_results_groups_by_sending_institution():
    rows = [
        {
            "academic_year_id": 76,
            "academic_year_code": "2025-2026",
            "group_name": "COMSC Computer Science",
            "source_file": "one.json",
            "sending_institution_id": 2,
            "sending_institution_name": "Evergreen Valley College",
            "receiving_requirement_id": "course:76:79:1",
            "berkeley_course": "COMPSCI 61A",
            "berkeley_title": "Structure and Interpretation of Computer Programs",
            "receiving_json": {"course_key": "COMPSCI 61A"},
            "sending_json": {"items": []},
        },
        {
            "academic_year_id": 76,
            "academic_year_code": "2025-2026",
            "group_name": "COMSC Computer Science",
            "source_file": "two.json",
            "sending_institution_id": 3,
            "sending_institution_name": "Los Angeles City College",
            "receiving_requirement_id": "course:76:79:1",
            "berkeley_course": "COMPSCI 61A",
            "berkeley_title": "Structure and Interpretation of Computer Programs",
            "receiving_json": {"course_key": "COMPSCI 61A"},
            "sending_json": {"items": []},
        },
    ]

    grouped = grouped_results(rows)

    assert [entry["sending_institution"]["name"] for entry in grouped] == [
        "Evergreen Valley College",
        "Los Angeles City College",
    ]
    assert grouped[0]["articulations"][0]["berkeley_course"] == "COMPSCI 61A"
