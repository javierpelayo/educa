from app import create_app, db
from flask_migrate import Migrate

app = create_app()
with app.app_context():
    db.create_all()

migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True)
