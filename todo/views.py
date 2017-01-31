# -*- coding: utf-8 -*-
# todo/views.py

from flask import g, render_template, flash, redirect, url_for, request, session
from datetime import datetime
from flask_login import login_required, current_user, login_user, logout_user
from passlib.hash import argon2
from todo import app, login_manager, db, mail
from .models import User, Task
from flask_mail import Message
import re
import random
random.seed()

@login_manager.user_loader
def user_loader(user_id):
    """Return user object given id"""

    return User.query.get(user_id)


@app.before_request
def before_request():
    g.user = current_user


@app.route('/', methods=['GET', 'POST'])
def login():
    """login method"""

    error = None
    if request.method == 'POST':
        username = request.form['login']
        password = request.form['password']
        remember_me = request.form.get('rememberme') # musi być .get aby, gdyż metoda POST przesyla dane tylko wtedy kiedy checkbox jest zaznaczony
        if username and password:
            user = User.query.filter_by(username=username).first()
            if user:
                if argon2.verify(password, user.password):   # sprawdzamy czy login i hasło zgodne z danymi w bazie przy pomocy Argon2
                    login_user(user, remember=remember_me)
                    flash('Logged in successfully')
                    return redirect(url_for("user", username=g.user.username))
                else:
                    error = "Incorrect password"  # komunikat o błędzie
            else:
                error = "No such user"  # komunikat o błędzie
        else:
            error = "Incorrect login or password"  # komunikat o błędzie

    return render_template('login.html', error=error)


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    """log out method"""

    logout_user()
    info = "logged out successfully"
    return render_template('login.html', info=info)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Sign up method"""

    error = None
    if request.method == 'POST':
        username = request.form['login']
        password = request.form['password']
        confpass = request.form['password2']
        email = request.form['email']
        if password and confpass and username and email:       # sprawdzenie czy podano zarówno login, mail jak i hasło
            pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
            if re.match(pattern, email):        # sprawdzenie poprawności maila
                user_data = User.query.filter_by(username=username).first()
                email_data = User.query.filter_by(email=email).first()
                if not user_data and not email_data:     # sprawdzamy czy na pewno nie ma już takiego użytkownika w bazie
                    if password == confpass:        # sprawdzenie zgodonści podanych haseł
                        password = argon2.using(rounds=4).hash(password)    # hashowanie hasła przy pomocy Argon2
                        user = User(username=username, password=password, email=email)
                        db.session.add(user)
                        db.session.commit()
                        info = "Profile was created successfully"
                        return render_template('login.html', info=info)
                    else:
                        error = "Passwords do not match"  # komunikat o błędzie
                else:
                    error = "Login or email already exists"  # komunikat o błędzie
            else:
                error = "Incorrect email address"  # komunikat o błędzie
        else:
            error = "Incorrect data"  # komunikat o błędzie

    return render_template('register.html', error=error)


@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    """Adding and displaying tasks"""

    error = None
    if request.method == 'POST':
        task_text = request.form['task']
        task_date = request.form['date']
        if len(task_text) > 0:
            executed = 0
            if task_date:
                data_pub = " ".join(str(task_date).split('T'))
            else:
                data_pub = ""
            task = Task(task=task_text, executed=executed, data_pub=data_pub, username=g.user.username)
            db.session.add(task)
            db.session.commit()
            flash('New task added.')
            return redirect(url_for('user', username=g.user.username))
        else:
            error = 'You cannot add empty task!'  # komunikat o błędzie

    tasks = Task.query.filter_by(username=g.user.username).order_by(Task.data_pub.desc()).all()
    return render_template('tasks_list.html', tasks=tasks, error=error)


@app.route('/executed', methods=['POST'])
@login_required
def executed():
    """Changing status of a task to executed """

    task_id = request.form['execute']
    task = Task.query.filter_by(id=task_id).first()
    task.executed = 1
    db.session.commit()
    return redirect(url_for('user', username=g.user.username))


@app.route('/erase', methods=['POST'])
@login_required
def erase():
    """Deletes a given task"""

    for i in request.form.getlist('erase'):
        task = Task.query.filter_by(id=i).first()
        db.session.delete(task)
        db.session.commit()
    flash('Tasks deleted!')
    return redirect(url_for('user', username=g.user.username))


@app.route('/settings', methods=['GET'])
@login_required
def settings():
    """Renders settings page"""

    return render_template('settings.html')


@app.route('/change_profile_data', methods=['GET', 'POST'])
@login_required
def change_profile_data():
    """Sign up method"""

    error = None
    info = None
    if request.method == 'POST':
        username = request.form['login']
        password = request.form['password']
        confpass = request.form['password2']
        email = request.form['email']

        pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if email and re.match(pattern, email):        # sprawdzenie poprawności maila
            email_data = User.query.filter_by(email=email).first()
            if not email_data:
                user = User.query.filter_by(username=g.user.username).first()
                user.email = email
                db.session.commit()
                info = 'Changes were saved'
            else:
                flash("email address already exists")  # komunikat o błędzie

        if username:
            user_data = User.query.filter_by(username=username).first()
            if not user_data:
                user = User.query.filter_by(username=g.user.username).first()
                tasks = Task.query.filter_by(username=g.user.username).all()
                for i in tasks:
                    i.username = username
                user.username = username
                db.session.commit()
                info = 'Changes were saved'
                login_user(user)
            else:
                flash("login already exists")  # komunikat o błędzie

        if password:
            if password == confpass:        # sprawdzenie zgodonści podanych haseł
                password = argon2.using(rounds=4).hash(password)    # hashowanie hasła przy pomocy Argon2
                user = User.query.filter_by(username=g.user.username).first()
                user.password = password
                db.session.commit()
                info = 'Changes were saved'
            else:
                flash("Passwords do not match")  # komunikat o błędzie

    return render_template('settings.html', info=info, error=error)


@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    """Deletes account permanently"""

    tasks = Task.query.filter_by(username=g.user.username).all()
    for i in tasks:
        db.session.delete(i)
    user = User.query.filter_by(username=g.user.username).first()
    db.session.delete(user)
    db.session.commit()
    logout_user()
    flash('Account was deleted permanently')
    return render_template('login.html')


@app.route('/remind_password', methods=['GET'])
def remind_password():
    """Renders remind_password page"""

    return render_template('remind_password.html')


@app.route('/password_reset', methods=['POST'])
def password_reset():
    email = request.form['email']
    letters = "abcdefghijklmnoprstuvwxyz"
    numbers = "1234567890"

    def password_generator():
        x = random.randint(4, 6)
        y = random.randint(2, 3)
        word = [random.choice([i for i in letters]) for i in range(x)]
        num = [random.choice([i for i in numbers]) for i in range(y)]
        lista = word + num
        random.shuffle(lista)
        password = "".join(lista)
        return password

    user = User.query.filter_by(email=email).first()
    error = None
    if user:
        try:
            password = password_generator()
            password_hashed = argon2.using(rounds=4).hash(password)
            user.password = password_hashed
            db.session.commit()
            msg = Message("Reset password", sender='todoserver7@gmail.com', recipients=[user.email])
            msg.body = "Hello {}! \nYour password has been changed. New password: {}. We recommend to change it" \
                       " immediately. \n\nRegards, \ntodo team!".format(user.username, password)
            mail.send(msg)
            flash('New password has been sent to given email address!')
        except Exception:
            error = "There was a problem with You email address. It looks like it doesn't exist or something..."
    else:
        error = "No user with given email address!"
    return render_template('login.html', error=error)