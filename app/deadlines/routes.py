from flask import Blueprint

deadlines = Blueprint("deadlines", __name__)

@deadlines.route('/dashboard/deadlines', methods=['GET'])
@login_required
def deadlines():
    courses = Course_User.query.filter_by(user_id=current_user.id).all()
    user_assignments = User_Assignment.query.filter_by(user_id=current_user.id).all()
    user_assignments = [ua.id for ua in user_assignments]
    assignments_due = []
    for course in courses:
        assignments = Assignment.query.filter_by(course_id=course.course_id).order_by(Assignment.duedate_time).all()[::-1]
        for assignment in assignments:
            if assignment.id not in user_assignments:
                assignments_due.append(assignment)

    return render_template("deadlines.html",
                            assignments=assignments_due,
                            title="Deadlines")