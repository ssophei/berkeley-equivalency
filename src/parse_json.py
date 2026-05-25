import argparse
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_INPUT_DIR = Path("data/articulations")
DEFAULT_OUTPUT_PATH = Path("data/normalized/berkeley_articulations.jsonl")


def compact_list(values: Any) -> list[Any]:
    if not isinstance(values, list):
        return []
    return [value for value in values if value not in (None, [], {})]


def institution_name(institution: dict[str, Any]) -> str | None:
    names = institution.get("names")
    if isinstance(names, list) and names:
        first_name = names[0]
        if isinstance(first_name, dict):
            return first_name.get("name")
    return institution.get("name")


def natural_sort_key(path: Path) -> list[int | str]:
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", path.name)
    ]


def clean_text(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip()
    return value


def course_key(prefix: Any, course_number: Any) -> str | None:
    if prefix is None or course_number is None:
        return None
    return f"{prefix} {course_number}".strip()


def normalize_cross_listed(raw_courses: Any) -> list[dict[str, Any]]:
    courses = compact_list(raw_courses)
    normalized = []
    for course in courses:
        if not isinstance(course, dict):
            continue
        normalized_course = {
            "id": course.get("courseIdentifierParentId"),
            "prefix": clean_text(course.get("prefix")),
            "course_number": clean_text(course.get("courseNumber")),
            "title": clean_text(course.get("courseTitle")),
        }
        normalized.append(
            {key: value for key, value in normalized_course.items() if value is not None}
        )
    return normalized


def normalize_course(
    raw_course: dict[str, Any], extras: dict[str, Any] | None = None
) -> dict[str, Any]:
    data = raw_course | (extras or {})
    normalized = {
        "type": "Course",
        "id": data.get("courseIdentifierParentId"),
        "course_instance_id": data.get("id"),
        "prefix": clean_text(data.get("prefix")),
        "course_number": clean_text(data.get("courseNumber")),
        "course_key": course_key(data.get("prefix"), data.get("courseNumber")),
        "title": clean_text(data.get("courseTitle")),
        "department": clean_text(data.get("department")),
        "min_units": data.get("minUnits"),
        "max_units": data.get("maxUnits"),
        "cross_listed_courses": normalize_cross_listed(
            data.get("visibleCrossListedCourses")
        ),
        "attributes": compact_list(data.get("attributes"))
        or compact_list(data.get("courseAttributes")),
        "requisites": compact_list(data.get("requisites")),
    }
    return {
        key: value
        for key, value in normalized.items()
        if value not in (None, [], {})
    }


def normalize_series(raw_series: dict[str, Any]) -> dict[str, Any]:
    series = raw_series.get("series", {})
    courses = [
        normalize_course(course)
        for course in compact_list(series.get("courses"))
        if isinstance(course, dict)
    ]
    normalized = {
        "type": "Series",
        "name": series.get("name"),
        "conjunction": series.get("conjunction"),
        "courses": courses,
        "attributes": compact_list(raw_series.get("seriesAttributes"))
        or compact_list(raw_series.get("courseAttributes")),
    }
    return {
        key: value
        for key, value in normalized.items()
        if value not in (None, [], {})
    }


def normalize_articulation_item(item: dict[str, Any]) -> dict[str, Any]:
    item_type = item.get("type")

    if item_type == "Course":
        return normalize_course(item)

    if item_type == "CourseGroup":
        normalized = {
            "type": "CourseGroup",
            "course_conjunction": item.get("courseConjunction"),
            "items": [
                normalize_articulation_item(child)
                for child in compact_list(item.get("items"))
                if isinstance(child, dict)
            ],
            "attributes": compact_list(item.get("attributes")),
        }
        return {
            key: value
            for key, value in normalized.items()
            if value not in (None, [], {})
        }

    if item_type in {"NotArticulated", "MustBeTakenAtReceivingUniversity"}:
        return {"type": item_type}

    return {
        "type": item_type or "Unknown",
        "raw_type": item_type,
    }


def normalize_sending_articulation(
    sending_articulation: dict[str, Any] | None,
) -> dict[str, Any]:
    if not sending_articulation:
        return {"type": "NotArticulated", "reason": "missing_sending_articulation"}

    reason = sending_articulation.get("noArticulationReason")
    items = [
        normalize_articulation_item(item)
        for item in compact_list(sending_articulation.get("items"))
        if isinstance(item, dict)
    ]

    if not items:
        normalized = {
            "type": "NotArticulated",
            "reason": reason or "no_sending_articulation_items",
            "attributes": compact_list(sending_articulation.get("attributes")),
        }
        return {
            key: value
            for key, value in normalized.items()
            if value not in (None, [], {})
        }

    normalized = {
        "type": "SendingArticulation",
        "items": items,
        "group_conjunctions": [
            {
                "conjunction": conjunction.get("groupConjunction"),
                "begin_position": conjunction.get("sendingCourseGroupBeginPosition"),
                "end_position": conjunction.get("sendingCourseGroupEndPosition"),
            }
            for conjunction in compact_list(
                sending_articulation.get("courseGroupConjunctions")
            )
            if isinstance(conjunction, dict)
        ],
        "attributes": compact_list(sending_articulation.get("attributes")),
    }
    return {
        key: value
        for key, value in normalized.items()
        if value not in (None, [], {})
    }


def normalize_receiving_node(raw_articulation: dict[str, Any]) -> dict[str, Any]:
    articulation_type = raw_articulation.get("type")

    if articulation_type == "Course":
        return normalize_course(
            raw_articulation.get("course", {}),
            {
                "visibleCrossListedCourses": raw_articulation.get(
                    "visibleCrossListedCourses"
                ),
                "courseAttributes": raw_articulation.get("courseAttributes"),
                "attributes": raw_articulation.get("receivingAttributes")
                or raw_articulation.get("attributes"),
            },
        )

    if articulation_type == "Series":
        return normalize_series(raw_articulation)

    return {"type": articulation_type or "Unknown"}


def normalize_receiving_articulation(
    raw_articulation: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    receiving = normalize_receiving_node(raw_articulation)
    sending = normalize_sending_articulation(
        raw_articulation.get("sendingArticulation")
    )

    return {
        "academic_year": context["academic_year"],
        "receiving_institution": context["receiving_institution"],
        "sending_institution": context["sending_institution"],
        "source_file": context["source_file"],
        "source_key": context["source_key"],
        "group_name": context["group_name"],
        "receiving": receiving,
        "sending": sending,
    }


def parse_file(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    with path.open(encoding="utf-8") as file:
        payload = json.load(file)

    result = payload.get("result") or {}
    academic_year = result.get("academicYear") or {}
    receiving_institution = result.get("receivingInstitution") or {}
    sending_institution = result.get("sendingInstitution") or {}

    base_context = {
        "academic_year": {
            "id": academic_year.get("id"),
            "code": academic_year.get("code"),
        },
        "receiving_institution": {
            "id": receiving_institution.get("id"),
            "name": institution_name(receiving_institution),
        },
        "sending_institution": {
            "id": sending_institution.get("id"),
            "name": institution_name(sending_institution),
        },
        "source_file": path.name,
    }
    base_context["source_key"] = {
        "academic_year_id": base_context["academic_year"]["id"],
        "sending_institution_id": base_context["sending_institution"]["id"],
        "receiving_institution_id": base_context["receiving_institution"]["id"],
    }

    records = []
    for group in compact_list(result.get("articulations")):
        if not isinstance(group, dict):
            continue
        context = base_context | {"group_name": group.get("name")}
        for articulation in compact_list(group.get("articulations")):
            if isinstance(articulation, dict):
                records.append(normalize_receiving_articulation(articulation, context))

    return records


def iter_input_files(input_dir: Path) -> list[Path]:
    return sorted(
        [path for path in input_dir.iterdir() if path.is_file()],
        key=natural_sort_key,
    )


def main(
    input_dir: str | Path = DEFAULT_INPUT_DIR,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> int:
    input_path = Path(input_dir)
    output = Path(output_path)

    files = iter_input_files(input_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with output.open("w", encoding="utf-8") as file:
        for path in files:
            for record in parse_file(path):
                file.write(json.dumps(record, separators=(",", ":"), sort_keys=True))
                file.write("\n")
                count += 1

    return count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize raw ASSIST articulation JSON captures to JSONL."
    )
    parser.add_argument(
        "--input-dir",
        default=DEFAULT_INPUT_DIR,
        type=Path,
        help="Directory containing raw ASSIST JSON captures.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_PATH,
        type=Path,
        help="Path to write normalized JSONL records.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    total = main(args.input_dir, args.output)
    print(f"Wrote {total} normalized articulation records to {args.output}")
