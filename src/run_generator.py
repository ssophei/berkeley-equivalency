import json

# Using the actual JSON data from the document
institutions_data = """[{"id":1,"names":[{"name":"California Maritime Academy","hasDepartments":true,"hideInList":false},{"name":"California State University, Maritime Academy","fromYear":2015,"hasDepartments":true,"hideInList":false}],"code":"CSUMA   ","prefers2016LegacyReport":false,"isCommunityCollege":false,"category":0,"termType":0,"beginId":31,"termTypeAcademicYears":[{"termType":0,"fromYear":2015},{"termType":0,"fromYear":1980}]},{"id":2,"names":[{"name":"Evergreen Valley College","hasDepartments":true,"hideInList":false}],"code":"EVERGRN ","prefers2016LegacyReport":false,"isCommunityCollege":true,"category":2,"termType":0,"beginId":31,"termTypeAcademicYears":[{"termType":0,"fromYear":2016},{"termType":0,"fromYear":1980}]}]"""

from assist_url_generator import generate_all_assist_urls, load_institutions, filter_community_colleges, filter_universities

# Load the full institutions data from the document
with open('data/institutions.json', 'r') as f:
    full_institutions_json = f.read()

# Generate all URLs
urls = generate_all_assist_urls(full_institutions_json)

# Analyze the data
institutions = load_institutions(full_institutions_json)
ccc_ids = filter_community_colleges(institutions)
university_ids = filter_universities(institutions)

print(f"Analysis of institutions data:")
print(f"Total institutions: {len(institutions)}")
print(f"Community Colleges: {len(ccc_ids)}")
print(f"Universities (CSU/UC): {len(university_ids)}")
print(f"Total URLs generated: {len(urls)}")
print(f"Expected total: {len(ccc_ids)} × {len(university_ids)} = {len(ccc_ids) * len(university_ids)}")

print(f"\nFirst 10 Community College IDs: {ccc_ids[:10]}")
print(f"First 10 University IDs: {university_ids[:10]}")

print(f"\nSample URLs:")
for i, url in enumerate(urls[:5]):
    print(f"{i+1}. {url}")

# Save all URLs to a file
with open('assist_urls.txt', 'w') as f:
    for url in urls:
        f.write(url + '\n')

print(f"\nAll {len(urls)} URLs saved to 'assist_urls.txt'")