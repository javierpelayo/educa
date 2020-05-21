from flask import request, redirect, url_for, flash
from . import app, db, routes
from flask_login import current_user
from educa.models import *
from functools import wraps
import os

# Queries the browser to force the
# download of an updated CSS/JS file
@app.template_filter()
def autoversion(filename):
  fullpath = os.path.join('./educa/', filename[1:])
  timestamp = str(os.path.getmtime(fullpath))
  shortpath = fullpath[7:]
  return f"{shortpath}?v={timestamp}"

# Used to check if the user is in the course
def course_auth(f):
    @wraps(f)
    def identify(*args, **kwargs):

        course = Course.query.filter_by(id=kwargs['course_id']).first()
        course_user = Course_User.query.filter_by(user_id=current_user.id, course_id=course.id).first()

        # check if user is in course if not redirect
        if current_user.id != course.teacher_id:
            if not course_user:
                flash("You are not in this course.", "warning")
                return redirect(url_for("courses"))
        return f(*args, **kwargs)

    return identify
