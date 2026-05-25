import json
from pathlib import Path

import pytest

from berkeley_url_generator import generate_all_assist_urls, generate_assist_manifest


DATA_DIR = Path("data")


@pytest.fixture(scope="module")
def institutions_json():
    return (DATA_DIR / "institutions.json").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def expected_urls():
    return json.loads((DATA_DIR / "urls.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def expected_manifest():
    return json.loads((DATA_DIR / "url_manifest.json").read_text(encoding="utf-8"))


def test_full_generation_matches_checked_in_berkeley_urls(
    institutions_json, expected_urls
):
    generated_urls = generate_all_assist_urls(institutions_json)

    assert generated_urls == expected_urls
    assert len(generated_urls) == 116


def test_full_generation_uses_current_prefix_agreement_contract(expected_urls):
    assert expected_urls

    for url in expected_urls:
        assert "agreement=79" in url
        assert "viewBy=prefix" in url
        assert "viewSendingAgreements=true" in url
        assert "%2FAllSendingPrefixes" in url
        assert "%2FAllMajors" not in url


def test_full_manifest_matches_checked_in_manifest(
    institutions_json, expected_manifest
):
    generated_manifest = generate_assist_manifest(institutions_json)

    assert generated_manifest == expected_manifest
    assert len(generated_manifest) == 116


def test_full_manifest_has_deterministic_human_readable_filenames(
    expected_manifest,
):
    first = expected_manifest[0]

    assert first["sending_institution_id"] == 2
    assert first["sending_institution_name"] == "Evergreen Valley College"
    assert first["output_file"] == (
        "year_76_sending_002_evergreen-valley-college"
        "_to_079_uc-berkeley.json"
    )
    assert all(entry["output_file"].endswith(".json") for entry in expected_manifest)
    assert len({entry["output_file"] for entry in expected_manifest}) == len(
        expected_manifest
    )
