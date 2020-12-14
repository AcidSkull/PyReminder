from flask import Flask, render_template, redirect, url_for
from flask.globals import request
from flask.helpers import flash
from flask_login.mixins import UserMixin
from flask_login.utils import login_required, logout_user
from sqlalchemy.orm import query
from wtforms import StringField, PasswordField, validators, BooleanField, SubmitField, TextAreaField
from wtforms.fields.html5 import DateField, TimeField
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, current_user
from flask_wtf import FlaskForm
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = os.urandom(16)
db = SQLAlchemy(app)

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

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class AdTaskForm(FlaskForm):
    title = StringField('Title', [validators.length(min=4, max=45), validators.DataRequired()])
    description = TextAreaField('Description', [validators.length(min=4, max=255), validators.DataRequired()])
    termDate = DateField('Date', [validators.DataRequired()] , format='%Y-%m-%d')
    termTime = TimeField('Time', [validators.DataRequired()], format='%H:%M:%S')

@app.route('/')
def index():
    form = AdTaskForm()
    if current_user.is_authenticated:
        query = TaskToDo.query.filter_by(user_id=current_user.id)
        return render_template('index.html', form=form, tasks=query)

    return render_template('index.html', form=form)

class LoginForm(FlaskForm):
    username = StringField('Login', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])



@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()

    if request.method == 'POST':
        username = form.username.data
        error = 'Bad username or password!'

        try:
            data = Users.query.filter_by(username=username).first()
            pwhash = data.password
        except:
            return render_template('login.html', form=form,error=error)
        if data is not None:
            if check_password_hash(pwhash, form.password.data):
                login_user(data)
                return redirect(url_for('index'))
        
        return render_template('login.html', form=form,error=error)

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')


class RegisterForm(FlaskForm):
    username = StringField('Username', [validators.length(min=4, max=25), validators.DataRequired()])
    email = StringField('Email', [validators.length(min=4, max=45), validators.DataRequired()])
    password = PasswordField('Password', [
        validators.DataRequired()
    ])
    confirm = PasswordField('Confirm password', [
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    accepted_rules = BooleanField("I accpeted the terms of use",[validators.DataRequired()])
    submit = SubmitField('Sign up')

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    error1 = ''
    error2 = ''

    if form.validate_on_submit():
        query = Users.query.filter_by(username=form.username.data).first()
        if query is None:
            query = Users.query.filter_by(email=form.email.data).first()
            if query is None:

                username = form.username.data
                email = form.email.data
                password = generate_password_hash(form.password.data, method='sha256')

                db.session.add(Users(id=None,username=username,password=password,email=email))
                db.session.commit()

                return redirect(url_for('thanks'))
            else:
                error2 = "Someone is already using this email addres!"
        else:
            error1 = "There is user with this nick!"

    return render_template('register.html', form=form, error1=error1, error2=error2)

@app.route('/addTask', methods=['POST'])
@login_required
def addTask():
    form = AdTaskForm(request.form)
    try:
        Task = TaskToDo(title=form.title.data, description=form.description.data, 
        termDate=form.termDate.data, termTime=form.termTime.raw_data[0],
        method=0, user_id=current_user.id, done=0)
        db.session.add(Task)
        db.session.commit()
        return redirect(url_for('index'))
    except:
        return 'There was a problem with adding your task!'

if __name__ == "__main__":
    app.run(debug=True)