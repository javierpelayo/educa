from flask import Blueprint, render_template

home = Blueprint("home", __name__)

@home.app_context_processor
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

@home.route('/')
@home.route('/home')
def home():
    return render_template("home.html", title="Home")

@home.route('/about')
def about():
    return render_template("about.html", title="About")

@home.route('/packages')
def packages():
    return render_template("packages.html", title="Packages")