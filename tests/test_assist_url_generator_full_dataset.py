import json
from pathlib import Path

import pytest

from assist_url_generator import generate_all_assist_urls

DATA_DIR = Path("data")


@pytest.fixture(scope="module")
def institutions_json():
    """Load the full institutions.json file shipped with the repository."""
    return (DATA_DIR / "institutions.json").read_text()


@pytest.fixture(scope="module")
def expected_urls():
    """Load the authoritative list of URLs that were previously generated and
    stored in assist_urls.txt. Each line is one URL."""
    url_lines = (Path("tests/assist_urls.txt").read_text().splitlines())
    # Strip empty lines (defensive)
    return [u.strip() for u in url_lines if u.strip()]


def test_full_generation_matches_fixtures(institutions_json, expected_urls):
    """Generate URLs from scratch and ensure they match the checked-in list.

    This is a high-level integration test that protects against accidental
    regressions in the URL-generation logic or in the source data. If the
    institutions list or the generation algorithm changes, this test should be
    updated alongside the fixtures.
    """
    generated_urls = generate_all_assist_urls(institutions_json)

    # Fundamental count check first – easier to interpret when it fails.
    assert len(generated_urls) == len(expected_urls)

    # Compare as sets to ignore ordering differences.
    assert set(generated_urls) == set(expected_urls)


def test_first_and_last_urls_stable(expected_urls, institutions_json):
    """Spot-check that the lexicographically first and last URLs remain stable.

    This is an additional lightweight guard that will surface in test reports
    exactly which URL changed if the ordering or encoding is modified.
    """
    generated_urls = sorted(generate_all_assist_urls(institutions_json))
    expected_sorted = sorted(expected_urls)

    assert generated_urls[0] == expected_sorted[0]
    assert generated_urls[-1] == expected_sorted[-1] 