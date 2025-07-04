import json
import pytest
import asyncio

from json_grabber import unwrap_nested_json, intercept

# ---------------------------------------------------------------------------
# Unit tests for unwrap_nested_json
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "input_data,expected",
    [
        # Simple nested JSON in string
        ("{\"a\": 1}", {"a": 1}),
        # One level of nesting in a dictionary
        ({"key": "{\"inner\": 2}"}, {"key": {"inner": 2}}),
        # Nested JSON inside a list
        (["{\"a\": 1}", "{\"b\": {\"c\": 3}}"], [{"a": 1}, {"b": {"c": 3}}]),
        # Deeply-nested JSON strings
        (
            {"outer": "{\"mid\": \"{\\\"inner\\\": 5}\"}"},
            {"outer": {"mid": {"inner": 5}}},
        ),
    ],
)
def test_unwrap_nested_json(input_data, expected):
    """Ensure nested JSON strings are recursively parsed."""
    assert unwrap_nested_json(input_data) == expected


# ---------------------------------------------------------------------------
# Live integration tests against ASSIST.org using json_grabber.intercept
# ---------------------------------------------------------------------------

# A couple of representative URLs copied from the original assist_urls.txt
# Do NOT remove the encoding in `viewByKey` – it is part of the contract we are
# validating.
SAMPLE_URLS = [
    "https://assist.org/transfer/results?year=75&institution=2&agreement=1&agreementType=to&viewAgreementsOptions=true&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=75%2F2%2Fto%2F1%2FAllMajors",
    "https://assist.org/transfer/results?year=75&institution=124&agreement=79&agreementType=to&viewAgreementsOptions=true&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=75%2F124%2Fto%2F79%2FAllMajors",
]


@pytest.mark.asyncio
@pytest.mark.parametrize("url", SAMPLE_URLS)
async def test_intercept_schema(url):
    """Fetch data via intercept and assert minimal expected schema."""

    parsed = await intercept(url)

    # Top-level keys
    assert {"result", "validationFailure", "isSuccessful"}.issubset(parsed)

    result = parsed["result"]
    # Ensure critical sub-objects exist
    for key in [
        "sendingInstitution",
        "receivingInstitution",
        "academicYear",
        "templateAssets",
        "articulations",
    ]:
        assert key in result, f"Missing key: {key}"

    # Basic sanity on nested IDs
    assert isinstance(result["sendingInstitution"]["id"], int)
    assert isinstance(result["receivingInstitution"]["id"], int)

    # At least one articulation with a templateCellId
    articulations = result.get("articulations", [])
    assert articulations, "Expected at least one articulation entry"
    assert any(
        isinstance(entry.get("templateCellId"), str) and entry["templateCellId"]
        for entry in articulations
    ) 