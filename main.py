from flask import Flask, render_template, redirect, url_for, session, logging, requests
from wtforms import From, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

    
if __name__ == "__main__":
    app.run(debug=True)