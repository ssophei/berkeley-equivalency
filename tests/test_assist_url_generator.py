import pytest
import json
from assist_url_generator import (
    load_institutions,
    filter_community_colleges,
    filter_universities,
    generate_assist_url,
    generate_all_assist_urls
)

@pytest.fixture
def sample_institutions_list():
    """Sample institutions list for testing."""
    return [
        {
            "id": 1,
            "names": [{"name": "California Maritime Academy"}],
            "isCommunityCollege": False,
            "category": 0
        },
        {
            "id": 2,
            "names": [{"name": "Evergreen Valley College"}],
            "isCommunityCollege": True,
            "category": 2
        },
        {
            "id": 3,
            "names": [{"name": "Los Angeles City College"}],
            "isCommunityCollege": True,
            "category": 2
        },
        {
            "id": 7,
            "names": [{"name": "University of California, San Diego"}],
            "isCommunityCollege": False,
            "category": 1
        }
    ]

@pytest.fixture
def sample_institutions_json():
    """Sample institutions data for testing."""
    return json.dumps(sample_institutions_list())





class TestLoadInstitutions:
    """Test cases for load_institutions function."""
    
    def test_load_institutions_valid_json(self, sample_institutions_json):
        """Test loading valid JSON data."""
        result = load_institutions(sample_institutions_json)
        assert isinstance(result, list)
        assert len(result) == 4
        assert result[0]['id'] == 1
        assert result[1]['isCommunityCollege'] is True
    
    def test_load_institutions_empty_json(self):
        """Test loading empty JSON array."""
        result = load_institutions('[]')
        assert result == []
    
    def test_load_institutions_invalid_json(self):
        """Test loading invalid JSON raises exception."""
        with pytest.raises(json.JSONDecodeError):
            load_institutions('invalid json')


class TestFilterCommunityColleges:
    """Test cases for filter_community_colleges function."""
    
    def test_filter_community_colleges_normal_case(self, sample_institutions_list):
        """Test filtering community colleges from normal data."""
        result = filter_community_colleges(sample_institutions_list)
        assert result == [2, 3]
        assert len(result) == 2
    
    def test_filter_community_colleges_no_ccc(self):
        """Test filtering when no community colleges exist."""
        institutions = [
            {"id": 1, "isCommunityCollege": False},
            {"id": 2, "isCommunityCollege": False}
        ]
        result = filter_community_colleges(institutions)
        assert result == []
    
    def test_filter_community_colleges_all_ccc(self):
        """Test filtering when all are community colleges."""
        institutions = [
            {"id": 1, "isCommunityCollege": True},
            {"id": 2, "isCommunityCollege": True}
        ]
        result = filter_community_colleges(institutions)
        assert result == [1, 2]
    
    def test_filter_community_colleges_missing_field(self):
        """Test filtering when isCommunityCollege field is missing."""
        institutions = [
            {"id": 1},  # Missing isCommunityCollege field
            {"id": 2, "isCommunityCollege": True}
        ]
        result = filter_community_colleges(institutions)
        assert result == [2]


class TestFilterUniversities:
    """Test cases for filter_universities function."""
    
    def test_filter_universities_normal_case(self, sample_institutions_list):
        """Test filtering universities from normal data."""
        result = filter_universities(sample_institutions_list)
        assert result == [1, 7]
        assert len(result) == 2
    
    def test_filter_universities_no_universities(self):
        """Test filtering when no universities exist."""
        institutions = [
            {"id": 1, "isCommunityCollege": True},
            {"id": 2, "isCommunityCollege": True}
        ]
        result = filter_universities(institutions)
        assert result == []
    
    def test_filter_universities_all_universities(self):
        """Test filtering when all are universities."""
        institutions = [
            {"id": 1, "isCommunityCollege": False},
            {"id": 2, "isCommunityCollege": False}
        ]
        result = filter_universities(institutions)
        assert result == [1, 2]


class TestGenerateAssistUrl:
    """Test cases for generate_assist_url function."""
    
    def test_generate_assist_url_normal_case(self):
        """Test URL generation with normal parameters."""
        url = generate_assist_url(75, 2, 7)
        expected_url = (
            "https://assist.org/transfer/results?"
            "year=75&"
            "institution=2&"
            "agreement=7&"
            "agreementType=to&"
            "viewAgreementsOptions=true&"
            "view=agreement&"
            "viewBy=major&"
            "viewSendingAgreements=false&"
            "viewByKey=75%2F2%2Fto%2F7%2FAllMajors"
        )
        assert url == expected_url
    
    def test_generate_assist_url_different_year(self):
        """Test URL generation with different year."""
        url = generate_assist_url(76, 2, 7)
        assert "year=76" in url
        assert "viewByKey=76%2F2%2Fto%2F7%2FAllMajors" in url
    
    def test_generate_assist_url_large_ids(self):
        """Test URL generation with large institution IDs."""
        url = generate_assist_url(75, 999, 888)
        assert "institution=999" in url
        assert "agreement=888" in url
        assert "viewByKey=75%2F999%2Fto%2F888%2FAllMajors" in url


class TestGenerateAllAssistUrls:
    """Test cases for generate_all_assist_urls function."""
    
    def test_generate_all_assist_urls_normal_case(self, sample_institutions_json):
        """Test generating all URLs with normal data."""
        urls = generate_all_assist_urls(sample_institutions_json)
        # 2 CCCs × 2 Universities = 4 URLs
        assert len(urls) == 4
        
        # Check that all combinations are present
        expected_combinations = [
            (2, 1), (2, 7),  # Evergreen Valley College to both universities
            (3, 1), (3, 7)   # Los Angeles City College to both universities
        ]
        
        for ccc_id, univ_id in expected_combinations:
            expected_url = generate_assist_url(75, ccc_id, univ_id)
            assert expected_url in urls
    
    def test_generate_all_assist_urls_no_ccc(self):
        """Test generating URLs when no community colleges exist."""
        institutions_json = json.dumps([
            {"id": 1, "isCommunityCollege": False},
            {"id": 2, "isCommunityCollege": False}
        ])
        urls = generate_all_assist_urls(institutions_json)
        assert urls == []
    
    def test_generate_all_assist_urls_no_universities(self):
        """Test generating URLs when no universities exist."""
        institutions_json = json.dumps([
            {"id": 1, "isCommunityCollege": True},
            {"id": 2, "isCommunityCollege": True}
        ])
        urls = generate_all_assist_urls(institutions_json)
        assert urls == []
    
    def test_generate_all_assist_urls_custom_year(self, sample_institutions_json):
        """Test generating URLs with custom year."""
        urls = generate_all_assist_urls(sample_institutions_json, year=76)
        assert len(urls) == 4
        for url in urls:
            assert "year=76" in url
            assert "76%2F" in url  # Check encoded viewByKey


class TestIntegration:
    """Integration tests using the actual data structure."""
    
    def test_url_format_compliance(self, sample_institutions_json):
        """Test that generated URLs comply with the expected format."""
        urls = generate_all_assist_urls(sample_institutions_json)
        
        for url in urls:
            # Check base URL
            assert url.startswith("https://assist.org/transfer/results?")
            
            # Check required parameters
            assert "year=" in url
            assert "institution=" in url
            assert "agreement=" in url
            assert "agreementType=to" in url
            assert "viewAgreementsOptions=true" in url
            assert "view=agreement" in url
            assert "viewBy=major" in url
            assert "viewSendingAgreements=false" in url
            assert "viewByKey=" in url
            
            # Check viewByKey format (URL encoded)
            assert "%2F" in url  # Forward slashes should be encoded
            assert "%2FAllMajors" in url
    
    def test_no_duplicate_urls(self, sample_institutions_json):
        """Test that no duplicate URLs are generated."""
        urls = generate_all_assist_urls(sample_institutions_json)
        assert len(urls) == len(set(urls))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])