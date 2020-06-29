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