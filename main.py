from flask import Flask, render_template, redirect, url_for
from flask.globals import request
from flask.helpers import flash
from flask_login.mixins import UserMixin
from flask_login.utils import login_required, logout_user
from wtforms import StringField, PasswordField, validators, BooleanField
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
    title = StringField('Title', [validators.length(min=4, max=45)])
    description = StringField('Description', [validators.length(min=4, max=255)])
    termDate = DateField('Date', format='%Y-%m-%d')
    termTime = TimeField('Time', format='%H:%M:%S')

@app.route('/')
def index():
    form = AdTaskForm()
    return render_template('index.html', form=form)

class LoginForm(FlaskForm):
    username = StringField('Login')
    password = PasswordField('Password', [
        validators.DataRequired()
    ])



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


class RegisterForm(FlaskForm):
    username = StringField('Username', [validators.length(min=4, max=25)])
    email = StringField('Email', [validators.length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm password')
    accepted_rules = BooleanField("I accpeted the terms of use",[validators.DataRequired()])

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        password = generate_password_hash(form.password.data, method='sha256')

        user = Users(username=username,password=password,email=email)

        did_user_exist = Users.query.filter_by(email=email).first()
        if did_user_exist:
            flash('Email addres already exist!')
            return render_template('register.html', form=form)


        db.session.add(user)
        db.session.commit()

        return render_template('thanks.html')

    return render_template('register.html', form=form)

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