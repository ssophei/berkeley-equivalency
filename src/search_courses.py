import argparse
import json
import os
from collections import defaultdict
from typing import Any


BERKELEY_ID = 79


EXACT_SEARCH_SQL = """
SELECT
    a.academic_year_id,
    ay.code AS academic_year_code,
    a.group_name,
    a.source_file,
    sending.id AS sending_institution_id,
    sending.name AS sending_institution_name,
    c.id AS receiving_course_id,
    c.course_key AS berkeley_course,
    c.title AS berkeley_title,
    a.receiving_json,
    a.sending_json
FROM articulations a
JOIN academic_years ay ON ay.id = a.academic_year_id
JOIN courses c ON c.id = a.receiving_course_id
JOIN institutions sending ON sending.id = a.sending_institution_id
WHERE c.institution_id = %(receiving_institution_id)s
  AND c.course_key = %(query)s
ORDER BY sending.name, c.course_key
"""


FUZZY_SEARCH_SQL = """
SELECT
    a.academic_year_id,
    ay.code AS academic_year_code,
    a.group_name,
    a.source_file,
    sending.id AS sending_institution_id,
    sending.name AS sending_institution_name,
    c.id AS receiving_course_id,
    c.course_key AS berkeley_course,
    c.title AS berkeley_title,
    a.receiving_json,
    a.sending_json
FROM articulations a
JOIN academic_years ay ON ay.id = a.academic_year_id
JOIN courses c ON c.id = a.receiving_course_id
JOIN institutions sending ON sending.id = a.sending_institution_id
WHERE c.institution_id = %(receiving_institution_id)s
  AND (
    c.course_key ILIKE %(pattern)s
    OR c.title ILIKE %(pattern)s
  )
ORDER BY c.course_key, sending.name
LIMIT %(limit)s
"""


def grouped_results(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = defaultdict(list)
    institutions = {}

    for row in rows:
        sending_id = row["sending_institution_id"]
        institutions[sending_id] = {
            "id": sending_id,
            "name": row["sending_institution_name"],
        }
        grouped[sending_id].append(
            {
                "academic_year": {
                    "id": row["academic_year_id"],
                    "code": row["academic_year_code"],
                },
                "group_name": row["group_name"],
                "source_file": row["source_file"],
                "berkeley_course": row["berkeley_course"],
                "berkeley_title": row["berkeley_title"],
                "receiving": row["receiving_json"],
                "sending": row["sending_json"],
            }
        )

    return [
        {
            "sending_institution": institutions[sending_id],
            "articulations": articulations,
        }
        for sending_id, articulations in sorted(
            grouped.items(),
            key=lambda item: institutions[item[0]]["name"],
        )
    ]


def search_courses(
    database_url: str,
    query: str,
    receiving_institution_id: int = BERKELEY_ID,
    fuzzy: bool = False,
    limit: int = 100,
) -> list[dict[str, Any]]:
    try:
        import psycopg
        from psycopg.rows import dict_row
    except ImportError as error:
        raise RuntimeError("psycopg is required for search. Run `uv sync` first.") from error

    sql = FUZZY_SEARCH_SQL if fuzzy else EXACT_SEARCH_SQL
    params = {
        "query": query,
        "pattern": f"%{query}%",
        "receiving_institution_id": receiving_institution_id,
        "limit": limit,
    }

    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        rows = conn.execute(sql, params).fetchall()

    return grouped_results(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search Berkeley course articulations in PostgreSQL."
    )
    parser.add_argument("query", help="Course key or search text, e.g. COMPSCI 61A")
    parser.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL"),
        help="PostgreSQL connection URL. Defaults to DATABASE_URL.",
    )
    parser.add_argument(
        "--receiving-institution-id",
        default=BERKELEY_ID,
        type=int,
        help="Receiving institution id to search. Defaults to UC Berkeley.",
    )
    parser.add_argument(
        "--fuzzy",
        action="store_true",
        help="Search course keys and titles with ILIKE instead of exact course key.",
    )
    parser.add_argument(
        "--limit",
        default=100,
        type=int,
        help="Maximum rows for fuzzy search.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if not args.database_url:
        raise SystemExit("Provide --database-url or set DATABASE_URL")
    results = search_courses(
        args.database_url,
        args.query,
        args.receiving_institution_id,
        args.fuzzy,
        args.limit,
    )
    print(json.dumps(results, indent=2, default=str))
