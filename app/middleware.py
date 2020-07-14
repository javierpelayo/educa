from flask import flash, redirect, url_for
from flask_login import current_user
from app.models import Course, Course_User
from functools import wraps

# Used to check if the user is in the course
def course_auth(f):
    @wraps(f)
    def identify(*args, **kwargs):

        course = Course.query.filter_by(id=kwargs['course_id']).first()
        course_user = Course_User.query.filter_by(user_id=current_user.id, course_id=course.id).first()

        if current_user.id != course.teacher_id:
            if not course_user:
                flash("You are not in this course.", "warning")
                return redirect(url_for("courses.courses"))
        return f(*args, **kwargs)

    return identify

# Used to check if the user is a teacher of the course
def teacher_auth(f):
    @wraps(f)
    def identify(*args, **kwargs):
        course = Course.query.filter_by(id=kwargs['course_id']).first()
        if current_user.id != course.teacher_id:
            flash("You do not have permission to access this page.", "warning")
            return redirect(url_for('courses.courses'))

        return f(*args, **kwargs)
    return identify