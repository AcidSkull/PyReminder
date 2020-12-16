from Reminder import db, login_manager
from flask_login.mixins import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Users(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)

    def __init__(self,id,username,password,email):
        self.id = id
        self.username = username
        self.password = password
        self.email = email

class TaskToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(45), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    termDate = db.Column(db.String, nullable=False)
    termTime = db.Column(db.String, nullable=False)
    method = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False, foreign_key=True)
    done = db.Column(db.Boolean, nullable=False)