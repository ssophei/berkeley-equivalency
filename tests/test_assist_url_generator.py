import json

import pytest

from berkeley_url_generator import (
    BERKELEY_ID,
    filter_community_colleges,
    generate_all_assist_urls,
    generate_assist_url,
    generate_assist_manifest,
    generate_output_filename,
    load_institutions,
    slugify,
)


@pytest.fixture
def sample_institutions_list():
    return [
        {
            "id": 2,
            "names": [{"name": "Evergreen Valley College"}],
            "isCommunityCollege": True,
        },
        {
            "id": 3,
            "names": [{"name": "Los Angeles City College"}],
            "isCommunityCollege": True,
        },
        {
            "id": BERKELEY_ID,
            "names": [{"name": "University of California, Berkeley"}],
            "isCommunityCollege": False,
        },
    ]


@pytest.fixture
def sample_institutions_json(sample_institutions_list):
    return json.dumps(sample_institutions_list)


def test_load_institutions_valid_json(sample_institutions_json):
    result = load_institutions(sample_institutions_json)

    assert len(result) == 3
    assert result[0]["id"] == 2


def test_load_institutions_invalid_json():
    with pytest.raises(json.JSONDecodeError):
        load_institutions("invalid json")


def test_filter_community_colleges(sample_institutions_list):
    assert filter_community_colleges(sample_institutions_list) == [2, 3]


def test_filter_community_colleges_ignores_missing_flag():
    institutions = [{"id": 1}, {"id": 2, "isCommunityCollege": True}]

    assert filter_community_colleges(institutions) == [2]


def test_generate_assist_url_uses_berkeley_prefix_agreement_shape():
    url = generate_assist_url(76, 2)

    assert url == (
        "https://assist.org/transfer/results?"
        "year=76&"
        "institution=2&"
        "agreement=79&"
        "agreementType=to&"
        "viewAgreementsOptions=true&"
        "view=agreement&"
        "viewBy=prefix&"
        "viewSendingAgreements=true&"
        "viewByKey=76%2F2%2Fto%2F79%2FAllSendingPrefixes"
    )


def test_generate_assist_url_encodes_custom_year_and_ids():
    url = generate_assist_url(77, 999)

    assert "year=77" in url
    assert "institution=999" in url
    assert "agreement=79" in url
    assert "viewByKey=77%2F999%2Fto%2F79%2FAllSendingPrefixes" in url


def test_generate_all_assist_urls_only_targets_berkeley(sample_institutions_json):
    urls = generate_all_assist_urls(sample_institutions_json, year=76)

    assert urls == [
        generate_assist_url(76, 2),
        generate_assist_url(76, 3),
    ]


def test_slugify_produces_filename_safe_names():
    assert slugify("Los Angeles City College") == "los-angeles-city-college"
    assert slugify("College of the Sequoias") == "college-of-the-sequoias"


def test_generate_output_filename_includes_ids_and_school_names():
    assert generate_output_filename(
        76,
        2,
        "Evergreen Valley College",
    ) == "year_76_sending_002_evergreen-valley-college_to_079_uc-berkeley.json"


def test_generate_assist_manifest_includes_url_metadata_and_output_file(
    sample_institutions_json,
):
    manifest = generate_assist_manifest(sample_institutions_json, year=76)

    assert manifest == [
        {
            "academic_year_id": 76,
            "sending_institution_id": 2,
            "sending_institution_name": "Evergreen Valley College",
            "receiving_institution_id": BERKELEY_ID,
            "receiving_institution_name": "University of California, Berkeley",
            "url": generate_assist_url(76, 2),
            "output_file": (
                "year_76_sending_002_evergreen-valley-college"
                "_to_079_uc-berkeley.json"
            ),
        },
        {
            "academic_year_id": 76,
            "sending_institution_id": 3,
            "sending_institution_name": "Los Angeles City College",
            "receiving_institution_id": BERKELEY_ID,
            "receiving_institution_name": "University of California, Berkeley",
            "url": generate_assist_url(76, 3),
            "output_file": (
                "year_76_sending_003_los-angeles-city-college"
                "_to_079_uc-berkeley.json"
            ),
        },
    ]


def test_generate_all_assist_urls_no_community_colleges():
    institutions_json = json.dumps(
        [{"id": BERKELEY_ID, "isCommunityCollege": False}]
    )

    assert generate_all_assist_urls(institutions_json) == []


def test_no_duplicate_urls(sample_institutions_json):
    urls = generate_all_assist_urls(sample_institutions_json)

    assert len(urls) == len(set(urls))
