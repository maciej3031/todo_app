# -*- coding: utf-8 -*-
# todo/views.py


from flask import g, render_template, flash, redirect, url_for, request
from datetime import datetime
from flask_login import login_required, current_user, login_user, logout_user
from passlib.hash import argon2
from todo import app, login_manager
from .models import User, get_db
# from .forms import TaskForm


@login_manager.user_loader
def user_loader(user_id):
    """Return user object given id"""

    return User(user_id)


@app.teardown_request
def close_db(error):
    """Closes connection with database"""

    if hasattr(g, 'db'):
        g.db.close()


@app.route('/', methods=['GET', 'POST'])
def login():
    """log in method"""

    error = None
    if request.method == 'POST':
        username = request.form['login']
        password = request.form['pass']
        if username and password:
            try:
                user = User(username)
                if argon2.verify(password, user.password):   # sprawdzamy czy login i hasło zgodne z danymi w bazie przy pomocy Argon2
                    login_user(user)
                    flash('Logged in successfully')
                    return redirect(url_for("insert"))
                else:
                    error = "Incorrect login or password"  # komunikat o błędzie
            except TypeError:
                error = "Incorrect login or password"   # komunikat o błędzie
        else:
            error = "Incorrect login or password"  # komunikat o błędzie

    return render_template('login.html', error=error)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """log out method"""

    logout_user()
    info = "logged out successfully"
    return render_template('login.html', info=info)


@app.route('/register_dir', methods=['GET', 'POST'])
def register_dir():
    return render_template('register.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Sign up method"""

    username = request.form['login']
    password = argon2.using(rounds=4).hash(request.form['pass'])       #hashowanie hasła przy pomocy Argon2
    db = get_db()
    user_data = db.execute('SELECT username FROM users WHERE username = ?', (username, )).fetchone()
    if username and password and not user_data:   # sprawdzamy czy na pewno nie ma już takiego użytkownika w bazie
        db.execute('INSERT INTO users VALUES (?,?)', (username, password))
        db.commit()
        info = "Profile was created successfully"
        return render_template('login.html', info=info)
    else:
        error = "Incorrect data or login already exists"  # komunikat o błędzie

    return render_template('register.html', error=error)


@app.route('/insert', methods=['GET', 'POST'])
@login_required
def insert():
    """Adding and displaying tasks"""

    error = None
    db = get_db()
    user = current_user     # current_user zwraca obiekt aktualnego użytkownika
    # form1 = TaskForm(request.form)
    if request.method == 'POST':
        if len(request.form['task']) > 0:
            task = request.form['task']
            executed = 0
            data_pub = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db.execute('INSERT INTO tasks VALUES (?,?,?,?,?);', (None, task, executed, data_pub, user.username))
            db.commit()
            flash('New task added.')
            return redirect(url_for('insert'))
        else:
            error = 'You cannot add empty task!'  # komunikat o błędzie

    tasks = db.execute('SELECT * FROM tasks WHERE username = ? ORDER BY data_pub DESC;', (user.username,)).fetchall()
    return render_template('tasks_list.html', tasks=tasks, error=error, nick=user.username)


@app.route('/executed', methods=['POST'])
@login_required
def executed():
    """Changing status of a task to executed """

    task_id = request.form['execute']
    db = get_db()
    db.execute("UPDATE tasks SET executed = ? WHERE id = ?", (1, task_id))
    db.commit()
    return redirect(url_for('insert'))


# @app.route('/tasks_create', methods=['POST'])
# @login_required
# def task_create():
#     """Deletes a given tasks or changes status of a task to executed"""
#
#     form1 = TaskForm(request.form)
#     if form1.validate_on_submit():
#         if form1.executed_button.data:
#             task_id = request.form['execute']
#             db = get_db()
#             db.execute("UPDATE tasks SET executed = ? WHERE id = ?", (1, task_id))
#             db.commit()
#             return redirect(url_for('insert'))
#         elif form1.erase_button.data:
#             for i in request.form.getlist('erase'):
#                 db = get_db()
#                 db.execute("DELETE FROM tasks WHERE id = ?", (i, ))
#                 db.commit()
#             return redirect(url_for('insert'))


@app.route('/erase', methods=['POST'])
@login_required
def erase():
    """Deletes a given task"""
    for i in request.form.getlist('erase'):
        db = get_db()
        db.execute("DELETE FROM tasks WHERE id = ?", (i, ))
        db.commit()
    return redirect(url_for('insert'))


@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    """Deletes account permanently"""

    user = current_user
    db = get_db()
    db.execute("DELETE FROM users WHERE username = ?", (user.username,))
    db.execute("DELETE FROM tasks WHERE username = ?", (user.username,))
    db.commit()
    logout_user()
    del user
    flash('Account was deleted permanently')
    return render_template('login.html')