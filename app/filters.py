from app.home.routes import home_
from functools import wraps
import os

# Queries the browser to force the
# download of an updated CSS/JS file

@home_.app_template_filter()
def autoversion(filename):
    fullpath = os.path.join('./app/', filename[1:])
    timestamp = str(os.path.getmtime(fullpath))
    shortpath = fullpath[5:]
    return f"{shortpath}?v={timestamp}"
