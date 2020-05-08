from datetime import datetime
from . import db, login_manager
from flask_login import UserMixin
from educa.filters import autoversion

# gets the user from the db and logs them in/ties it with their session
@login_manager.user_loader
def load_user(user_id):
    return User_Account.query.get(int(user_id))

# Association/Join Tables
conversation_user = db.Table('conversation_user',
                    db.Column('user_id', db.Integer, db.ForeignKey('user_account.id')),
                    db.Column('conversation_id', db.Integer, db.ForeignKey('conversation.id')))

class Course_User(db.Model):
    # SQLAlchemy creates tablenames by default unless specified inside class
    __tablename__ = 'course_user'
    user_id = db.Column(db.Integer, db.ForeignKey('user_account.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), primary_key=True)
    grade = db.Column(db.Integer)
    course = db.relationship('Course', backref='users')

    def __repr__(self):
        return f"Course_User('{self.user_id}', '{self.course_id}', '{self.grade}')"

class User_Assignment(db.Model):
    __tablename__ = 'user_assignment'
    user_id = db.Column(db.Integer, db.ForeignKey('user_account.id'), primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), primary_key=True)
    url = db.Column(db.String(20))
    content = db.Column(db.Text)
    grade = db.Column(db.Integer)
    assignment = db.relationship('Assignment', backref='users')

    def __repr__(self):
        return f"User_Assignment('{self.user_id}', '{self.assignment_id}', '{self.url}', '{self.content}', '{self.grade}')"

# UserMixin adds classes used to represent users for login
# SECTION 1. User Schema
class User_Account(db.Model, UserMixin):
    __tablename__ = 'user_account'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profession = db.Column(db.String(10), nullable=False)
    biography = db.Column(db.Text)
    profile_image = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)
    messages = db.relationship('Message', backref='user')
    conversations = db.relationship('Conversation',
                        secondary=conversation_user,
                        backref='users')
    courses = db.relationship('Course', backref='teacher')
    classes = db.relationship('Course_User')
    assignments = db.relationship('User_Assignment')

    def __repr__(self):
        return f"User('{self.first_name} {self.last_name}', '{self.email}', '{self.profession}', '{self.profile_image}')"


# SECTION 2. Messaging Schema
class Conversation(db.Model):
    __tablename__ = 'conversation'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    messages = db.relationship('Message')

    def __repr__(self):
        return f"Conversation('{self.id}', '{self.title}')"

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_account.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Message('{self.id}', '{self.conversation_id}', '{self.user_id}', '{self.content}', '{self.timestamp}')"


# SECTION 3. Course Schema
class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user_account.id'))
    title = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(20), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    syllabus = db.Column(db.Text)
    assignments = db.relationship('Assignment')
    lectures = db.relationship('Lecture')

    def __repr__(self):
        return f"Course('{self.id}', '{self.teacher_id}', '{self.title}', '{self.subject}', '{self.points}')"

class Assignment(db.Model):
    __tablename__ = 'assignment'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    points = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    duedate = db.Column(db.DateTime, nullable=False)
    questions = db.relationship('Question')

    def __repr__(self):
        return f"Assignment('{self.id}', '{self.course_id}', '{self.points}', '{self.title}', '{self.content}', '{self.timestamp}')"

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'))
    title = db.Column(db.String(20), nullable=False)
    options = db.relationship('Option')

    def __repr__(self):
        return f"Question('{self.id}', '{self.assignment_id}', '{self.title}')"

class Option(db.Model):
    __tablename__ = 'option'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Option('{self.id}', '{self.question_id}', '{self.content}')"


# SECTION 4. Lectures
class Lecture(db.Model):
    __tablename__ = 'lecture'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    url = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"Lecture('{self.id}', '{self.course_id}', '{self.title}', '{self.description}', '{self.timestamp}', '{self.url}')"
