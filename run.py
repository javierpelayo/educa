from app import create_app, db
from flask_migrate import Migrate
import os

port = int(os.environ.get("PORT", 5000))

app = create_app()
with app.app_context():
    db.create_all()

migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
