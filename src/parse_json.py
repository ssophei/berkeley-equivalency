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
                            'course': f'{course.get('prefix')} {course.get('courseNumber')}: {course.get('courseTitle')}',
                            'department': course.get('department'),
                            'units': [course.get('minUnits'), course.get('maxUnits')],
                            'course attributes': course.get('courseAttributes'),
                            'cross-listed courses': course.get('visibleCrossListedCourses'),
                            'requisites': course.get('requisites')
                        }
                        courses.append(course_info)
# print(articulations)
for template_cell in articulations:
    receiving_course = template_cell['articulation']['course']
    receiving_course_name =  f'{receiving_course.get('prefix')} {receiving_course.get('courseNumber')}: {receiving_course.get('courseTitle')}'
    for course in courses:
        if course['course'] == receiving_course_name:
            print(course['course'])
            print(template_cell['articulation']['sendingArticulation'])
    # print(receiving_course_name)