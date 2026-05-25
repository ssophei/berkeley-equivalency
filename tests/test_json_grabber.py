import json

import pytest

from json_grabber import (
    capture_failure,
    intercept,
    load_fetch_entries,
    output_path_for_entry,
    unwrap_nested_json,
    validate_capture,
)


@pytest.mark.parametrize(
    "input_data,expected",
    [
        ('{"a": 1}', {"a": 1}),
        ({"key": '{"inner": 2}'}, {"key": {"inner": 2}}),
        (
            ['{"a": 1}', '{"b": {"c": 3}}'],
            [{"a": 1}, {"b": {"c": 3}}],
        ),
        (
            {"outer": '{"mid": "{\\"inner\\": 5}"}'},
            {"outer": {"mid": {"inner": 5}}},
        ),
    ],
)
def test_unwrap_nested_json(input_data, expected):
    assert unwrap_nested_json(input_data) == expected


def test_unwrap_nested_json_rejects_scalar_top_level():
    with pytest.raises(TypeError):
        unwrap_nested_json('"scalar"')


def test_load_fetch_entries_accepts_manifest_entries(tmp_path):
    manifest = tmp_path / "url_manifest.json"
    manifest.write_text(
        json.dumps(
            [
                {
                    "url": "https://assist.org/example",
                    "output_file": "year_76_sending_002_example.json",
                    "sending_institution_id": 2,
                }
            ]
        ),
        encoding="utf-8",
    )

    assert load_fetch_entries(manifest) == [
        {
            "url": "https://assist.org/example",
            "output_file": "year_76_sending_002_example.json",
            "sending_institution_id": 2,
        }
    ]


def test_load_fetch_entries_still_accepts_legacy_url_lists(tmp_path):
    urls = tmp_path / "urls.json"
    urls.write_text(json.dumps(["https://assist.org/example"]), encoding="utf-8")

    assert load_fetch_entries(urls) == [
        {
            "url": "https://assist.org/example",
            "output_file": "assist_data_1.json",
        }
    ]


def test_output_path_for_entry_uses_manifest_filename(tmp_path):
    entry = {"output_file": "year_76_sending_002_example.json"}

    assert output_path_for_entry(entry, tmp_path) == (
        tmp_path / "year_76_sending_002_example.json"
    )


def test_validate_capture_rejects_mismatched_manifest_metadata():
    data = {
        "result": {
            "sendingInstitution": {"id": 3},
            "receivingInstitution": {"id": 79},
            "academicYear": {"id": 76},
        }
    }
    entry = {
        "sending_institution_id": 2,
        "receiving_institution_id": 79,
        "academic_year_id": 76,
    }

    with pytest.raises(ValueError, match="sending institution"):
        validate_capture(data, entry)


def test_capture_failure_keeps_manifest_context():
    entry = {
        "academic_year_id": 76,
        "sending_institution_id": 69,
        "sending_institution_name": "Chaffey College",
        "receiving_institution_id": 79,
        "output_file": "year_76_sending_069_chaffey-college_to_079_uc-berkeley.json",
        "url": "https://assist.org/example",
    }

    failure = capture_failure(entry, TimeoutError("timed out"))

    assert failure == {
        "academic_year_id": 76,
        "sending_institution_id": 69,
        "sending_institution_name": "Chaffey College",
        "receiving_institution_id": 79,
        "output_file": "year_76_sending_069_chaffey-college_to_079_uc-berkeley.json",
        "url": "https://assist.org/example",
        "error_type": "TimeoutError",
        "error": "timed out",
    }


class FakeResponse:
    url = "https://assist.org/api/Agreements?Key=76%2F2%2Fto%2F79%2FAllSendingPrefixes"

    async def json(self):
        return {
            "result": (
                '{"sendingInstitution":{"id":2},'
                '"receivingInstitution":{"id":79},'
                '"academicYear":{"id":76},'
                '"articulations":[{"name":"ANTH Anthropology"}]}'
            ),
            "validationFailure": None,
            "isSuccessful": True,
        }


class FakeResponseInfo:
    @property
    async def value(self):
        return FakeResponse()


class FakeExpectResponse:
    def __init__(self, predicate):
        self.predicate = predicate

    async def __aenter__(self):
        assert self.predicate(FakeResponse())
        return FakeResponseInfo()

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class FakePage:
    def __init__(self):
        self.goto_url = None
        self.wait_until = None

    def expect_response(self, predicate, timeout):
        assert timeout == 20000
        return FakeExpectResponse(predicate)

    async def goto(self, url, wait_until):
        self.goto_url = url
        self.wait_until = wait_until


class FakeContext:
    def __init__(self):
        self.page = FakePage()
        self.closed = False

    async def new_page(self):
        return self.page

    async def close(self):
        self.closed = True


class FakeBrowser:
    def __init__(self):
        self.context = FakeContext()

    async def new_context(self):
        return self.context


@pytest.mark.asyncio
async def test_intercept_extracts_agreement_response_and_closes_context():
    browser = FakeBrowser()
    url = (
        "https://assist.org/transfer/results?"
        "year=76&institution=2&agreement=79&viewByKey="
        "76%2F2%2Fto%2F79%2FAllSendingPrefixes"
    )

    parsed = await intercept(browser, url)

    assert parsed == {
        "result": {
            "sendingInstitution": {"id": 2},
            "receivingInstitution": {"id": 79},
            "academicYear": {"id": 76},
            "articulations": [{"name": "ANTH Anthropology"}],
        },
        "validationFailure": None,
        "isSuccessful": True,
    }
    assert browser.context.page.goto_url == url
    assert browser.context.page.wait_until == "domcontentloaded"
    assert browser.context.closed is True
