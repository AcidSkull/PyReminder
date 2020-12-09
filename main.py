from enum import unique
from flask import Flask, render_template, redirect, url_for, session, logging
from flask.globals import request
from flask.helpers import flash
from flask_login.mixins import UserMixin
from wtforms import Form, StringField, PasswordField, validators, BooleanField
from passlib.hash import sha256_crypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from markupsafe import escape
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

with open('secret.json') as f:
    data = json.load(f)

app.secret_key = data['secret_key']

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(id)

@app.route('/')
def index():
    return render_template('index.html')

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    password = db.Column(db.String(77), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)

class LoginForm(Form):
    username = StringField('Username', [validators.length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired()
    ])

class User(UserMixin,db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String)
    password = db.Column(db.String)



@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    # if form.validate_on_submit():
    #     user = User.query.get(form.username.data)



    return render_template('login.html', form=form)


class RegisterForm(Form):
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
        password = sha256_crypt.encrypt(str(form.password.data))

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