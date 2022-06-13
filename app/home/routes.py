from flask import Blueprint, render_template, url_for, redirect

home_ = Blueprint("home", __name__)

@home_.app_context_processor
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

@home_.route('/')
@home_.route('/home')
def home():
    return redirect(url_for('users.login'))

@home_.route('/about')
def about():
    return render_template("about.html", title="About")

@home_.route('/packages')
def packages():
    return render_template("packages.html", title="Packages")

from app.filters import autoversion