# -*- coding: utf-8 -*-
# todo/views.py

from flask import g, render_template, flash, redirect, url_for, request, session
from datetime import datetime
from flask_login import login_required, current_user, login_user, logout_user
from passlib.hash import argon2
from todo import app, login_manager, db, mail
from .models import User, Task, Question, Choice, Opinion
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
    flash("logged out successfully")
    return redirect(url_for("login"))


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
                        flash("Profile was created successfully")
                        return redirect(url_for("login"))
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


@app.route('/poll', methods=['POST', 'GET'])
@login_required
def poll():
    """Voting logic"""

    question = Question.query.order_by(Question.id).all()
    if request.method == 'POST':
        selected_choice1 = request.form.get('choice1')
        opinion_text = request.form['choice2']
        selected_choice3 = request.form.get('choice3')
        error_text = request.form['choice4']

        if selected_choice1 and selected_choice3:
            choice1 = Choice.query.filter_by(id=selected_choice1).first()
            choice1.votes += 1
            choice3 = Choice.query.filter_by(id=selected_choice3).first()
            choice3.votes += 1
            db.session.commit()
        else:
            error = "You did not select a choice in all questions."
            return render_template('results.html', error=error, question=question)
        if opinion_text or error_text:
            opinion = Opinion(opinion_text=opinion_text, error_text=error_text, pub_date=datetime.now())
            db.session.add(opinion)
            db.session.commit()
        return redirect(url_for('results'))
    else:
        return render_template('poll.html', question=question)


@app.route('/results', methods=['GET'])
@login_required
def results():
    """Shows results template"""
    question = Question.query.order_by(Question.id).all()
    return render_template('results.html', question=question)


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


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Changing profile data"""

    info = None
    if request.method == 'POST':
        username = request.form['login']
        password = request.form['password']
        confpass = request.form['password2']
        email = request.form['email']

        pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if email:
            if re.match(pattern, email):        # sprawdzenie poprawności maila
                email_data = User.query.filter_by(email=email).first()
                if not email_data:
                    user = User.query.filter_by(username=g.user.username).first()
                    user.email = email
                    db.session.commit()
                    info = 'Changes were saved'
                else:
                    error = "email address already exists"  # komunikat o błędzie
                    return render_template('settings.html', error=error)
            else:
                error = "incorrect email address"
                return render_template('settings.html', error=error)

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
                error = "login already exists"  # komunikat o błędzie
                return render_template('settings.html', error=error)

        if password or confpass:
            if password == confpass:        # sprawdzenie zgodonści podanych haseł
                password = argon2.using(rounds=4).hash(password)    # hashowanie hasła przy pomocy Argon2
                user = User.query.filter_by(username=g.user.username).first()
                user.password = password
                db.session.commit()
                info = 'Changes were saved'
            else:
                error = "Passwords do not match"  # komunikat o błędzie
                return render_template('settings.html', error=error)
        if info:
            flash(info)
        return redirect(url_for('settings'))

    return render_template('settings.html')


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
    return redirect(url_for("login"))


@app.route('/password_reset', methods=['GET', 'POST'])
def password_reset():
    """Resets password"""

    error = None

    def password_generator():
        x = random.randint(4, 6)
        y = random.randint(2, 3)
        word = [random.choice([i for i in letters]) for i in range(x)]
        num = [random.choice([i for i in numbers]) for i in range(y)]
        lista = word + num
        random.shuffle(lista)
        password = "".join(lista)
        return password

    if request.method == "POST":
        email = request.form['email']
        letters = "abcdefghijklmnoprstuvwxyz"
        numbers = "1234567890"
        user = User.query.filter_by(email=email).first()
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
                return redirect(url_for("login"))
            except Exception:
                error = "There was a problem with You email address. It looks like it doesn't exist or something..."
        else:
            error = "No user with given email address or address is wrong!"

    return render_template('remind_password.html', error=error)