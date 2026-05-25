import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


DEFAULT_NORMALIZED_DIR = Path("data/normalized/articulations")
DEFAULT_SCHEMA_PATH = Path("db/schema.sql")


@dataclass(frozen=True)
class ImportRows:
    institutions: list[dict[str, Any]]
    academic_year: dict[str, Any]
    receiving_course: dict[str, Any]
    articulation: dict[str, Any]


def iter_jsonl_records(input_dir: str | Path) -> Iterable[dict[str, Any]]:
    for path in sorted(Path(input_dir).glob("*.jsonl")):
        with path.open(encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(f"Invalid JSON in {path}:{line_number}") from error


def course_id_from_receiving(receiving: dict[str, Any]) -> int:
    if receiving.get("type") == "Course" and receiving.get("id") is not None:
        return int(receiving["id"])

    if receiving.get("type") == "Series":
        courses = receiving.get("courses") or []
        course_ids = [str(course.get("id")) for course in courses if course.get("id")]
        if course_ids:
            return -int("".join(course_ids))

    raise ValueError(f"Cannot derive receiving course id from {receiving}")


def searchable_course_from_receiving(receiving: dict[str, Any]) -> dict[str, Any]:
    if receiving.get("type") == "Course":
        return {
            "id": course_id_from_receiving(receiving),
            "prefix": receiving.get("prefix"),
            "course_number": str(receiving.get("course_number"))
            if receiving.get("course_number") is not None
            else None,
            "course_key": receiving.get("course_key"),
            "title": receiving.get("title"),
            "department": receiving.get("department"),
            "min_units": receiving.get("min_units"),
            "max_units": receiving.get("max_units"),
        }

    if receiving.get("type") == "Series":
        courses = receiving.get("courses") or []
        course_keys = [course.get("course_key") for course in courses if course.get("course_key")]
        titles = [course.get("title") for course in courses if course.get("title")]
        return {
            "id": course_id_from_receiving(receiving),
            "prefix": None,
            "course_number": None,
            "course_key": receiving.get("name") or ", ".join(course_keys),
            "title": receiving.get("name") or ", ".join(titles),
            "department": courses[0].get("department") if courses else None,
            "min_units": sum(
                course.get("min_units") or 0 for course in courses
            )
            or None,
            "max_units": sum(
                course.get("max_units") or 0 for course in courses
            )
            or None,
        }

    raise ValueError(f"Unsupported receiving type: {receiving.get('type')}")


def record_to_import_rows(record: dict[str, Any]) -> ImportRows:
    receiving_institution = record["receiving_institution"]
    sending_institution = record["sending_institution"]
    academic_year = record["academic_year"]
    receiving_course = searchable_course_from_receiving(record["receiving"])
    receiving_course["institution_id"] = receiving_institution["id"]

    articulation = {
        "academic_year_id": academic_year["id"],
        "receiving_institution_id": receiving_institution["id"],
        "sending_institution_id": sending_institution["id"],
        "receiving_course_id": receiving_course["id"],
        "group_name": record.get("group_name"),
        "source_file": record["source_file"],
        "receiving_json": record["receiving"],
        "sending_json": record["sending"],
    }

    return ImportRows(
        institutions=[
            {
                "id": receiving_institution["id"],
                "name": receiving_institution["name"],
                "is_community_college": False,
            },
            {
                "id": sending_institution["id"],
                "name": sending_institution["name"],
                "is_community_college": True,
            },
        ],
        academic_year=academic_year,
        receiving_course=receiving_course,
        articulation=articulation,
    )


def apply_schema(conn, schema_path: str | Path = DEFAULT_SCHEMA_PATH) -> None:
    conn.execute(Path(schema_path).read_text(encoding="utf-8"))


def import_record(conn, record: dict[str, Any]) -> None:
    rows = record_to_import_rows(record)

    for institution in rows.institutions:
        conn.execute(
            """
            INSERT INTO institutions (id, name, is_community_college)
            VALUES (%(id)s, %(name)s, %(is_community_college)s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                is_community_college = EXCLUDED.is_community_college
            """,
            institution,
        )

    conn.execute(
        """
        INSERT INTO academic_years (id, code)
        VALUES (%(id)s, %(code)s)
        ON CONFLICT (id) DO UPDATE SET code = EXCLUDED.code
        """,
        rows.academic_year,
    )

    conn.execute(
        """
        INSERT INTO courses (
            id,
            institution_id,
            prefix,
            course_number,
            course_key,
            title,
            department,
            min_units,
            max_units
        )
        VALUES (
            %(id)s,
            %(institution_id)s,
            %(prefix)s,
            %(course_number)s,
            %(course_key)s,
            %(title)s,
            %(department)s,
            %(min_units)s,
            %(max_units)s
        )
        ON CONFLICT (id) DO UPDATE SET
            institution_id = EXCLUDED.institution_id,
            prefix = EXCLUDED.prefix,
            course_number = EXCLUDED.course_number,
            course_key = EXCLUDED.course_key,
            title = EXCLUDED.title,
            department = EXCLUDED.department,
            min_units = EXCLUDED.min_units,
            max_units = EXCLUDED.max_units
        """,
        rows.receiving_course,
    )

    conn.execute(
        """
        INSERT INTO articulations (
            academic_year_id,
            receiving_institution_id,
            sending_institution_id,
            receiving_course_id,
            group_name,
            source_file,
            receiving_json,
            sending_json
        )
        VALUES (
            %(academic_year_id)s,
            %(receiving_institution_id)s,
            %(sending_institution_id)s,
            %(receiving_course_id)s,
            %(group_name)s,
            %(source_file)s,
            %(receiving_json)s::jsonb,
            %(sending_json)s::jsonb
        )
        ON CONFLICT (
            academic_year_id,
            receiving_institution_id,
            sending_institution_id,
            receiving_course_id,
            group_name,
            source_file
        ) DO UPDATE SET
            receiving_json = EXCLUDED.receiving_json,
            sending_json = EXCLUDED.sending_json
        """,
        {
            **rows.articulation,
            "receiving_json": json.dumps(rows.articulation["receiving_json"]),
            "sending_json": json.dumps(rows.articulation["sending_json"]),
        },
    )


def import_normalized_dir(
    database_url: str,
    input_dir: str | Path = DEFAULT_NORMALIZED_DIR,
    schema_path: str | Path = DEFAULT_SCHEMA_PATH,
    apply_schema_first: bool = True,
) -> int:
    try:
        import psycopg
    except ImportError as error:
        raise RuntimeError(
            "psycopg is required for database import. Run `uv sync` first."
        ) from error

    count = 0
    with psycopg.connect(database_url) as conn:
        if apply_schema_first:
            apply_schema(conn, schema_path)
        for record in iter_jsonl_records(input_dir):
            import_record(conn, record)
            count += 1
        conn.commit()
    return count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import normalized articulation JSONL files into PostgreSQL."
    )
    parser.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL"),
        help="PostgreSQL connection URL. Defaults to DATABASE_URL.",
    )
    parser.add_argument(
        "--input-dir",
        default=DEFAULT_NORMALIZED_DIR,
        type=Path,
        help="Directory containing normalized JSONL files.",
    )
    parser.add_argument(
        "--schema",
        default=DEFAULT_SCHEMA_PATH,
        type=Path,
        help="SQL schema file to apply before import.",
    )
    parser.add_argument(
        "--skip-schema",
        action="store_true",
        help="Do not apply schema.sql before importing records.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if not args.database_url:
        raise SystemExit("Provide --database-url or set DATABASE_URL")
    imported = import_normalized_dir(
        args.database_url,
        args.input_dir,
        args.schema,
        not args.skip_schema,
    )
    print(f"Imported {imported} normalized articulation records")
