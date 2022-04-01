from flask import Blueprint, render_template, url_for
from flask_login import login_required, current_user
from app.models import (Course_User, User_Assignment,
                        Assignment)
from app.filters import autoversion

deadlines_ = Blueprint("deadlines", __name__)

@deadlines_.route('/dashboard/deadlines', methods=['GET'])
@login_required
def deadlines():
    profile_image = url_for('static', filename="profile_images/" + current_user.profile_image)
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
                            profile_image=profile_image,
                            assignments=assignments_due,
                            title="Deadlines")