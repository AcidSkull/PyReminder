from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, BooleanField, SubmitField, TextAreaField
from wtforms.fields.html5 import DateField, TimeField, TelField

class AdTaskForm(FlaskForm):
    title = StringField('Title', [validators.length(min=4, max=45), validators.DataRequired()])
    description = TextAreaField('Description', [validators.length(min=4, max=255), validators.DataRequired()])
    termDate = DateField('Date', [validators.DataRequired()] , format='%Y-%m-%d')
    termTime = TimeField('Time', [validators.DataRequired()], format='%H:%M:%S')

class LoginForm(FlaskForm):
    username = StringField('Login', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', [validators.length(min=4, max=25), validators.DataRequired()])
    email = StringField('Email', [validators.length(min=4, max=45), validators.DataRequired()])
    password = PasswordField('Password', [
        validators.DataRequired()
    ])
    confirm = PasswordField('Confirm password', [
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    phone_nr = TelField('Telephone number', [validators.DataRequired(), validators.length(min=12, max=12)], render_kw={'placeholder':'for eg.:+48756432543'})
    accepted_rules = BooleanField("I accpeted the terms of use",[validators.DataRequired()])
    submit = SubmitField('Sign up')

