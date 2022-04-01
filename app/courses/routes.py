from flask import (Blueprint, send_file, current_app, url_for,
                    redirect, flash, request, render_template)
from flask_login import login_required, current_user
from app.courses.forms import (NewCourseForm, AddCourseForm, UpdateCourseForm,
                                UpdateSyllabusForm)
from app.models import (Course, Course_User)
from app.middleware import course_auth, teacher_auth
from app import db
import os

courses_ = Blueprint("courses", __name__, static_url_path='static')

@courses_.route('/download/<string:filename>', methods=['GET'])
@login_required
def download_file(filename):
    file_path = os.path.join(current_app.root_path, 'static/assignments', filename)
    return send_file(file_path, as_attachment=True)

@courses_.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('courses.courses'))

@courses_.route('/dashboard/courses', methods=['GET', 'POST'])
@login_required
def courses():
    profile_image = url_for('static', filename="profile_images/" + current_user.profile_image)
    teacher_courses = Course.query.filter_by(teacher_id=current_user.id).all()

    # Get the student courses
    # NEEDS REFACTORING/MORE EFFICIENT WAY
    user_courses = Course_User.query.filter_by(user_id=current_user.id).all()
    student_courses = []
    for i in range(len(user_courses)):
        student_courses.append(Course.query.filter_by(id=user_courses[i].course_id).first())

    # sort the courses by id for template rendering and consistency
    teacher_courses.sort(key=lambda c:c.id)
    student_courses.sort(key=lambda c:c.id)

    # For Students
    add_course = AddCourseForm()

    # For Teachers
    new_course = NewCourseForm()

    # POST
    if new_course.validate_on_submit():
        course = Course(teacher_id=current_user.id,
                        title=new_course.title.data,
                        subject=new_course.subject.data,
                        points=new_course.points.data,
                        code=new_course.code.data,
                        join=(new_course.join.data == "True"))
        db.session.add(course)
        db.session.commit()
        return redirect(url_for("courses.courses"))
    elif add_course.validate_on_submit():
        course = Course.query.filter_by(id=add_course.course_id.data, code=add_course.code.data).first()
        if course:
            if str(current_user.id) in list(course.dropped):
                flash("You were dropped from this course and can no longer join.", "warning")
                return redirect(url_for("courses.courses"))

            if course.join:
                course_user = Course_User.query.filter_by(user_id=current_user.id, course_id=course.id).first()

                if course_user:
                    flash("You are already in this course", "primary")
                    return redirect(url_for("courses.courses"))
                else:
                    course_user = Course_User(user_id=current_user.id,
                                            course_id=add_course.course_id.data)
                    db.session.add(course_user)
                    db.session.commit()

                    flash(f"Successfully added course: {course.title}!", "success")
                    return redirect(url_for("courses.courses"))
            else:
                flash("Course is not open to new students.", "primary")
                return redirect(url_for("courses.courses"))
        else:
            flash(f"That course does not exist.", "warning")
            return redirect(url_for("courses.courses"))
    elif new_course.errors or add_course.errors:
        #
        # ERROR TESTING
        #
        flash("There was an error in adding that course.", "danger")
        return redirect(url_for("courses.courses"))

    if request.method == "GET" and current_user.profession == "Teacher":
        return render_template('courses.html',
                                profile_image=profile_image,
                                courses=teacher_courses,
                                new_course=new_course,
                                title="Courses")
    elif request.method == "GET" and current_user.profession == "Student":
        return render_template('courses.html',
                                profile_image=profile_image,
                                courses=student_courses,
                                add_course=add_course,
                                title="Courses")

@courses_.route('/dashboard/courses/<int:course_id>', methods=['GET', 'POST'])
@login_required
@course_auth
def course(course_id):
    profile_image = url_for('static', filename="profile_images/" + current_user.profile_image)
    course = Course.query.filter_by(id=course_id).first()
    teacher = (course.teacher_id == current_user.id)

    drop = request.form.get('drop')

    if not teacher and request.method == "GET":
        return render_template('course.html',
                                profile_image=profile_image,
                                course=course,
                                title="Course - " + str(course.title))

    elif not teacher and request.method == "POST" and drop:
        course_user = Course_User.query.filter_by(course_id=course.id, user_id=current_user.id).first()
        for a in current_user.assignments:
            db.session.delete(a)
        db.session.delete(course_user)
        db.session.commit()

        flash("You have dropped the course.", "success")
        return redirect(url_for("courses.courses"))

    delete = request.form.get('delete')
    edit_course_form = UpdateCourseForm()

    if request.method == "GET":
        edit_course_form.title.data = course.title
        edit_course_form.subject.data = course.subject
        edit_course_form.points.data = course.points
        edit_course_form.code.data = course.code
        edit_course_form.join.data = str(course.join)

        return render_template('course.html',
                                profile_image=profile_image,
                                course=course,
                                edit_course_form=edit_course_form,
                                title="Course - " + str(course.title))

    if teacher and request.method == "POST" and delete:

        # Deletes all assignments, questions, options,
        # user_assignments, course_users
        db.session.delete(course)
        db.session.commit()

        flash("Course has been successfully deleted.", "success")
        return redirect(url_for("courses.courses"))
    elif teacher and edit_course_form.validate_on_submit():
        course.title = edit_course_form.title.data
        course.subject = edit_course_form.subject.data
        course.points = edit_course_form.points.data
        course.code = edit_course_form.code.data
        course.join = (edit_course_form.join.data == "True")

        db.session.commit()

        flash("Course was updated successfully.", "success")
        return redirect(url_for("courses.course", course_id=course.id))
    elif teacher and edit_course_form.errors:
        flash(f"Could not update course due to a form error.", "danger")
        return redirect(url_for("courses.course", course_id=course.id))

@courses_.route('/dashboard/courses/<int:course_id>/edit_syllabus', methods=['GET', 'POST'])
@login_required
@course_auth
@teacher_auth
def course_syllabus(course_id):
    profile_image = url_for('static', filename="profile_images/" + current_user.profile_image)
    course = Course.query.filter_by(id=course_id).first()
    syllabusform = UpdateSyllabusForm()

    if syllabusform.validate_on_submit():
        course.syllabus = syllabusform.syllabus.data
        db.session.commit()

        flash("Course syllabus was updated successfully!", "success")
        return redirect(url_for("courses.course", course_id=course.id))
    elif request.method == "GET":
        syllabusform.syllabus.data = course.syllabus
        return render_template('course_syllabus.html',
                                profile_image=profile_image,
                                course=course,
                                syllabusform=syllabusform,
                                title=str(course.title) + " - Syllabus")