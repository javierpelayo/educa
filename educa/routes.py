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
from educa.filters import autoversion
import secrets
from PIL import Image
from datetime import datetime
import os
import json

# ERROR ROUTES

@app.errorhandler(429)
def too_many_requests(e):
    return render_template("error/429.html"), 429

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
    output_size = (100,100)
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
    if request.method == 'GET' and edit == "true":
        print("test1")
        fullname = current_user.first_name + " " + current_user.last_name
        form.fullname.data = fullname
        form.email.data = current_user.email
        form.biography.data = current_user.biography
        return render_template('profile.html',
                                title='Profile',
                                profile_image=profile_image,
                                form=form,
                                edit=edit)
    # If request is a 'POST' & form.val...
    elif form.validate_on_submit():
        if form.removepic.data == False and form.picture.data:
            delete_picture()
            picture_file = save_picture(form.picture.data)
            current_user.profile_image = picture_file
        elif form.removepic.data == True:
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
                                form=form,
                                edit="true")
    # elif request.method != 'POST'
    else:
        return render_template('profile.html',
                                title='Profile',
                                profile_image=profile_image)

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

    # For Students
    add_course = AddCourseForm()
    # For Teachers
    new_course = NewCourseForm()

    # POST
    if new_course.validate_on_submit():
        course = Course(teacher_id=current_user.id,
                        title=new_course.title.data,
                        subject=new_course.subject.data,
                        points=new_course.points.data)
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('courses'))
    elif add_course.validate_on_submit():
        course = Course.query.filter_by(id=add_course.id.data).first()
        if course:
            course_user = Course_User(user_id=current_user.id,
                                    course_id=add_course.id.data)
            db.session.add(course_user)
            db.session.commit()
        return redirect(url_for('courses'))
    elif request.method == "POST" and new_course.errors or add_course.errors:
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
def course(course_id):
    course = Course.query.filter_by(id=course_id).first()

    edit_course_form = UpdateCourseForm()
    syllabusform = UpdateSyllabusForm()

    if request.method == "GET":
        edit_course_form.title.data = course.title
        edit_course_form.subject.data = course.subject
        edit_course_form.points.data = course.points

    # GET - HTTP URL Queries
    edit_syllabus = request.args.get('edit')
    delete = request.form.get('delete')

    # POST - PUT HTTP Variable Headers
    syllabus = request.form.get('syllabus')
    title = request.form.get('title')
    subject = request.form.get('subject')
    points = request.form.get('points')

    # GET - edit syllabus query
    if course.teacher_id == current_user.id and request.method == "GET" and edit_syllabus == "true":
        syllabusform.syllabus.data = course.syllabus
        return render_template('course_about.html',
                                course=course,
                                syllabusform=syllabusform,
                                edit=edit_syllabus,
                                edit_course_form=edit_course_form,
                                title="Course - " + str(course.title))
    # POST - DELETE - delete course query
    elif course.teacher_id == current_user.id and request.method == "POST" and delete == "true":
        db.session.delete(course)
        db.session.commit()

        flash("Course deletion was successful!", "success")
        return redirect(url_for('courses'))
    # POST - PUT - Update syllabus
    elif course.teacher_id == current_user.id and syllabusform.validate_on_submit() and syllabus:
        course.syllabus = syllabusform.syllabus.data
        db.session.commit()
        flash("Syllabus was updated successfully!", "success")
        return redirect(url_for('course', course_id=course.id))
    # POST - PUT - UPDATE course information
    elif (course.teacher_id == current_user.id and
            edit_course_form.validate_on_submit() and
            title and subject and points):
        course.title = edit_course_form.title.data
        course.subject = edit_course_form.subject.data
        course.points = edit_course_form.points.data
        db.session.commit()

        flash("Course was updated successfully!", "success")
        return redirect(url_for('course', course_id=course.id))
    elif edit_course_form.errors:

        flash("Course could not be updated! Please check the form again.", "warning")
        return redirect(url_for('course', course_id=course.id))
    # GET
    else:
        return render_template('course_about.html',
                                course=course,
                                edit_course_form=edit_course_form,
                                title="Course - " + str(course.title))

# Convert duedate to timestamp for easier sorting
def to_timestamp_sort(model_objects):
    for i in range(len(model_objects)):
        model_objects[i].duedate = datetime.timestamp(model_objects[i].duedate)

    model_objects.sort(key=lambda a:a.duedate)

    return model_objects

@app.route('/dashboard/courses/<int:course_id>/assignments', methods=['GET'])
@login_required
def assignments(course_id):
    course = Course.query.filter_by(id=course_id).first()
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    a_ts_duedate = []

    assignments = to_timestamp_sort(assignments)

    # Put assignments duedate timestamp in a list - used to check for late assignments
    # and convert duedate back to a readable format
    for i in range(len(assignments)):
        a_ts_duedate.append(assignments[i].duedate)
        assignments[i].duedate = datetime.fromtimestamp(assignments[i].duedate).strftime("%b %d %Y %I:%M %p %Z")

    if request.method == "GET":
        return render_template('assignments.html',
                                course=course,
                                assignments=assignments,
                                current_time=datetime.timestamp(datetime.utcnow()),
                                a_ts_duedate=a_ts_duedate,
                                title=str(course.title) + " - Assignments")

@app.route('/dashboard/courses/<int:course_id>/assignments/new', methods=["GET", "POST"])
@login_required
def new_assignment(course_id):
    course = Course.query.filter_by(id=course_id).first()
    assignmentform = AssignmentForm()
    errors = {}

    # Course Teacher Authentication
    if current_user.id is not course.teacher_id:
        return redirect(url_for('assignments', course_id=course_id))

    request_form = request.form.to_dict()

    # form error handling through ajax POST request
    if 'ajax' in request_form and request.method == "POST":
        assignmentform.validate()
        for key, value in assignmentform.errors.items():
            if key == "dateInput":
                errors[key] = "Not a valid date value. ex: 01/25/2020"
            else:
                errors[key] = value[0];

        for key, value in request_form.items():
            if "qOption_" in key and value == "":
                errors[key] = "This field is required."
            elif "question_points" in key:
                try:
                    int(value)
                except ValueError:
                    errors[key] = "Not a valid integer value."
            elif "question_answer" not in key and "question_" in key and value == "":
                errors[key] = "This field is required."
        return errors

    if request.method == "POST":
        questions = {}
        options = {}
        q_ids = []
        question_option_ids = []
        question_amt = 0

        # GET ASSIGNMENT QUESTIONS/OPTIONS

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

            # creating list of key value tuples [(q_key, o_value)]
            question_option_ids.append((q_id, o_id))

        q_ids.sort()
        question_amt = len(q_ids)

        # CREATE ASSIGNMENT/QUESTIONS/OPTIONS

        dateInput = assignmentform.dateInput.data.strftime('%m/%d/%Y').split("/")
        hour = int(assignmentform.hour.data)
        minute = int(assignmentform.minute.data)
        month = int(dateInput[0])
        day = int(dateInput[1])
        year = int(dateInput[2])
        date_time = datetime(year, month, day, hour, minute)

        assignment = Assignment(course_id=course.id,
                                points=assignmentform.points.data,
                                title=assignmentform.title.data,
                                content=assignmentform.content.data,
                                type=assignmentform.type.data,
                                duedate=date_time)
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
                                title=str(course.title) + "- New Assignment")

@app.route('/dashboard/courses/<int:course_id>/assignments/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def assignment(course_id, assignment_id):

    delete = request.form.get("delete")
    request_form = request.form.to_dict()
    course = Course.query.filter_by(id=course_id).first()
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    user_assignments = User_Assignment.query.filter_by(user_id=current_user.id, assignment_id=assignment.id).all()
    questions = Question.query.filter_by(assignment_id=assignment.id).all()
    options_dict = {}

    # Make assignment due date readable
    assignment.duedate = assignment.duedate.strftime("%b %d %Y %I:%M %p %Z")

    if user_assignments:
        done = True
        user_assignments = to_timestamp_sort(user_assignments)
        # Get the latest assignment submitted by the user
        user_assignment = user_assignments[0]
    else:
        user_assignment = ""
        done = False

    # get all options
    for x in range(len(questions)):
        options = Option.query.filter_by(question_id=questions[x].id).all()
        options_dict[questions[x].title] = options

    if current_user.id == course.teacher_id and request.method == "POST" and delete == "true":
        print("delete")
        db.session.delete(assignment)
        for question in questions:
            db.session.delete(question)
        for question, options in options_dict.items():
            for option in options:
                db.session.delete(option)
        db.session.commit()

        flash('Assignment was deleted successfully!', 'success')
        return redirect(url_for("assignments", course_id=course.id))
    elif "ajax" in request_form and request.method == "POST":
        print("ajax")
        # error handling
        errors = {}
        for key, value in request_form.items():
            if "question_" in key and value == "":
                errors[key] = "This question requires an answer."
        print(errors)
        return errors
    elif request.method == "POST":
        print(request_form)
        return redirect(url_for("assignment", course_id=course.id, assignment_id=assignment.id))
    elif request.method == "GET":
        return render_template('assignment.html',
                                course=course,
                                assignment=assignment,
                                user_assignment=user_assignment,
                                questions=questions,
                                options_dict=options_dict,
                                done=done,
                                title=str(course.title) + " - " + str(assignment.title))
