from app.models import Assignment, Course_User, User_Assignment
from collections import OrderedDict
import json

def grades_edit_error_handler(request_form, course):
    errors = {}
    total_points = 0

    for key, value in request_form.items():
        if "assignment_" in key:
            try:
                total_points += int(value)
            except:
                if value != "-":
                    errors[key] = "Not a valid integer or hyphen."
    if total_points > course.points:
        for key, value in request_form.items():
            if "assignment_" in key:
                errors[key] = f"Total assignment points exceeds the course points: {course.points}"

    return errors

def calculate_grade(course_user, assignment, points):
    total_assignment_points = 0
    if course_user.assignments_done:
        assignments_done = json.loads(course_user.assignments_done)
    else:
        assignments_done = {}

    if str(assignment.id) in assignments_done:
        if assignments_done[str(assignment.id)] < points:

            course_user.points -= assignments_done[str(assignment.id)]
            course_user.points += points

            assignments_done[str(assignment.id)] = points
    else:
        course_user.points += points
        assignments_done[str(assignment.id)] = points

    # used for recalculating the course grade according
    # to the assignments the student has turned in
    for key in assignments_done:
        a_done = Assignment.query.filter_by(id=int(key)).first()
        total_assignment_points += a_done.points

    course_user.assignments_done = json.dumps(assignments_done)

    try:
        leftover_points = course_user.points/total_assignment_points
    except ZeroDivisionError:
        leftover_points = 0

    course_user.grade = '{:.2%}'.format(leftover_points)

# used to gather information about
# a user for grades template rendering
def user_grades(course, user_id):
    course_user = Course_User.query.filter_by(user_id=user_id, course_id=course.id).first()
    assignments = Assignment.query.filter_by(course_id=course.id).all()
    assignments.sort(key=lambda a:a.duedate_time)

    user_latest_assignments = []

    # OrderedDict is for the template so it renders as shown here
    user_points = OrderedDict([("Exam/Quiz", 0), ("Lab", 0), ("HW", 0), ("Instructions", 0)])
    assignment_points = OrderedDict([("Exam/Quiz", 0), ("Lab", 0), ("HW", 0), ("Instructions", 0)])

    # get all user assignments and add the points for each assignment type
    for assignment in assignments:
        user_assignments = User_Assignment.query.filter_by(user_id=user_id, assignment_id=assignment.id).all()
        if user_assignments:
            user_assignments.sort(key=lambda ua:ua.created_time)
            user_latest_assignments.append(user_assignments[-1])
        else:
            # used to keep the index the same as the assignment,
            # a 0 means they haven't turned it in
            user_latest_assignments.append(0)
        assignment_points[assignment.type] += assignment.points

    # add how much the student scored for each assignment and its type
    for user_assignment in user_latest_assignments:
        if user_assignment != 0:
            user_points[user_assignment.type] += user_assignment.points

    current_assignment_points = sum(assignment_points.values())

    return (course_user, assignments, user_latest_assignments,
            user_points, assignment_points, current_assignment_points)