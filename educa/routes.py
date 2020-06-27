from flask import (render_template, request,
                    redirect, url_for,
                    session, logging,
                    current_app, sessions, flash,
                    jsonify, Response, send_file)                
from . import app, db, bcrypt, limiter, mail
from educa.forms import (RegistrationForm,
                        ResetPasswordRequestForm,
                        ResetPasswordForm,
                        LoginForm,
                        UpdateProfileForm,
                        NewCourseForm,
                        AddCourseForm,
                        UpdateCourseForm,
                        UpdateSyllabusForm,
                        AssignmentForm,
                        NewLectureForm,
                        NewConversationForm,
                        NewMessageForm)
from educa.models import *
from flask_login import (login_user,
                        current_user,
                        logout_user,
                        login_required)
from functools import wraps
from educa.filters import autoversion, course_auth, teacher_auth
from educa.email import send_email, send_email_confirmation, send_password_reset
from PIL import Image
from datetime import datetime
from time import time
from collections import OrderedDict
import secrets
import os
import json
import magic

# Profile Picture Functionality
def save_picture(form_picture):
    print(form_picture)
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

# Free up space
def delete_picture():
    pic = current_user.profile_image
    if pic != "default.png":
        picture_path = os.path.join(app.root_path,
                                    'static/profile_images',
                                    pic)
        os.remove(picture_path)

def save_assignment(file):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(file.filename)
    fn = random_hex + f_ext
    file_path = os.path.join(app.root_path,
                                'static/assignments',
                                fn)
    file.save(file_path)

    accepted_types = ["PDF", "PNG", "JPG", "JPEG"]
    with open(file_path, 'rb') as f:
        type = magic.from_buffer(f.read(2048))
    if any(at in type for at in accepted_types):
        return fn

    os.remove(file_path)
    return

def delete_assignment(fn):
    file_path = os.path.join(app.root_path,
                                'static/assignments',
                                fn)
    os.remove(file_path)

def calculate_grade(course_user, assignment, points):
    total_assignment_points = 0
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


def assignment_error_handler(request_form):
    errors = {}
    for key, value in request_form.items():
        if "question_" in key and value == "":
            errors[key] = "This question requires an answer."

    return errors

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

@app.context_processor
def inject_default():
    msg_notif = False
    try:
        profile_image = url_for('static', filename="profile_images/" + current_user.profile_image)
        for convo in current_user.conversations:
            if not convo.read:
                msg_notif = True
                break
    except:
        profile_image = url_for('static', filename="profile_images/default.png")

    return dict(profile_image=profile_image, msg_notif=msg_notif)

@app.errorhandler(429)
def too_many_requests(e):
    return render_template("error/429.html"), 429

@app.errorhandler(404)
def not_found_error(e):
    return render_template("error/404.html"), 404

@app.errorhandler(500)
def interal_error(e):
    db.session.rollback()
    return render_template('error/500.html'), 500

@app.errorhandler(413)
def request_entity_too_large(e):
    return render_template('error/413.html'), 413

@app.route('/download/<string:filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(app.root_path, 'static/assignments', filename)
    return send_file(file_path, as_attachment=True)

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
                    password=hashed_pw,
                    confirmed=False)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('verify_email_message', email=form.email.data))
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
            if user.confirmed:
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                # if next_page query parameter exists redirect to that page
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                return redirect(url_for('verify_email_message', email=user.email))
        else:
            error = "The email or password is incorrect."
            return render_template("login.html",
                                    title="Login",
                                    form=form,
                                    error=error)
    return render_template("login.html",
                            title="Login",
                            form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/verify_email_message/<string:email>', methods=["GET"])
def verify_email_message(email):
    if current_user.is_authenticated and current_user.confirmed:
        return redirect(url_for('dashboard'))
    if request.method == "GET":
        user = User_Account.query.filter_by(email=email).first()
        if user:
            if not user.confirmed:
                send_email_confirmation(user)
                return render_template("verify_email.html", email=email, title="Email Confirmation")
            else:
                flash("Your email has been confirmed.", "success")
                return redirect(url_for('login'))
        else:
            flash("A user with that email does not exist.", "danger")
            return redirect(url_for('login'))

@app.route('/resend_email_message/<string:email>', methods=["GET"])
def resend_email_message(email):
    if current_user.is_authenticated and current_user.confirmed:
        return redirect(url_for('dashboard'))

    # Not following DRY incase of flash message pile up
    if request.method == "GET":
        user = User_Account.query.filter_by(email=email).first()
        if user:
            if not user.confirmed:
                flash("Your email confirmation link has been resent.", "success")
                return redirect(url_for("verify_email_message", email=email))
            else:
                flash("Your email has been confirmed.", "success")
                return redirect(url_for('login'))
        else:
            flash("A user with that email does not exist.", "danger")
            return redirect(url_for('login'))


@app.route('/verify_email/<token>', methods=["GET", "POST"])
def verify_email(token):
    if current_user.is_authenticated and current_user.confirmed:
        return redirect(url_for('courses'))
    user = User_Account.verify_token(token)
    if not user:
        flash("This email verification link has expired. Please try again by logging in.", "warning")
        return redirect(url_for('login'))
    if request.method == "GET":
        user.confirmed = True
        db.session.commit()
        flash("Your email has been confirmed.", "success")
        return redirect(url_for('login'))



@app.route('/reset_password_request', methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('courses'))
    form = ResetPasswordRequestForm()
    if request.method == "POST" and form.validate_on_submit():
        user = User_Account.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset(user)
            return render_template("reset_password_message.html", email=user.email, title="Reset Password")
        else:
            flash("That user does not exist. Please register an account if you haven't.", "warning")
            return redirect(url_for("reset_password_request"))
    else:
        return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('courses'))
    user = User_Account.verify_token(token)
    if not user:
        flash("The link to reset your password has expired. Please try again.", "warning")
        return redirect(url_for('login'))
    form = ResetPasswordForm()
    if request.method == "POST" and form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash("Your password has been reset.", "success")
        return redirect(url_for('login'))
    else:
        return render_template('reset_password.html', form=form, title="Reset Password")

@app.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('courses'))


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
            if str(current_user.id) in list(course.dropped):
                flash("You were dropped from this course and can no longer join.", "warning")
                return redirect(url_for("courses"))

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

    drop = request.form.get('drop')

    if not teacher and request.method == "GET":
        return render_template('course.html',
                                course=course,
                                title="Course - " + str(course.title))

    elif not teacher and request.method == "POST" and drop:
        course_user = Course_User.query.filter_by(course_id=course.id, user_id=current_user.id).first()
        for a in current_user.assignments:
            db.session.delete(a)
        db.session.delete(course_user)
        db.session.commit()

        flash("You have dropped the course.", "success")
        return redirect(url_for("courses"))

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
    elif teacher and edit_course_form.errors:
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
    user_assignments = []

    for a in assignments:
        user_assignment = User_Assignment.query.filter_by(user_id=current_user.id, assignment_id=a.id).all()
        if user_assignment:
            user_assignment.sort(key=lambda a:a.created_time)
            user_assignments.append(user_assignment[-1])
        else:
            user_assignments.append(0)

    if request.method == "GET":
        return render_template('assignments.html',
                                course=course,
                                assignments=assignments,
                                user_assignments=user_assignments,
                                current_time=time(),
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

    if "ajax" in request_form and request.method == "POST":
        return new_assignment_error_handler(assignmentform, request_form)
    if request.method == "POST":
        errors = new_assignment_error_handler(assignmentform, request_form)
        if errors:
            flash("There was an error in creating that assignment.", "danger")
            return redirect(url_for('new_assignment', course_id=course.id))

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
        duedate_ctime = datetime.fromtimestamp(duedate_time).isoformat() + "Z"

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

# NO CSRF
@app.route('/dashboard/courses/<int:course_id>/assignments/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
@course_auth
def assignment(course_id, assignment_id):

    file = request.files.get("file")
    upload = request.form.get("upload")

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

    if request.method == "POST" and upload and assignment.type == "Instructions":
        if tries < assignment.tries:
            course_user = Course_User.query.filter_by(user_id=current_user.id, course_id=course.id).first()
            filename = save_assignment(file)

            if filename:
                calculate_grade(course_user, assignment, 0)
                for ua in user_assignments:
                    delete_assignment(ua.filename)
                    db.session.delete(ua)

                user_assignment = User_Assignment(user_id=current_user.id,
                                                assignment_id=assignment.id,
                                                filename=filename,
                                                tries=tries+1,
                                                points=0,
                                                type=assignment.type)

                db.session.add(user_assignment)
                db.session.commit()
                flash("Assignment has been successfully submitted.", "success")
                return redirect(url_for('assignment', course_id=course.id, assignment_id=assignment.id))
            else:
                flash("That file type is not allowed.", "warning")
                return redirect(url_for('assignment', course_id=course.id, assignment_id=assignment.id))
        else:
            flash("You have already reached your max tries.", "warning")
            return redirect(url_for('assignments', course_id=course.id))


        return redirect(url_for("assignment", course_id=course.id, assignment_id=assignment.id))
    elif current_user.id == course.teacher_id and request.method == "POST" and delete:
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
    if "ajax" in request_form and request.method == "POST":
        return assignment_error_handler(request_form)
    elif request.method == "POST" and current_user.profession == "Student" and tries < assignment.tries:

        errors = assignment_error_handler(request_form)
        if errors:
            flash("There was an error in submitting this assignment.", "danger")
            return redirect(url_for('assignment', course_id=course.id, assignment_id=assignment.id))

        course_user = Course_User.query.filter_by(user_id=current_user.id, course_id=course.id).first()
        total_assignment_points = 0
        answers = []
        points = 0

        for key, value in request_form.items():
            if "question_" in key:
                answers.append(value)

        for i in range(len(answers)):
            if questions[i].answer == answers[i]:
                points += questions[i].points

        if assignment.points == points:
            tries = assignment.tries
        else:
            tries += 1

        calculate_grade(course_user, assignment, points)

        user_assignment = User_Assignment(user_id=current_user.id,
                                        assignment_id=assignment.id,
                                        filename="",
                                        answers=answers,
                                        points=points,
                                        tries=tries,
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
                                current_time=time(),
                                user_assignment=user_assignment,
                                questions=questions,
                                options_dict=options_dict,
                                redo=redo,
                                tries=tries,
                                title=course.title + " - " + assignment.title)

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

@app.route('/dashboard/courses/<int:course_id>/lectures', methods=['GET', 'POST'])
@login_required
@course_auth
def lectures(course_id):
    course = Course.query.filter_by(id=course_id).first()
    lectures = Lecture.query.filter_by(course_id=course_id).all()
    lectures.sort(key=lambda l:l.created_time)

    if request.method == "GET":
        return render_template("lectures.html",
                                course=course,
                                lectures=lectures,
                                title=f"{course.title} - Lectures",
                                header=" \ Lectures")


@app.route('/dashboard/courses/<int:course_id>/lectures/new', methods=['GET', 'POST'])
@login_required
@course_auth
@teacher_auth
def new_lecture(course_id):
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
        return redirect(url_for("lectures", course_id=course.id))
    else:
        return render_template("new_lecture.html",
                                course=course,
                                form=form,
                                title=f"{course.title} - New Lecture",
                                header=" \ New Lecture")

@app.route('/dashboard/courses/<int:course_id>/lectures/<int:lecture_id>', methods=['GET', 'POST'])
@login_required
@course_auth
def lecture(course_id, lecture_id):
    course = Course.query.filter_by(id=course_id).first()
    lecture = Lecture.query.filter_by(id=lecture_id).first()

    if request.method == "GET":
        return render_template("lecture.html",
                                course=course,
                                lecture=lecture,
                                title=f"{course.title} - Lecture",
                                header=" \ " + lecture.title)

@app.route('/dashboard/deadlines', methods=['GET'])
@login_required
def deadlines():
    courses = Course_User.query.filter_by(user_id=current_user.id).all()
    user_assignments = User_Assignment.query.filter_by(user_id=current_user.id).all()
    user_assignments = [ua.id for ua in user_assignments]
    assignments_due = []
    for course in courses:
        assignments = Assignment.query.filter_by(course_id=course.course_id).order_by(Assignment.duedate_time).all()[::-1]
        for assignment in assignments:
            if assignment.id not in user_assignments:
                assignments_due.append(assignment)

    return render_template("deadlines.html",
                            assignments=assignments_due,
                            title="Deadlines")

def inbox_info():
    conversations = current_user.conversations
    conversations.sort(key=lambda c:c.conversation_id, reverse=True)
    convos = []

    if conversations:
        # fix here
        for i in range(len(conversations)):
            users = []

            for convo_user in conversations[i].conversation.conversation_users:
                users.append(convo_user.user)

            users = ", ".join([user.first_name for user in users])
            msg = Message.query.filter_by(conversation_id=conversations[i].conversation_id).order_by(Message.created_time).all()[-1]

            convos.append({"names": users, "msg": msg.content, "date": msg.created_ctime, "conversation_id": conversations[i].conversation_id, "read": conversations[i].read})

    return convos

# NO CSRF
@app.route('/dashboard/inbox', methods=['GET', 'POST'])
@login_required
def inbox():
    conversation_snippets = inbox_info()

    delete = request.form.get("delete")

    if request.method == "POST" and delete:
        request_form = request.form.to_dict()
        convos_del = [Conversation_User.query.filter_by(user_id=current_user.id, conversation_id=int(value)).first() for key, value in request_form.items() if "convo_" in key]

        for convo_user in convos_del:
            message = Message(conversation_id=convo_user.conversation_id,
                        user_id=current_user.id,
                        content=f"{current_user.first_name} {current_user.last_name} has left this conversation.",
                        msg_type="left")
            db.session.add(message)

        for convo in convos_del:
            db.session.delete(convo)

        db.session.commit()

        return redirect(url_for("inbox"))

    return render_template("conversation.html",
                            conversation_snippets=conversation_snippets,
                            title="Inbox")

def searched_users(name, course_id):
    name = name.title().split(" ")
    first_name = name[0]
    if len(name) > 1:
        last_name = name[1]
    search_match = []
    results_parsed = {}

    search_all = User_Account.query.filter(User_Account.first_name.startswith(first_name)).all()

    for user in search_all:
        if user.profession == "Student":
            search_match += [user for c in user.classes if c.course_id == int(course_id)]
        else:
            search_match += [user for c in user.courses if c.id == int(course_id)]

    for user in search_match:
        if current_user.id != user.id:
            if user.profession == "Student":
                results_parsed[f"{user.first_name} {user.last_name} #{user.id}"] = str(user.id)
            else:
                results_parsed[f"{user.first_name} {user.last_name} - Teacher"] = str(user.id)

    return results_parsed

@app.route('/dashboard/inbox/conversation/new/search', methods=['GET'])
@login_required
@limiter.exempt
def get_recipients():
    request_args = request.args.to_dict()
    if request.method == "GET":
        return searched_users(request_args['name'], request_args['course_id'])

@app.route('/dashboard/inbox/conversation/new', methods=['GET', 'POST'])
@login_required
def new_conversation():
    conversation_snippets = inbox_info()
    recipient = request.args.get("recipient_id")
    if recipient:
        recipient = User_Account.query.filter_by(id=int(recipient)).first()
    request_form = request.form.to_dict()

    if request.method == "POST":
        recipients = [{key: value} for key, value in request_form.items() if "recipient_" in key]
        form = NewConversationForm(recipients=recipients)

        if form.validate_on_submit():
            conversation = Conversation(title=form.title.data)
            db.session.add(conversation)
            db.session.commit()

            conversation_user = Conversation_User(user_id=current_user.id, conversation_id=conversation.id, read=True)

            for recipient_id in set(form.recipients.data):
                if current_user.id != int(recipient_id):
                    conversation_recipient = Conversation_User(user_id=int(recipient_id), conversation_id=conversation.id)
                    db.session.add(conversation_recipient)

            msg = Message(conversation_id=conversation.id,
                                user_id=current_user.id,
                                content=form.message.data)
            
            db.session.add(conversation_user)
            db.session.add(msg)
            db.session.commit()

            return redirect(url_for("conversation", convo_id=conversation.id))
        else:
            return redirect(url_for('new_conversation'))
    elif request.method == "GET":
        form = NewConversationForm()
        return render_template("new_conversation.html",
                            conversation_snippets=conversation_snippets,
                            recipient=recipient,
                            form=form,
                            title="New Conversation")

@app.route('/dashboard/inbox/conversation/<int:convo_id>/update', methods=['GET'])
@login_required
@limiter.exempt
def update_messages(convo_id):
    conversation = Conversation.query.filter_by(id=convo_id).first()
    messages = conversation.messages
    update_msg = []
    msg_timestamp = float(request.args.get('timestamp'))
    top = request.args.get('top')

    for msg in messages:
        if top == "true":
            if msg.created_time < msg_timestamp and len(update_msg) < 10:
                update_msg.append(msg.rendering_dict())
        else:
            if msg.created_time > msg_timestamp:
                update_msg.append(msg.rendering_dict())

    if top == "true":
        update_msg = sorted(update_msg, key= lambda d: d.get("timestamp"))
    else:
        update_msg = sorted(update_msg, key= lambda d: d.get("timestamp"), reverse=True)
    
    return json.dumps(update_msg)

@app.route('/dashboard/inbox/conversation/<int:convo_id>', methods=['GET', 'POST'])
@login_required
@limiter.exempt
def conversation(convo_id):

    user_convo = Conversation_User.query.filter_by(user_id=current_user.id, conversation_id=convo_id).first()
    user_convo.read = True
    db.session.commit()

    conversation_snippets = inbox_info()
    conversation = Conversation.query.filter_by(id=convo_id).first()

    messages = conversation.messages
    if len(messages) > 10:
        messages = messages[-10:]

    form = NewMessageForm()

    if request.method == "POST" and form.validate_on_submit():
        message = Message(conversation_id=convo_id,
                            user_id=current_user.id,
                            content=form.message.data)

        conversation_users = Conversation_User.query.filter_by(conversation_id=convo_id).all()
        for convo_user in conversation_users:
            if convo_user.user_id != current_user.id:
                convo_user.read = False

        db.session.add(message)
        db.session.commit()

        return redirect(url_for('conversation', convo_id=convo_id))
    return render_template("conversation.html",
                            conversation=conversation,
                            messages=messages,
                            conversation_snippets=conversation_snippets,
                            form=form,
                            title="Conversation")