# -*- coding: utf-8 -*-
# todo/views.py

from flask import g, render_template, flash, redirect, url_for, request, abort
from flask_login import login_required, current_user, logout_user
from flask_mail import Message

from config import MAIL_USERNAME
from todo import app, login_manager, db, mail
from .messages import *
from .models import User, Task, Question, Choice, Opinion, ErrorOpinion


@login_manager.user_loader
def user_loader(user_id):
    """Returns user object given id"""

    return User.query.get(user_id)  # zwraca obiekt klasy User o podanym id


@app.before_request
def before_request():
    g.user = current_user  # zapisanie aktualnego użytkownika do globalnego obiektu przed każdym requestem


@app.route('/', methods=['GET', 'POST'])
def login():
    """login method"""

    if request.method == 'POST':
        username = request.form['login']
        password = request.form['password']
        # poniżej musi być .get aby, gdyż metoda POST przesyla dane tylko wtedy kiedy checkbox jest zaznaczony
        remember_me = request.form.get('rememberme')

        if not User.check_login_data_correctness(username, password):
            error = LoginMessages.incorrect_data_error_message
            return render_template('login.html', error=error)

        if not User.check_user_existence_by_username(username):
            error = LoginMessages.no_user_error_message
            return render_template('login.html', error=error)

        if User.handle_login(username, password, remember_me):
            flash(LoginMessages.success_message)
            return redirect(url_for("user", username=g.user.username))
        else:
            error = LoginMessages.incorrect_password_error_message
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    """log out method"""

    logout_user()
    flash(LogoutMessages.success_message)
    return redirect(url_for("login"))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Sign up method"""

    if request.method == 'POST':
        username = request.form['login']
        password = request.form['password']
        confpass = request.form['password2']
        email = request.form['email']

        if not User.check_register_data_correctness(username, password, confpass, email):
            error = RegisterMessages.incorrect_data_error_message
            return render_template('register.html', error=error)

        if not User.check_valid_email(email):  # sprawdzenie poprawności maila
            error = RegisterMessages.incorrect_email_error_message
            return render_template('register.html', error=error)

        if User.check_user_existence_by_username(username) or User.check_user_existence_by_email(email):
            error = RegisterMessages.already_exist_error_message
            return render_template('register.html', error=error)

        if User.handle_registration(username, password, confpass, email):
            flash(RegisterMessages.success_message)
            return redirect(url_for("login"))
        else:
            error = RegisterMessages.incorrect_passwords_error_message
            return render_template('register.html', error=error)

    return render_template('register.html')


@app.route('/user/<username>', methods=['GET', 'POST'])
@app.route('/user/<username>/<int:page>', methods=['GET', 'POST'])
@login_required
def user(username, page=1):
    """Adds and displays tasks"""

    g.user.check_user_tasks_per_page()
    g.user.save_actual_page(page)
    error = None
    if request.method == 'POST':
        task_text = request.form['task']
        task_date = request.form['date']
        if Task.handle_task_adding(task_text, task_date, g.user.id):
            flash(UserMessages.success_message)
            return redirect(url_for('user', username=g.user.username))
        else:
            error = UserMessages.error_message
    if username == g.user.username:
        tasks = Task.get_all_tasks_by_username(g.user, page)
        return render_template('tasks_list.html', tasks=tasks, error=error)
    else:
        return abort(404)


@app.route('/poll', methods=['POST', 'GET'])
@login_required
def poll():
    """Vote logic"""

    question = Question.query.order_by(Question.id).all()
    if request.method == 'POST':
        selected_choice1 = request.form.get('choice1')
        opinion_text = request.form['choice2']
        selected_choice3 = request.form.get('choice3')
        error_text = request.form['choice4']

        if not Choice.handle_selected_choices(selected_choice1, selected_choice3):
            error = PollMessages.no_choices_error_message
            return render_template('results.html', error=error, question=question)

        if opinion_text:
            if not Opinion.handle_opinion(opinion_text, g.user.id):
                error = PollMessages.mex_length_error_message
                return render_template('results.html', error=error, question=question)

        if error_text:
            if not ErrorOpinion.handle_error_opinion(error_text, g.user.id):
                error = PollMessages.mex_length_error_message
                return render_template('results.html', error=error, question=question)

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
    """Changes status of a task to executed """

    task_id = request.form['execute']
    task = Task.query.filter_by(id=task_id).first()
    task.executed = 1
    db.session.commit()
    page = g.user.page
    flash(ExecutedMessages.success_message)
    return redirect(url_for('user', username=g.user.username, page=page))


@app.route('/undo', methods=['POST'])
@login_required
def undo():
    """Changes status of a task back to not executed """

    task_id = request.form['undo']
    task = Task.query.filter_by(id=task_id).first()
    task.executed = 0
    db.session.commit()
    page = g.user.page
    flash(UndoMessages.success_message)
    return redirect(url_for('user', username=g.user.username, page=page))


@app.route('/erase', methods=['POST'])
@login_required
def erase():
    """Deletes a given task"""

    for task_id in request.form.getlist('erase'):
        task = Task.query.filter_by(id=task_id).first()
        db.session.delete(task)
        db.session.commit()
    page = g.user.page
    flash(EraseMessages.success_message)
    return redirect(url_for('user', username=g.user.username, page=page))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Changes profile data"""

    if request.method == 'POST':
        username = request.form['login']
        password = request.form['password']
        confpass = request.form['password2']
        email = request.form['email']

        if email:
            if User.check_valid_email(email):
                if not g.user.handle_email_change(email):
                    error = SettingsMessages.email_exists_error_message
                    return render_template('settings.html', error=error)
            else:
                error = SettingsMessages.incorrect_email_error_message
                return render_template('settings.html', error=error)

        if username:
            if not g.user.handle_username_change(username):
                error = SettingsMessages.incorrect_login_data_error_message
                return render_template('settings.html', error=error)

        if password or confpass:
            if not g.user.handle_password_change(password, confpass):
                error = SettingsMessages.incorrect_password_data_error_message
                return render_template('settings.html', error=error)

        flash(SettingsMessages.success_message)
        return redirect(url_for('settings'))

    return render_template('settings.html')


@app.route('/app_settings', methods=['POST'])
@login_required
def app_settings():
    """Changes app settings"""

    if request.method == 'POST':
        tasks_per_page = request.form['tasks_per_page']
        try:
            tasks_per_page = int(tasks_per_page)
            if g.user.handle_tasks_per_page_change(tasks_per_page):
                flash(AppSettingsMessages.success_message.format(tasks_per_page))
            else:
                error = AppSettingsMessages.incorrect_value_error_message
                return render_template('settings.html', error=error)
        except ValueError:
            error = AppSettingsMessages.incorrect_number_error_message
            return render_template('settings.html', error=error)

    return redirect(url_for('settings'))


@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    """Deletes account permanently"""

    tasks = Task.query.filter_by(username_id=g.user.id).all()
    # usuwamy wszystkie taski, co prawda cascade='all, delete' w modelu User załatwia sprawę, ale dla pewności
    for task in tasks:
        db.session.delete(task)
    user = User.query.filter_by(username=g.user.username).first()
    db.session.delete(user)
    db.session.commit()
    logout_user()
    flash(DeleteAccountMessages.success_message)
    return redirect(url_for("login"))


@app.route('/password_reset', methods=['GET', 'POST'])
def password_reset():
    """Resets password"""

    error = None

    if request.method == "POST":
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            try:
                password = User.password_generator()
                msg = Message(PasswordResetMessages.title_of_message, sender=MAIL_USERNAME, recipients=[user.email])
                msg.body = PasswordResetMessages.body_of_message.format(user.username, password)
                mail.send(msg)
                user.handle_password_reset(password)
                flash(PasswordResetMessages.success_message)
                return redirect(url_for("login"))
            except Exception:
                error = PasswordResetMessages.unidentified_error_message
        else:
            error = PasswordResetMessages.no_user_error_message

    return render_template('remind_password.html', error=error)
