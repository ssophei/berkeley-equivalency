import json
import pytest

from json_grabber import unwrap_nested_json

# ---------------------------------------------------------------------------
# Unit tests for unwrap_nested_json
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "input_data,expected",
    [
        # Primitive passthrough
        (42, 42),
        ("plain string", "plain string"),
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
# Tests validating that the assist_data.json fixture adheres to the expected
# schema returned by json_grabber.intercept. We do **not** contact the network –
# we simply load the checked-in sample file and run light structural checks.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def assist_data():
    with open("data/assist_data.json", "r") as fh:
        return json.load(fh)


def test_assist_data_top_level_keys(assist_data):
    required_top_keys = {"result", "validationFailure", "isSuccessful"}
    assert required_top_keys.issubset(assist_data.keys())


def test_assist_data_result_minimal_schema(assist_data):
    """Validate that important sub-objects are present in `result`."""
    result = assist_data["result"]
    expected_keys = {
        "sendingInstitution",
        "receivingInstitution",
        "academicYear",
        "templateAssets",
        "articulations",
    }
    assert expected_keys.issubset(result.keys())
    # Sanity check a couple of deeply-nested IDs to be integers
    assert isinstance(result["sendingInstitution"]["id"], int)
    assert isinstance(result["receivingInstitution"]["id"], int)


def test_assist_data_articulations_have_template_ids(assist_data):
    """Every articulation entry should reference a templateCellId string."""
    articulations = assist_data["result"].get("articulations", [])
    assert articulations, "Expected at least one articulation entry"
    for entry in articulations:
        assert "templateCellId" in entry and isinstance(entry["templateCellId"], str) 