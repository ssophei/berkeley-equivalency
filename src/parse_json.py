import json

with open('../docs/ivc-berkeley-ds-test.json') as file:
    response = json.load(file)

templateAssets = json.loads(response['result']['templateAssets'])
articulations = json.loads(response['result']['articulations'])
courses = []
for group in templateAssets:
    if group['type'] == 'RequirementGroup':
        for section in group['sections']:
            for row in section.get('rows', []):
                for cell in row['cells']:
                    if cell['type'] == 'Course':
                        course = cell['course']
                        course_info = {
                            'title': course.get('courseTitle'),
                            'course prefix': course.get('prefix'),
                            'course number': course.get('courseNumber'),
                            'department': course.get('department'),
                            'min units': course.get('minUnits'),
                            'max units': course.get('maxUnits'),
                            'course attributes': course.get('courseAttributes', None),
                            'cross listed courses': course.get('visibleCrossListedCourses', None),
                            'requisites': course.get('requisites', None)
                        }
                        courses.append(course_info)
print(courses)
# print(articulations)