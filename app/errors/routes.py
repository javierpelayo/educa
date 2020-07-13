from flask import Blueprint, render_template
from app import db
from app.filters import autoversion

errors = Blueprint("errors", __name__)

@errors.errorhandler(429)
def too_many_requests(e):
    return render_template("error/429.html"), 429

@errors.errorhandler(404)
def not_found_error(e):
    return render_template("error/404.html"), 404

@errors.errorhandler(500)
def interal_error(e):
    db.session.rollback()
    return render_template('error/500.html'), 500

@errors.errorhandler(413)
def request_entity_too_large(e):
    return render_template('error/413.html'), 413