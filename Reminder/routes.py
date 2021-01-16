from flask import render_template, redirect, url_for
from flask.globals import request
from flask_login.utils import login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, current_user
from Reminder.models import Users, TaskToDo
from Reminder.forms import LoginForm, RegisterForm, AdTaskForm
from Reminder import app, db



@app.route('/')
def index():
    form = AdTaskForm()
    if current_user.is_authenticated:
        query = TaskToDo.query.filter_by(user_id=current_user.id)
        return render_template('index.html', form=form, tasks=query)

    return render_template('index.html', form=form)

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
                phone_nr = form.phone_nr.data

                db.session.add(Users(id=None,username=username,password=password,email=email,phone_nr=phone_nr))
                db.session.commit()

                return render_template('thanks.html')
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
        user_id=current_user.id)

        db.session.add(Task)
        db.session.commit()
        return redirect(url_for('index'))
    except:
        return 'There was a problem with adding your task!'

@app.route('/deleteTask/<int:id>')
@login_required
def deleteTask(id):
    Task = TaskToDo.query.get_or_404(id)

    try:
        db.session.delete(Task)
        db.session.commit()
        return redirect(url_for('index'))
    except:
        return 'There was a problem with deleting your task!'
