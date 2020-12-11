from flask import Flask, render_template, redirect, url_for, session, logging
from flask.globals import request
from flask.helpers import flash
from flask_login.mixins import UserMixin
from wtforms import Form, StringField, PasswordField, validators, BooleanField
from passlib.hash import sha256_crypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user
from flask_bcrypt import bcrypt
from markupsafe import escape
from flask_wtf import FlaskForm
import os, sqlite3

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

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

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
        password = generate_password_hash(form.password.data, method='sha256')

        data = Users.query.filter_by(username=username,password=password)
        if data is not None:
            return redirect(url_for('index'))

    return render_template('login.html', form=form)


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

    
if __name__ == "__main__":
    app.run(debug=True)