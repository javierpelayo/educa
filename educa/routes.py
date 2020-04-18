from flask import (render_template,request,
                    redirect, url_for,
                    session, logging, current_app)
from . import app, db, bcrypt
from educa.forms import RegistrationForm, LoginForm, UpdateProfileForm
from educa.models import *
from flask_login import login_user, current_user, logout_user, login_required
from functools import wraps
from educa.filters import autoversion
import secrets
from PIL import Image
import os

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
    return render_template('dashboard.html',
                            title='Dashboard')


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

courses_list = [
    {
        'title': 'Math 106',
        'subject': 'Math',
        'teacher': 'Tang Bang'
     },
     {
        'title': 'HIST B1',
        'subject': 'Humanities',
        'teacher': 'Jamal Wright'
     },
     {
        'title': 'ADMJ C1',
        'subject': 'Law',
        'teacher': 'Jack Smith'
     },
     {
        'title': 'COMP B11',
        'subject': 'CS',
        'teacher': 'Harvey Mendoza'
     },
]

@app.route('/dashboard/courses', methods=['GET', 'POST'])
@login_required
def courses():
    return render_template('courses.html',
                            courses_list=courses_list)
