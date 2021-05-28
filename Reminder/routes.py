from flask import render_template, redirect, url_for, Markup
from flask.globals import request, session
from flask_login.utils import login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, current_user
from Reminder.models import Users, TaskToDo
from Reminder.forms import LoginForm, RegisterForm, AdTaskForm, ChangePassword, ChangePhoneNumber, ChangeNickname, DeleteAccount
from Reminder import app, db



@app.route('/')
def index():
    form = [AdTaskForm(), ChangePassword(), ChangePhoneNumber(), ChangeNickname(), DeleteAccount()]
    if current_user.is_authenticated:
        query = TaskToDo.query.filter_by(user_id=current_user.id)
        return render_template('index.html', form=form, tasks=query)

    return render_template('index.html')

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

                return render_template('thanks.html', message=Markup("Congratulations! <br> You succesfully registered! <br><a href=\"/\">Return to home page</a>"))
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

    if Task.user_id != int(current_user.get_id()):return redirect(url_for('index'))

    try:
        db.session.delete(Task)
        db.session.commit()
        return redirect(url_for('index'))
    except:
        return 'There was a problem with deleting your task!'

@app.route('/settings', methods=['POST'])
@login_required
def settings():
    post = request.form
    User = Users.query.get_or_404(int(current_user.get_id()))

    if 'newPassword' in post:
        if check_password_hash(User.password, post['oldPassword']):
            User.password = generate_password_hash(post['newPassword'], method='sha256')
            db.session.commit()
            return render_template('thanks.html', message='Password changed succesfully!')
        else:
            return render_template('thanks.html', message='Password is incorrect!')
    elif 'newNumber' in post:
        if User.phone_nr == post['oldNumber']:
            User.phone_nr = post['newNumber']
            db.session.commit()
            return render_template('thanks.html', message='Phone number changed succesfully!')
        else:
            return render_template('thanks.html', message='Phone number is incorrect!')
    elif 'NewUsername' in post:
        User.username = post['NewUsername']
        db.session.commit()
        return render_template('thanks.html', message='Username changed succesfully!')
    elif 'password' in post:
        if check_password_hash(User.password, post['password']):
            db.session.delete(User)
            db.session.commit()
            
        return redirect(url_for('index'))

    return redirect(url_for('index'))