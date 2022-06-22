from flask import (Blueprint, request, render_template,
                    url_for, redirect)
from flask_login import login_required, current_user
from app.profile.utils import (save_picture, delete_picture)
from app.profile.forms import UpdateProfileForm
from app.models import (Course_User, User_Assignment, Course,
                        Assignment)
from app.filters import autoversion
from app import db

profile_ = Blueprint("profile", __name__)

@profile_.route('/dashboard/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    edit = request.args.get('edit')
    profile_image = url_for('static', filename="profile_images/" + current_user.profile_image)

    # check if user is student or teacher
    if current_user.profession == "Student":
        courses = Course_User.query.filter_by(user_id=current_user.id).all()
        assignments = User_Assignment.query.filter_by(user_id=current_user.id).all()
    elif current_user.profession == "Teacher":
        assignments = []
        courses = Course.query.filter_by(teacher_id=current_user.id).all()
        for course in courses:
            assignments.append(Assignment.query.filter_by(course_id=course.id).all())

    if request.method == 'GET' and edit:
        fullname = current_user.first_name + " " + current_user.last_name
        form.fullname.data = fullname
        form.email.data = current_user.email
        form.biography.data = current_user.biography
        return render_template('profile.html',
                                title='Profile',
                                profile_image=profile_image,
                                courses=courses,
                                assignments=assignments,
                                form=form,
                                edit=edit)
    elif request.method == "POST" and form.validate_on_submit():
        if not form.removepic.data and form.picture.data:
            # delete_picture()
            # picture_file = save_picture(form.picture.data)
            # current_user.profile_image = picture_file
            current_user.profile_image = "default.png" # ONLY FOR DEMO, REMOVE IF IN PRODUCTION
        elif form.removepic.data:
            # delete_picture()
            current_user.profile_image = "default.png"

        fullname = form.fullname.data.split(" ")
        first_name = fullname[0]
        last_name = " ".join(fullname[1:])
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.email = form.email.data
        current_user.biography = form.biography.data
        db.session.commit()

        return redirect(url_for("profile.profile"))
    elif form.errors:
        return render_template('profile.html',
                                title='Profile',
                                profile_image=profile_image,
                                courses=courses,
                                assignments=assignments,
                                form=form,
                                edit=edit)
    elif request.method == "GET":
        return render_template('profile.html',
                                title='Profile',
                                profile_image=profile_image,
                                courses=courses,
                                assignments=assignments,
                                form=form)