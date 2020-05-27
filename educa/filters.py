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

#
# Middleware Section
#

# Used to check if the user is in the course
def course_auth(f):
    @wraps(f)
    def identify(*args, **kwargs):

        course = Course.query.filter_by(id=kwargs['course_id']).first()
        course_user = Course_User.query.filter_by(user_id=current_user.id, course_id=course.id).first()

        if current_user.id != course.teacher_id:
            if not course_user:
                return redirect(url_for("courses"))
        return f(*args, **kwargs)

    return identify

# used to check if the user is a teacher of the course
def teacher_auth(f):
    @wraps(f)
    def identify(*args, **kwargs):
        course = Course.query.filter_by(id=kwargs['course_id']).first()
        if current_user.id != course.teacher_id:
            return redirect(url_for('courses'))

        return f(*args, **kwargs)
    return identify
