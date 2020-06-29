from app import create_app, db
from flask_migrate import Migrate

app = create_app()

migrate = Migrate(app, db)

if __name__ == '__main__':
    # app.run(host= "192.168.0.104", port=9000, debug=True)
    app.run(debug=True)
