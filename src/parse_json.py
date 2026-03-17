import json

with open('../docs/ivc-berkeley-ds.json') as file:
    response = json.load(file)

templateAssets = response.get('result').get('templateAssets')
articulations = response.get('result').get('articulations')
# articulations = json.loads(response['result']['articulations'])
courses = []
for group in templateAssets:
    if group['type'] == 'RequirementGroup':
        for section in group['sections']:
            for row in section.get('rows', []):
                for cell in row['cells']:
                    if cell['type'] == 'Course':
                        course = cell['course']
                        course_info = {
                            'internal id': course.get('courseIdentifierParentId'),
                            'department': course.get('department'),
                            'title': course.get('courseTitle'),
                            'course prefix': course.get('prefix'),
                            'course number': course.get('courseNumber'),
                            'course': f'{course.get('prefix')} {course.get('courseNumber')}: {course.get('courseTitle')}',
                            'units': [course.get('minUnits'), course.get('maxUnits')],
                            'course attributes': cell.get('courseAttributes'),
                            'cross-listed courses': cell.get('visibleCrossListedCourses'),
                            'requisites': cell.get('requisites')
                        }
                        courses.append(course_info)
courses = json.dumps(courses, indent=2)
# for template_cell in articulations:
#     receiving_course = template_cell['articulation']['course']
#     receiving_course_name =  f'{receiving_course.get('prefix')} {receiving_course.get('courseNumber')}: {receiving_course.get('courseTitle')}'
#     for course in courses:
#         if course['course'] == receiving_course_name:
#             print(course['course'])
#             print(template_cell['articulation']['sendingArticulation'].get('items'))
    # print(receiving_course_name)
print(courses)