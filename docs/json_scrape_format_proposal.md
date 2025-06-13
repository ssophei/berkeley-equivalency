# Final Proposal: API-Aligned Data Storage Format

## Overview

This proposal defines a JSON data structure for storing scraped course articulation data. The format is designed to closely mirror the ASSIST API, making future migration straightforward, while only requiring fields that are feasible to scrape.

## Top-Level Structure

Each file contains a list of agreement objects. Each agreement object represents a single articulation agreement page (typically for a major, year, and school pair).

```json
{
  "name": "Economics",
  "type": "Articulation Agreement", // or "General Education" (see below)
  "receivingInstitution": "UC Berkeley",
  "sendingInstitution": "De Anza College",
  "academicYear": "2024–2025",
  "articulations": [ /* see below */ ]
}
```

### Field Definitions

* `name`: The name of the major or agreement (e.g., "Economics").
* `type`:
  * `"Articulation Agreement"`: Scraped from a major or department articulation agreement page.
  * `"General Education"`: Scraped from the General Education section of the agreement.
  * **Note**: The HTML structure for General Education agreements may differ and will require additional parsing logic. Implementing General Education scraping should be considered a future enhancement.
* `receivingInstitution`: The university or four-year institution (e.g., "UC Berkeley").
* `sendingInstitution`: The community college or source institution (e.g., "De Anza College").
* `academicYear`: The agreement year or range (e.g., "2024–2025").
* `articulations`: List of course articulation mappings (see below).

## Articulation Structure

Each articulation maps a set of sending courses (community college) to a set of receiving courses (university).

```json
{
  "receiving": { /* course node or group node */ },
  "sending": { /* course node or group node or NotArticulated node */ }
}
```

## Course Node Structure

```json
{
  "type": "Course",
  "prefix": "ECON",
  "courseNumber": "1",
  "courseTitle": "Principles of Macroeconomics",
  "minUnits": 4.0,
  "visibleCrossListedCourses": [
    { "prefix": "BUS", "courseNumber": "10" }
  ]
}
```

* `type`: `"Course"`, `"CourseGroup"`, `NotArticulated` and `"MustBeTakenAtReceivingUniversity` see below for more details
* `prefix`: Subject code.
* `courseNumber`: Course number.
* `courseTitle`: Course title.
* `minUnits`: Number of units/credits.
* `visibleCrossListedCourses`: (optional) List of equivalent courses at the same school.

## Group Node Structure (AND/OR logic)

```json
{
  "type": "CourseGroup",
  "courseConjunction": "And", // or "Or"
  "items": [
    { /* course node or group node */ },
    { /* course node or group node */ }
  ],
  "attributes": [
    "Regular and honors courses may be combined to complete this series"
  ]
}
```

* `type`: Always `"CourseGroup"` for group nodes.
* `courseConjunction`: `"And"` or `"Or"`.
* `items`: Array of child nodes (course or group).
* `attributes`: (optional) Array of notes, prerequisites, etc.

## NotArticulated Node Structure

When there is no articulated course at the sending institution for a given receiving course or requirement, this node is used.

```json
{
  "type": "NotArticulated"
}
```

## MustBeTakenAtReceivingUniversity

This is for when a course must be taken at the receiving univeristy

```json
{
  "type": "MustBeTakenAtReceivingUniversity"
}
```

## Full Example

```json
[
  {
    "name": "Economics",
    "type": "Articulation Agreement",
    "receivingInstitution": "UC Berkeley",
    "sendingInstitution": "De Anza College",
    "academicYear": "2024–2025",
    "articulations": [
      {
        "receiving": {
          "type": "Course",
          "prefix": "ECON",
          "courseNumber": "1",
          "courseTitle": "Introduction to Economics",
          "minUnits": 4.0
        },
        "sending": {
          "type": "CourseGroup",
          "courseConjunction": "Or",
          "items": [
            {
              "type": "CourseGroup",
              "courseConjunction": "And",
              "items": [
                {
                  "type": "Course",
                  "prefix": "ECON",
                  "courseNumber": "1",
                  "courseTitle": "Principles of Macroeconomics",
                  "minUnits": 4.0,
                  "visibleCrossListedCourses": [
                    { "prefix": "BUS", "courseNumber": "10" }
                  ]
                },
                {
                  "type": "Course",
                  "prefix": "ECON",
                  "courseNumber": "2",
                  "courseTitle": "Principles of Microeconomics",
                  "minUnits": 4.0
                }
              ],
              "attributes": [
                "Regular and honors courses may be combined to complete this series"
              ]
            },
            {
              "type": "Course",
              "prefix": "ECON",
              "courseNumber": "1H",
              "courseTitle": "Principles of Macroeconomics - HONORS",
              "minUnits": 4.0
            }
          ]
        }
      },
      {
        "receiving": {
          "type": "CourseGroup",
          "courseConjunction": "Or",
          "items": [
            {
              "type": "Course",
              "prefix": "MATH",
              "courseNumber": "1A",
              "courseTitle": "Calculus I",
              "minUnits": 5.0
            },
            {
              "type": "Course",
              "prefix": "MATH",
              "courseNumber": "1AH",
              "courseTitle": "Calculus I - HONORS",
              "minUnits": 5.0
            }
          ]
        },
        "sending": {
          "type": "Course",
          "prefix": "MATH",
          "courseNumber": "16A",
          "courseTitle": "Analytic Geometry and Calculus",
          "minUnits": 3.0
        }
      },
      {
        "receiving": {
          "type": "Course",
          "prefix": "POLI",
          "courseNumber": "30",
          "courseTitle": "Political Inquiry",
          "minUnits": 4.0,
          "attributes": [
            "This course must be taken at the university after transfer"
          ]
        },
        "sending": {
          "type": "NotArticulated"
        }
      }
    ]
  }
]
```

## Why This Format?

* **API Alignment**: Field names and structure closely match the ASSIST API for easy migration and future integration.
* **Minimal Scrape Load**: No extra fields are required beyond what we currently scrape, minimizing the development workload.
* **Rich Metadata**: Attributes and group logic are preserved for extensibility and to capture important notes, prerequisites, and complex articulation rules.
* **Explicit "No Articulation"**: The `NotArticulated` type clearly identifies cases where a course or requirement has no direct equivalent at the sending institution.
* **Simplified Node Structure**: Removal of the `school` field from `Course` and `NotArticulated` nodes simplifies the structure and correctly identifies the institution via the parent `receivingInstitution` or `sendingInstitution` fields.
* **Future-Proofing**: General Education support is planned but not required for initial implementation, allowing for phased development.
