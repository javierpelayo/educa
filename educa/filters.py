from . import app
import os

# Queries the browser to force the
# download of an updated CSS file

@app.template_filter()
def autoversion(filename):
  fullpath = os.path.join('./educa/', filename[1:])
  timestamp = str(os.path.getmtime(fullpath))
  shortpath = fullpath[7:]
  return f"{shortpath}?v={timestamp}"
