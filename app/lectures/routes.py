from flask import (Blueprint, request, render_template,
                    redirect, url_for, flash)
from flask_login import login_required, current_user
from app.lectures.forms import NewLectureForm
from app.filters import autoversion
from app.middleware import course_auth, teacher_auth
from app.models import (Course, Lecture)
from app import db
lectures_ = Blueprint("lectures", __name__)

@lectures_.route('/dashboard/courses/<int:course_id>/lectures', methods=['GET', 'POST'])
@login_required
@course_auth
def lectures(course_id):
    profile_image = url_for('static', filename="profile_images/" + current_user.profile_image)
    course = Course.query.filter_by(id=course_id).first()
    lectures = Lecture.query.filter_by(course_id=course_id).all()
    lectures.sort(key=lambda l:l.created_time)

    if request.method == "GET":
        return render_template("lectures.html",
                                profile_image=profile_image,
                                course=course,
                                lectures=lectures,
                                title=f"{course.title} - Lectures")


@lectures_.route('/dashboard/courses/<int:course_id>/lectures/new', methods=['GET', 'POST'])
@login_required
@course_auth
@teacher_auth
def new_lecture(course_id):
    profile_image = url_for('static', filename="profile_images/" + current_user.profile_image)
    course = Course.query.filter_by(id=course_id).first()
    form = NewLectureForm()

    if request.method == "POST" and form.validate_on_submit():
        url = form.url.data
        if "watch?v=" in url:
            url = url.replace("watch?v=", "embed/")
        else:
            url = url.split("/")[-1]
            url = "https://youtube.com/embed/" + url

        lecture = Lecture(course_id=course.id,
                            title=form.title.data,
                            url=url,
                            description=form.description.data)
        db.session.add(lecture)
        db.session.commit()

        flash("Lecture was successfully uploaded.", "success")
        return redirect(url_for("lectures.lectures", course_id=course.id))
    else:
        return render_template("new_lecture.html",
                                profile_image=profile_image,
                                course=course,
                                form=form,
                                title=f"{course.title} - New Lecture",
                                header=" \\ New Lecture")

@lectures_.route('/dashboard/courses/<int:course_id>/lectures/<int:lecture_id>', methods=['GET', 'POST'])
@login_required
@course_auth
def lecture(course_id, lecture_id):
    profile_image = url_for('static', filename="profile_images/" + current_user.profile_image)
    course = Course.query.filter_by(id=course_id).first()
    lecture = Lecture.query.filter_by(id=lecture_id).first()

    if request.method == "GET":
        return render_template("lecture.html",
                                profile_image=profile_image,
                                course=course,
                                lecture=lecture,
                                title=f"{course.title} - Lecture",
                                header=" \\ " + lecture.title)