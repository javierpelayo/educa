from flask import (render_template, request,
                    redirect, url_for,
                    session, logging,
                    current_app, sessions, flash,
                    jsonify, Response)
from . import app, db, bcrypt, limiter
from educa.forms import (RegistrationForm,
                        LoginForm,
                        UpdateProfileForm,
                        NewCourseForm,
                        AddCourseForm,
                        UpdateCourseForm,
                        UpdateSyllabusForm,
                        AssignmentForm)
from educa.models import *
from flask_login import (login_user,
                        current_user,
                        logout_user,
                        login_required)
from functools import wraps
from educa.filters import autoversion, course_auth, teacher_auth
import secrets
from PIL import Image
from datetime import datetime
from time import time
from collections import OrderedDict
import os
import json

# Global Jinja Vars
@app.context_processor
def inject_pf_image():
    try:
        profile_image = url_for('static', filename="profile_images/" + current_user.profile_image)
    except:
        profile_image = url_for('static', filename="profile_images/default.png")
    return dict(profile_image=profile_image)

# ERROR ROUTES

@app.errorhandler(429)
def too_many_requests(e):
    return render_template("error/429.html"), 429

@app.errorhandler(404)
def not_found_error(e):
    db.session.rollback()
    return render_template("error/404.html"), 404

@app.errorhandler(500)
def interal_error(e):
    db.session.rollback()
    return render_template('error/500.html'), 500

# INTRODUCTION PAGES

@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html", title="Home")

@app.route('/about')
def about():
    return render_template("about.html", title="About")

@app.route('/packages')
def packages():
    return render_template("packages.html", title="Packages")


####### TEST ROUTE / REMOVE IN PRODUCTION #######
@app.route('/test')
def test():
    return render_template("test.html", title="Test")

@app.route('/process', methods=['POST'])
def process():
    email = request.form.get('email')
    name = request.form.get('name')
    print(email)
    print(name)
    if name and email:
        # reverses the name
        new_name = name[::-1]

        # no need to call jsonify since flask
        # parses out dictionaries as JSON
        return {'name': new_name}
    else:
        return redirect(url_for('about'))
    print("error")
    return {'error': 'Missing Data!'}

##################################################

# REGISTER / LOGIN / LOGOUT

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    # if the form is validated on submit
    if request.method == 'POST' and form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User_Account(first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    profession=form.profession.data,
                    password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        # User DB entry here
        return redirect(url_for('login'))
    else:
        return render_template("register.html", title="Register",
                                form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User_Account.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            print("Login Successful")
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            # if next_page query parameter exists redirect to that page
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            error = "The email or password is incorrect."
            return render_template("login.html",
                                    title="Login",
                                    form=form,
                                    error=error)
    else:
        return render_template("login.html",
                                title="Login",
                                form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# DASHBOARD

# MAIN ROUTE
@app.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('courses'))


# Profile Picture Functionality
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path,
                                'static/profile_images',
                                picture_fn)

    # Resize image using PILLOW
    output_size = (200,200)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def delete_picture():
    pic = current_user.profile_image
    if pic != "default.png":
        picture_path = os.path.join(app.root_path,
                                    'static/profile_images',
                                    pic)
        os.remove(picture_path)

@app.route('/dashboard/profile', methods=['GET', 'POST'])
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
            delete_picture()
            picture_file = save_picture(form.picture.data)
            current_user.profile_image = picture_file
        elif form.removepic.data:
            delete_picture()
            current_user.profile_image = "default.png"

        fullname = form.fullname.data.split(" ")
        first_name = fullname[0]
        last_name = " ".join(fullname[1:])
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.email = form.email.data
        current_user.biography = form.biography.data
        db.session.commit()

        return redirect(url_for('profile'))
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

@app.route('/dashboard/courses', methods=['GET', 'POST'])
@login_required
def courses():
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
        return redirect(url_for('courses'))
    elif add_course.validate_on_submit():
        course = Course.query.filter_by(id=add_course.course_id.data, code=add_course.code.data).first()
        if course:
            if course.join:
                course_user = Course_User.query.filter_by(user_id=current_user.id, course_id=course.id).first()

                if course_user:
                    flash("You are already in this course", "primary")
                    return redirect(url_for("courses"))
                else:
                    course_user = Course_User(user_id=current_user.id,
                                            course_id=add_course.course_id.data)
                    db.session.add(course_user)
                    db.session.commit()

                    flash(f"Successfully added course: {course.title}!", "success")
                    return redirect(url_for('courses'))
            else:
                flash("Course is not open to new students.", "primary")
                return redirect(url_for('courses'))
        else:
            flash(f"That course does not exist.", "warning")
            return redirect(url_for('courses'))
    elif new_course.errors or add_course.errors:
        #
        # ERROR TESTING
        #
        flash("There was an error in adding that course.", "danger")
        return redirect(url_for('courses'))

    if request.method == "GET" and current_user.profession == "Teacher":
        return render_template('courses.html',
                                courses=teacher_courses,
                                new_course=new_course,
                                title="Courses")
    elif request.method == "GET" and current_user.profession == "Student":
        return render_template('courses.html',
                                courses=student_courses,
                                add_course=add_course,
                                title="Courses")

@app.route('/dashboard/courses/<int:course_id>', methods=['GET', 'POST'])
@login_required
@course_auth
def course(course_id):
    course = Course.query.filter_by(id=course_id).first()
    teacher = (course.teacher_id == current_user.id)

    if not teacher:
        return render_template('course.html',
                                course=course,
                                title="Course - " + str(course.title))

    delete = request.form.get('delete')
    edit_course_form = UpdateCourseForm()

    if request.method == "GET":
        edit_course_form.title.data = course.title
        edit_course_form.subject.data = course.subject
        edit_course_form.points.data = course.points
        edit_course_form.code.data = course.code
        edit_course_form.join.data = str(course.join)

        return render_template('course.html',
                                course=course,
                                edit_course_form=edit_course_form,
                                title="Course - " + str(course.title))

    if teacher and request.method == "POST" and delete:

        # Deletes all assignments, questions, options,
        # user_assignments, course_users
        db.session.delete(course)
        db.session.commit()

        flash("Course has been successfully deleted.", "success")
        return redirect(url_for("courses"))
    elif teacher and edit_course_form.validate_on_submit():
        course.title = edit_course_form.title.data
        course.subject = edit_course_form.subject.data
        course.points = edit_course_form.points.data
        course.code = edit_course_form.code.data
        course.join = (edit_course_form.join.data == "True")

        db.session.commit()

        flash("Course was updated successfully.", "success")
        return redirect(url_for("course", course_id=course.id))
    elif edit_course_form.errors:
        flash(f"Could not update course due to a form error.", "danger")
        return redirect(url_for("course", course_id=course.id))

@app.route('/dashboard/courses/<int:course_id>/edit_syllabus', methods=['GET', 'POST'])
@login_required
@course_auth
@teacher_auth
def course_syllabus(course_id):
    course = Course.query.filter_by(id=course_id).first()
    syllabusform = UpdateSyllabusForm()

    if syllabusform.validate_on_submit():
        course.syllabus = syllabusform.syllabus.data
        db.session.commit()

        flash("Course syllabus was updated successfully!", "success")
        return redirect(url_for("course", course_id=course.id))
    elif request.method == "GET":
        syllabusform.syllabus.data = course.syllabus
        return render_template('course_syllabus.html',
                                course=course,
                                syllabusform=syllabusform,
                                title=str(course.title) + " - Syllabus")


@app.route('/dashboard/courses/<int:course_id>/assignments', methods=['GET'])
@login_required
@course_auth
def assignments(course_id):
    course = Course.query.filter_by(id=course_id).first()
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    assignments = sorted(assignments, key=lambda a: a.duedate_time)

    course_user = Course_User.query.filter_by(user_id=current_user.id, course_id=course.id).first()

    # check if user is in course if not redirect
    if current_user.id != course.teacher_id:
        if not course_user:
            return redirect(url_for("courses"))

    if request.method == "GET":
        return render_template('assignments.html',
                                course=course,
                                assignments=assignments,
                                current_time=time(),
                                title=str(course.title) + " - Assignments")

def new_assignment_error_handler(assignmentform, request_form):
    errors = {}
    assignmentform.validate()
    question_total_points = 0

    for key, value in assignmentform.errors.items():
        if key == "date_input":
            errors[key] = "Not a valid date value. ex: 01/25/2020"
        else:
            errors[key] = value[0]
    for key, value in request_form.items():
        if "qOption_" in key and value == "":
            errors[key] = "This field is required."
        elif "question_points" in key:
            try:
                question_total_points += int(value)
            except ValueError:
                errors[key] = "Not a valid integer value."
        elif "question_answer" not in key and "question_" in key and value == "":
            errors[key] = "This field is required."

    try:
        a_points = int(request_form["points"])
    except ValueError:
        a_points = 0

    if question_total_points > a_points:
        for key, value in request_form.items():
            if "question_points" in key:
                errors[key] = f"Total question points exceeds assignment points: {a_points}"

    return errors

@app.route('/dashboard/courses/<int:course_id>/assignments/new', methods=["GET", "POST"])
@login_required
@course_auth
@teacher_auth
def new_assignment(course_id):
    course = Course.query.filter_by(id=course_id).first()
    assignmentform = AssignmentForm()
    errors = {}

    request_form = request.form.to_dict()

    if 'ajax' in request_form and request.method == "POST":
        return new_assignment_error_handler(assignmentform, request_form)
    if request.method == "POST":

        # If user maliciously bypasses the ajax request
        errors = new_assignment_error_handler(assignmentform, request_form)
        if errors:
            flash("There was an error in creating the assignment.", "danger")
            return redirect(url_for("assignments", course_id=course.id))

        questions = {}
        options = {}
        q_ids = []
        question_option_ids = []
        question_amt = 0

        # separate the questions from the options
        for key, value in request_form.items():
            if "question_option" in key:
                options[key] = value
            elif "question_" in key:
                questions[key] = value

        # Split the POST question variables to just be question ids
        for key, value in questions.items():
            question_ids = key.split("_")
            question_id = question_ids[2]
            if question_id not in q_ids:
                q_ids.append(question_id)

        # Split the POST option variables to just be question ids with option ids
        for key, value in options.items():
            qu_op_ids = key.split("_")
            q_id = qu_op_ids[2]
            o_id = qu_op_ids[3]

            question_option_ids.append((q_id, o_id))

        q_ids.sort()
        question_amt = len(q_ids)

        date_input = assignmentform.date_input.data.strftime('%m/%d/%Y').split("/")
        hour = int(assignmentform.hour.data)
        minute = int(assignmentform.minute.data)
        month = int(date_input[0])
        day = int(date_input[1])
        year = int(date_input[2])

        datetime_object = datetime(year, month, day, hour, minute)

        duedate_time = datetime.timestamp(datetime_object)
        duedate_ctime = datetime_object.strftime("%b %d %Y %I:%M %p")

        assignment = Assignment(course_id=course.id,
                                points=assignmentform.points.data,
                                title=assignmentform.title.data,
                                content=assignmentform.content.data,
                                type=assignmentform.type.data,
                                tries=assignmentform.tries.data,
                                duedate_time=duedate_time,
                                duedate_ctime=duedate_ctime)
        db.session.add(assignment)
        db.session.commit()

        # CREATE each question for the assignment
        for x in range(question_amt):
            question = Question(assignment_id=assignment.id,
                                title=questions['question_title_' + str(x)],
                                content=questions['question_content_' + str(x)],
                                answer=questions['question_answer_' + str(x)],
                                points=questions['question_points_' + str(x)],
                                type=questions['question_type_' + str(x)])

            db.session.add(question)
            db.session.commit()

            # CREATE each option for that question
            for key, value in question_option_ids:
                if key == str(x):
                    option = Option(question_id=question.id,
                                    content=options["question_option_" + key + "_" + value])
                    db.session.add(option)
                    db.session.commit()

        flash("Assignment was created successfully!", "success")
        return redirect(url_for("assignments", course_id=course.id))

    elif request.method == "GET":
        return render_template('new_assignment.html',
                                course=course,
                                assignmentform=assignmentform,
                                title=str(course.title) + " - New Assignment")

@app.route('/dashboard/courses/<int:course_id>/assignments/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
@course_auth
def assignment(course_id, assignment_id):

    redo = request.args.get("redo")
    delete = request.form.get("delete")
    request_form = request.form.to_dict()

    course = Course.query.filter_by(id=course_id).first()
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    user_assignments = User_Assignment.query.filter_by(user_id=current_user.id, assignment_id=assignment.id).all()
    questions = Question.query.filter_by(assignment_id=assignment.id).all()
    options_dict = {}

    questions.sort(key=lambda q:q.id)
    user_assignments.sort(key=lambda a:a.points)
    tries = len(user_assignments)

    if user_assignments:
        user_assignment = user_assignments[-1]
        tries = user_assignment.tries
    else:
        user_assignment = ''

    # get all options for each question
    for question in questions:
        options = question.options
        options_dict[str(question.id)] = options

    if current_user.id == course.teacher_id and request.method == "POST" and delete:
        course_assignments = Assignment.query.filter_by(course_id=course.id).all()
        course_users = Course_User.query.filter_by(course_id=course.id).all()
        total_assignment_points = 0

        # get the total point count for assignments in course
        for course_assignment in course_assignments:
            total_assignment_points += course_assignment.points

        # for every user in the course delete assignments that
        # they turned in for this assignment & reflect the change
        # to their grade
        for course_user in course_users:
            turned_in_assignments = User_Assignment.query.filter_by(user_id=course_user.user_id, assignment_id=assignment.id).all()

            if turned_in_assignments:
                turned_in_assignments.sort(key=lambda a:a.created_time)
                student_assignment = turned_in_assignments[-1]

                assignments_done = json.loads(course_user.assignments_done)
                del assignments_done[str(assignment.id)]
                course_user.assignments_done = json.dumps(assignments_done)

                course_user.points -= student_assignment.points

                try:
                    leftover_points = course_user.points/(total_assignment_points - assignment.points)
                except ZeroDivisionError:
                    leftover_points = 0

                course_user.grade = '{:.2%}'.format(leftover_points)

        # deletion of assignments cascades to questions, options and user_assignments
        db.session.delete(assignment)
        db.session.commit()

        flash('Assignment was deleted successfully!', 'success')
        return redirect(url_for("assignments", course_id=course.id))
    elif "ajax" in request_form and request.method == "POST":
        errors = {}
        for key, value in request_form.items():
            if "question_" in key and value == "":
                errors[key] = "This question requires an answer."
        return errors
    elif request.method == "POST" and current_user.profession == "Student" and tries < assignment.tries:
        course_user = Course_User.query.filter_by(user_id=current_user.id, course_id=course.id).first()
        total_assignment_points = 0
        url = ""
        answers = []
        points = 0

        for key, value in request_form.items():
            if "question_" in key:
                answers.append(value)

        for i in range(len(answers)):
            if questions[i].answer == answers[i]:
                points += questions[i].points

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

        user_assignment = User_Assignment(user_id=current_user.id,
                                        assignment_id=assignment.id,
                                        url=url,
                                        answers=answers,
                                        points=points,
                                        tries=tries+1,
                                        type=assignment.type)

        db.session.add(user_assignment)
        db.session.commit()

        flash("Assignment turned in!", "success")
        return redirect(url_for("assignment", course_id=course.id, assignment_id=assignment.id))
    elif request.method == "POST":
        flash("You can no longer redo this assignment.", "danger")
        return redirect(url_for("assignment", course_id=course.id, assignment_id=assignment.id))
    elif request.method == "GET":
        return render_template('assignment.html',
                                course=course,
                                assignment=assignment,
                                user_assignment=user_assignment,
                                questions=questions,
                                options_dict=options_dict,
                                redo=redo,
                                tries=tries,
                                title=course.title + " - " + assignment.title)

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

@app.route('/dashboard/courses/<int:course_id>/grades', methods=['GET'])
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

@app.route('/dashboard/courses/<int:course_id>/students', methods=['GET', 'POST'])
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

@app.route('/dashboard/courses/<int:course_id>/students/<int:student_id>', methods=['GET'])
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

@app.route('/dashboard/courses/<int:course_id>/students/<int:student_id>/grades', methods=['GET', 'POST'])
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

@app.route('/dashboard/courses/<int:course_id>/students/<int:student_id>/grades/edit', methods=['GET', 'POST'])
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

    if 'ajax' in request_form and request.method == "POST":
        return grades_edit_error_handler(request_form, course)
    elif request.method == "POST":

        # if user maliciously bypasses the ajax request
        errors = grades_edit_error_handler(request_form, course)
        if errors:
            flash("There was an error in updating the grades.", "danger")
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
                    user_assignment = user_assignment[-1]
                    user_assignment.points = value

                    course_user.points -= user_assignments[key]
                    course_user.points += value

                    user_assignments[key] = value
                else:
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
@app.route('/dashboard/courses/<int:course_id>/students/<int:student_id>/assignments', methods=['GET'])
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
@app.route('/dashboard/courses/<int:course_id>/students/<int:student_id>/assignments/<int:user_assignment_id>', methods=['GET'])
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
