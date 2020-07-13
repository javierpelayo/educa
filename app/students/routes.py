from flask import (Blueprint, redirect, url_for, request,
                    render_template, flash)
from flask_login import login_required, current_user
from app.students.utils import (grades_edit_error_handler, calculate_grade,
                                user_grades)
from app.models import (Course, User_Account, Assignment,
                        Course_User, User_Assignment)
from app.filters import autoversion, course_auth, teacher_auth
from app.assignments.utils import delete_assignment
from app import db
import json

students_ = Blueprint("students", __name__)

@students_.route('/dashboard/courses/<int:course_id>/grades', methods=['GET'])
@login_required
@course_auth
def grades(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if current_user.id == course.teacher_id:
        return redirect(url_for("students", course_id=course.id))

    (course_user, assignments,
    user_latest_assignments,
    user_points, assignment_points,
    current_assignment_points) = user_grades(course, current_user.id)

    if request.method == "GET":
        return render_template('grades.html',
                                course=course,
                                course_user=course_user,
                                assignments=assignments,
                                user_latest_assignments=user_latest_assignments,
                                assignment_points=assignment_points,
                                user_points=user_points,
                                current_assignment_points=current_assignment_points,
                                title=course.title + " - Grades")

@students_.route('/dashboard/courses/<int:course_id>/students', methods=['GET', 'POST'])
@login_required
@course_auth
def students(course_id):
    course = Course.query.filter_by(id=course_id).first()
    course_students = Course_User.query.filter_by(course_id=course.id).all()
    teacher = User_Account.query.filter_by(id=course.teacher_id).first()
    students_list = []
    drop = request.form.get("drop")

    for student in course_students:
        user = User_Account.query.filter_by(id=student.user_id).first()
        students_list.append(user)

    if request.method == "POST" and drop:
        for course_user in course_students:
            if course_user.user_id == int(drop):
                assignments = Assignment.query.filter_by(course_id=course.id).all()
                for a in assignments:
                    user_assignments = User_Assignment.query.filter_by(user_id=course_user.user_id, assignment_id=a.id).all()
                    for ua in user_assignments:
                        db.session.delete(ua)

                dropped = list(course.dropped)
                dropped.append(drop)
                course.dropped = dropped
                db.session.delete(course_user)

        db.session.commit()
        flash("User has been dropped from course.", "success")
        return redirect(url_for("students", course_id=course.id))
    elif request.method == "GET":
        return render_template("students.html",
                                course=course,
                                course_students=course_students,
                                students_list=students_list,
                                teacher=teacher,
                                title=course.title + " - Students")

@students.route('/dashboard/courses/<int:course_id>/students/<int:student_id>', methods=['GET'])
@login_required
@course_auth
def student(course_id, student_id):
    course = Course.query.filter_by(id=course_id).first()

    courses_user = Course_User.query.filter_by(user_id=student_id).all()
    assignments_user = User_Assignment.query.filter_by(user_id=student_id).all()

    user = User_Account.query.filter_by(id=student_id).first()

    if current_user.id == user.id:
        return redirect(url_for("profile"))

    profile_image = url_for('static', filename="profile_images/" + user.profile_image)

    if request.method == "GET":
        return render_template("student.html",
                                course=course,
                                user=user,
                                courses_user=courses_user,
                                assignments_user=assignments_user,
                                profile_image=profile_image,
                                title=course.title + " - " + user.first_name + " " + user.last_name)

@students_.route('/dashboard/courses/<int:course_id>/students/<int:student_id>/grades', methods=['GET', 'POST'])
@login_required
@course_auth
@teacher_auth
def student_grades(course_id, student_id):
    course = Course.query.filter_by(id=course_id).first()
    student = User_Account.query.filter_by(id=student_id).first()

    (course_user, assignments,
    user_latest_assignments,
    user_points, assignment_points,
    current_assignment_points) = user_grades(course, student_id)

    if request.method == "GET":
        return render_template("grades.html",
                                course=course,
                                course_user=course_user,
                                assignments=assignments,
                                user_latest_assignments=user_latest_assignments,
                                user_points=user_points,
                                assignment_points=assignment_points,
                                current_assignment_points=current_assignment_points,
                                student=student,
                                title=f"Grades - {student.first_name} {student.last_name}")

@students_.route('/dashboard/courses/<int:course_id>/students/<int:student_id>/grades/edit', methods=['GET', 'POST'])
@login_required
@course_auth
@teacher_auth
def student_grades_edit(course_id, student_id):
    course = Course.query.filter_by(id=course_id).first()
    student = User_Account.query.filter_by(id=student_id).first()

    (course_user, assignments,
    user_latest_assignments,
    user_points, assignment_points,
    current_assignment_points) = user_grades(course, student_id)

    request_form = request.form.to_dict()

    if "ajax" in request_form and request.method == "POST":
        return grades_edit_error_handler(request_form, course)
    elif request.method == "POST":
        errors = grades_edit_error_handler(request_form, course)

        # used if user bypasses ajax
        if errors:
            flash("Student grades could not be updated.", "danger")
            return redirect(url_for("student_grades", course_id=course.id, student_id=student.id))

        assignments_form = {}
        a_points = 0

        for key, value in request_form.items():
            print(f"{key} : {value}")
            if "assignment_" in key:
                id = key.split("_")
                id = id[1]
                try:
                    assignments_form[id] = int(value)
                except:
                    assignments_form[id] = value

        user_assignments = json.loads(course_user.assignments_done)
        for key, value in assignments_form.items():
            assignment = Assignment.query.filter_by(id=int(key)).first()
            user_assignment = User_Assignment.query.filter_by(user_id=student.id, assignment_id=int(key)).all()

            if user_assignment:
                user_assignment.sort(key=lambda a:a.created_time)

                if value != "-":
                    a_points += assignment.points
                    user_assignment[-1].points = value

                    course_user.points -= user_assignments[key]
                    course_user.points += value

                    user_assignments[key] = value
                else:
                    if assignment.type == "Instructions":
                        for a in user_assignment:
                            delete_assignment(a.filename)

                    course_user.points -= user_assignments[key]

                    del user_assignments[key]

                    # deletes all user_assignments turned in for this assignment
                    for ua in user_assignment:
                        db.session.delete(ua)


            elif value != "-":
                a_points += assignment.points
                user_assignment = User_Assignment(user_id=student_id,
                                                assignment_id=assignment.id,
                                                points=value,
                                                tries=assignment.tries,
                                                type=assignment.type)
                course_user.points += value
                user_assignments[key] = value
                db.session.add(user_assignment)

        course_user.assignments_done = json.dumps(user_assignments)

        Assignment.query

        # grades should be based on assignments they have turned in
        if a_points > 0:
            course_user.grade = '{:.2%}'.format(course_user.points/a_points)
        else:
            course_user.grade = '{:.2%}'.format(0)

        db.session.commit()

        flash(f"Grades for {student.first_name} {student.last_name} have been updated.", "success")
        return redirect(url_for("student_grades", course_id=course.id, student_id=student.id))
    elif request.method == "GET":
        return render_template("grades_edit.html",
                                course=course,
                                course_user=course_user,
                                assignments=assignments,
                                user_latest_assignments=user_latest_assignments,
                                user_points=user_points,
                                assignment_points=assignment_points,
                                current_assignment_points=current_assignment_points,
                                student=student,
                                title=f"Grades - {student.first_name} {student.last_name}")

# view assignments that the user has turned in
@students_.route('/dashboard/courses/<int:course_id>/students/<int:student_id>/assignments', methods=['GET'])
@login_required
@course_auth
@teacher_auth
def student_assignments(course_id, student_id):
    course = Course.query.filter_by(id=course_id).first()
    student = User_Account.query.filter_by(id=student_id).first()
    assignments = course.assignments
    assignments.sort(key=lambda a:a.duedate_time)
    student_assignments = []

    for assignment in assignments:
        turned_in_assignments = User_Assignment.query.filter_by(user_id=student.id, assignment_id=assignment.id).all()
        if turned_in_assignments:
            turned_in_assignments.sort(key=lambda a:a.created_time)
            student_assignments.append(turned_in_assignments[-1])
        else:
            # used to keep the index same as assignments
            student_assignments.append(0)

    if request.method == "GET":
        return render_template("student_assignments.html",
                                course=course,
                                student=student,
                                assignments=assignments,
                                student_assignments=student_assignments,
                                title=f"Assignments - {student.first_name} {student.last_name}")


# view an individual student assignment
@students_.route('/dashboard/courses/<int:course_id>/students/<int:student_id>/assignments/<int:user_assignment_id>', methods=['GET'])
@login_required
@course_auth
@teacher_auth
def student_assignment(course_id, student_id, user_assignment_id):
    course = Course.query.filter_by(id=course_id).first()
    student = User_Account.query.filter_by(id=student_id).first()
    user_assignment = User_Assignment.query.filter_by(id=user_assignment_id).first()

    assignment = user_assignment.assignment
    questions = assignment.questions
    questions.sort(key=lambda q:q.id)
    options_dict = {}

    for question in questions:
        options = question.options
        options_dict[str(question.id)] = options

    if request.method == "GET":
        return render_template("student_assignment.html",
                                course=course,
                                student=student,
                                user_assignment=user_assignment,
                                assignment=assignment,
                                questions=questions,
                                options_dict=options_dict,
                                title=f"Assignment - {student.first_name} {student.last_name}")