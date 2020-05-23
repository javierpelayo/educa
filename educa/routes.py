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
from collections import OrderedDict
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
@course_auth
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
        return render_template('course.html',
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
        return render_template('course.html',
                                course=course,
                                edit_course_form=edit_course_form,
                                title="Course - " + str(course.title))

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
                                current_time=datetime.timestamp(datetime.utcnow()),
                                title=str(course.title) + " - Assignments")

@app.route('/dashboard/courses/<int:course_id>/assignments/new', methods=["GET", "POST"])
@login_required
@course_auth
@teacher_auth
def new_assignment(course_id):
    course = Course.query.filter_by(id=course_id).first()
    assignmentform = AssignmentForm()
    errors = {}

    request_form = request.form.to_dict()

    # form error handling through ajax POST request
    if 'ajax' in request_form and request.method == "POST":
        assignmentform.validate()
        for key, value in assignmentform.errors.items():
            if key == "date_input":
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
                                title=str(course.title) + "- New Assignment")

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
    questions.sort(key=lambda q: q.id)

    if user_assignments:
        user_assignments = sorted(user_assignments, key=lambda a:a.points)
        # Get the latest assignment submitted by the user
        print(user_assignments)
        user_assignment = user_assignments[-1]
    else:
        user_assignment = ''

    # get all options
    for x in range(len(questions)):
        options = Option.query.filter_by(question_id=questions[x].id).all()
        options_dict[questions[x].title] = options

    if current_user.id == course.teacher_id and request.method == "POST" and delete == "true":
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
        # error handling
        errors = {}
        for key, value in request_form.items():
            if "question_" in key and value == "":
                errors[key] = "This question requires an answer."
        return errors
    elif request.method == "POST":
        course_user = Course_User.query.filter_by(user_id=current_user.id, course_id=course.id).first()
        assignments = Assignment.query.filter_by(course_id=course.id).all()
        total_assignment_points = 0
        url = ""
        answers = []
        points = 0

        for a in assignments:
            total_assignment_points += a.points

        for key, value in request_form.items():
            if "question_" in key:
                answers.append(value)

        for i in range(len(answers)):
            if questions[i].answer == answers[i]:
                points += questions[i].points

        #
        # Update the students grade during the course
        #

        # if the student has completed assignments
        if course_user.assignments_done:
            assignments_done = json.loads(course_user.assignments_done)
        else:
            assignments_done = {}

        # if the assignment exists in the returned done assignments
        if assignment.id in assignments_done:
            if assignments_done[str(assignment.id)] < points:
                course_user.points -= assignments_done[str(assignment.id)] + points
                assignments_done[str(assignment.id)] = points
        else:
            course_user.points += points
            assignments_done[str(assignment.id)] = points

        # convert back to json for db storage
        assignments_done = json.dumps(assignments_done)
        course_user.assignments_done = assignments_done

        # update grade with any new points and assignments needed to turn in
        course_user.grade = '{:.2%}'.format(course_user.points/total_assignment_points)

        user_assignment = User_Assignment(user_id=current_user.id,
                                        assignment_id=assignment.id,
                                        url=url,
                                        answers=answers,
                                        points=points,
                                        type=assignment.type)

        db.session.add(user_assignment)
        db.session.commit()

        flash("Assignment turned in!", "success")
        return redirect(url_for("assignment", course_id=course.id, assignment_id=assignment.id))
    elif request.method == "GET" and redo:
        return render_template('assignment.html',
                                course=course,
                                assignment=assignment,
                                user_assignment=user_assignment,
                                questions=questions,
                                options_dict=options_dict,
                                redo=redo,
                                title=str(course.title) + " - " + str(assignment.title))
    elif request.method == "GET":
        print(user_assignment)
        return render_template('assignment.html',
                                course=course,
                                assignment=assignment,
                                user_assignment=user_assignment,
                                questions=questions,
                                options_dict=options_dict,
                                title=str(course.title) + " - " + str(assignment.title))

# used to gather information about
# a user for grades template rendering
def user_grades(course, user_id):
    course_user = Course_User.query.filter_by(user_id=user_id, course_id=course.id).first()

    assignments = Assignment.query.filter_by(course_id=course.id).all()
    assignments = sorted(assignments, key=lambda a:a.duedate_time)

    user_latest_assignments = []

    # OrderedDict is for the template so it renders as shown here
    user_points = OrderedDict([("Exam/Quiz", 0), ("Lab", 0), ("HW", 0), ("Instructions", 0)])
    assignment_points = OrderedDict([("Exam/Quiz", 0), ("Lab", 0), ("HW", 0), ("Instructions", 0)])

    # get all user assignments and add the points for each assignment type
    for assignment in assignments:
        user_assignments = User_Assignment.query.filter_by(user_id=user_id, assignment_id=assignment.id).all()
        if user_assignments:
            user_assignments = sorted(user_assignments, key=lambda ua:ua.created_time)
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
    students_list = []
    for student in course_students:
        user = User_Account.query.filter_by(id=student.user_id).first()
        students_list.append(user)

    if request.method == "GET":
        return render_template("students.html",
                                course=course,
                                course_students=course_students,
                                students_list=students_list,
                                title=course.title + " - Students")

@app.route('/dashboard/courses/<int:course_id>/students/<int:student_id>', methods=['GET'])
@login_required
@course_auth
def student(course_id, student_id):
    course = Course.query.filter_by(id=course_id).first()

    courses_user = Course_User.query.filter_by(user_id=student_id).all()
    assignments_user = User_Assignment.query.filter_by(user_id=student_id).all()

    user = User_Account.query.filter_by(id=student_id).first()
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
def student_grades(course_id, student_id):
    course = Course.query.filter_by(id=course_id).first()
