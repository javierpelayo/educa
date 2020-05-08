from flask import (render_template, request,
                    redirect, url_for,
                    session, logging,
                    current_app, sessions)
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

    edit_course = UpdateCourseForm()
    syllabusform = UpdateSyllabusForm()

    if request.method == "GET":
        edit_course.title.data = course.title
        edit_course.subject.data = course.subject
        edit_course.points.data = course.points

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
                                edit_course=edit_course,
                                title="Course - " + str(course.title))
    # POST - DELETE - delete course query
    elif course.teacher_id == current_user.id and request.method == "POST" and delete == "true":
        db.session.delete(course)
        db.session.commit()
        return redirect(url_for('courses'))
    # POST - PUT - Update syllabus
    elif course.teacher_id == current_user.id and syllabusform.validate_on_submit() and syllabus:
        course.syllabus = syllabusform.syllabus.data
        db.session.commit()
        return redirect(url_for('course', course_id=course.id))
    # POST - PUT - UPDATE course information
    elif (course.teacher_id == current_user.id and
            edit_course.validate_on_submit() and
            title and subject and points):
        course.title = edit_course.title.data
        course.subject = edit_course.subject.data
        course.points = edit_course.points.data
        db.session.commit()
        return redirect(url_for('course', course_id=course.id))
    elif edit_course.errors:
        return redirect(url_for('course', course_id=course.id))
    # GET
    else:
        return render_template('course_about.html',
                                course=course,
                                edit_course=edit_course,
                                title="Course - " + str(course.title))

@app.route('/dashboard/courses/<int:course_id>/assignments', methods=['GET', 'POST'])
@login_required
def assignments(course_id):
    course = Course.query.filter_by(id=course_id).first()
    edit_course = UpdateCourseForm()
    assignmentform = AssignmentForm()

    if request.method == "GET":
        edit_course.title.data = course.title
        edit_course.subject.data = course.subject
        edit_course.points.data = course.points

    if request.method == "POST" and assignmentform.validate_on_submit():
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
                                duedate=date_time)
        db.session.add(assignment)
        db.session.commit()

        return redirect(url_for('course', course_id=course.id))
    elif assignmentform.errors:
        print(assignmentform.errors)
    return render_template('assignments.html',
                            course=course,
                            edit_course=edit_course,
                            assignmentform=assignmentform)
