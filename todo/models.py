# -*- coding: utf-8 -*-
# todo/models.py
import random
import re
from datetime import datetime, timedelta

from flask_login import login_user
from passlib.hash import argon2

from config import TASKS_PER_PAGE
from todo import db

random.seed()


class User(db.Model):
    """User class"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, index=True)
    tasks = db.relationship('Task', backref='author', lazy='dynamic', cascade='all, delete')
    opinions = db.relationship('Opinion', backref='opinion_author', lazy='dynamic')
    tasks_per_page = db.Column(db.Integer)
    page = db.Column(db.Integer)
    last_login = db.Column(db.DateTime)

    def __str__(self):
        return self.username

    def is_active(self):
        """logged in user always active"""
        return True

    def get_id(self):
        """Returns username as id"""
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def is_authenticated(self):
        """Returns True"""
        return True

    def is_anonymous(self):
        """always False, no anonymous users"""
        return False

    def check_user_tasks_per_page(self):
        """Check if user defined his own "tasks_per_page" value. Takes actual page, returns nothing"""

        if self.tasks_per_page is None:
            self.tasks_per_page = TASKS_PER_PAGE
            db.session.commit()

    def save_actual_page(self, page):
        """Saves actual page to database, takes page, returns nothing"""

        self.page = page
        db.session.commit()

    @staticmethod
    def check_valid_email(email):
        """Check if email address is valid and has correct length. Takes string email address, returns True/False"""

        pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if len(email) < 100 and re.match(pattern, email):
            return True
        else:
            return False

    @staticmethod
    def hash_password(new_password):
        """Hashes password using argon2. Takes password and returns hashed password"""

        password = argon2.using(rounds=4).hash(new_password)
        return password

    @staticmethod
    def check_register_data_correctness(username, password, confpass, email):
        """Checks if all fields were given and their lengths. Takes username, password, confpass and email.
        If ok returns True. Otherwise returns False."""

        if password and confpass and username and email and len(username) < 40 and len(password) < 40 and len(
                confpass) < 40 and len(email) < 100:
            return True
        else:
            return False

    @classmethod
    def check_user_existence_by_email(cls, email):
        """Takes email. Checks if exists user with given email and returns True. Otherwise returns False. """

        user = cls.query.filter_by(email=email).first()
        if user:
            return True
        else:
            return False

    @classmethod
    def handle_registration(cls, username, password, confpass, email):
        """Handle registration, takes username, password, confpass and email. Checks if password = confpass,
        hashes password, creates user, saves it to db and returns True. Otherwise returns False."""

        if password == confpass:
            password = cls.hash_password(password)
            user = cls(username=username, password=password, email=email)
            db.session.add(user)
            db.session.commit()
            return True
        else:
            return False

    @staticmethod
    def check_login_data_correctness(username, password):
        """Checks if all fields were given and their lengths. Takes username and password.
        If ok returns True. Otherwise returns False."""

        if username and password and len(username) < 40 and len(password) < 40:
            return True
        else:
            return False

    @classmethod
    def check_user_existence_by_username(cls, username):
        """Takes username. Checks if exists user with given username and returns True. Otherwise returns False. """

        user = cls.query.filter_by(username=username).first()
        if user:
            return True
        else:
            return False

    @classmethod
    def handle_login(cls, username, password, remember_me):
        """Handle logging in, takes username, password and remember_me, checks if password is correct, logs user in,
        sets last_login attribute in db and returns True. Otherwise returns False."""

        user = cls.query.filter_by(username=username).first()
        if argon2.verify(password, user.password):
            login_user(user, remember=remember_me)
            user.last_login = datetime.utcnow().replace(microsecond=0) + timedelta(hours=2)
            db.session.commit()
            return True
        else:
            return False

    def handle_email_change(self, email):
        """Takes email and username. Checks if there is no such email addres in db, if there is no
         then changes email address of given user id db and returns True. Otherwise returns False."""

        user_by_email = self.query.filter_by(email=email).first()
        if not user_by_email:
            user = User.query.filter_by(username=self.username).first()
            user.email = email
            db.session.commit()
            return True
        else:
            return False

    def handle_username_change(self, new_username):
        """Takes new_username and current_user object. Checks if there is no such username in db and correct length,
         if everything is ok then changes username of given user in db, logs user in again and returns True.
        Otherwise returns False."""

        user_by_username = User.query.filter_by(username=new_username).first()
        if not user_by_username and len(new_username) < 40:
            user = User.query.filter_by(username=self.username).first()
            tasks = Task.query.filter_by(username_id=self.id).all()
            user.username = new_username
            for i in tasks:
                i.username = new_username
            db.session.commit()
            login_user(user)
            return True
        else:
            return False

    def handle_password_change(self, password, confpass):
        """Takes password, confirm_password and current_user object. Checks if password and confirm_pass are the same
         and correct length of password, if everything is ok then hashes password, changes it in db and returns True.
        Otherwise returns False."""

        if password == confpass and len(password) < 40:
            password = User.hash_password(password)
            user = User.query.filter_by(username=self.username).first()
            user.password = password
            db.session.commit()
            return True
        else:
            return False

    def handle_tasks_per_page_change(self, tasks_per_page):
        """Takes tasks_per_page value and current_user object. Checks correct value of tasks_per_page,
         if everything is ok then changes it in db and returns True.
        Otherwise returns False."""

        if 100 > tasks_per_page > 0:
            user = User.query.filter_by(username=self.username).first()
            user.tasks_per_page = tasks_per_page
            db.session.commit()
            return True
        else:
            return False

    def handle_password_reset(self, password):
        """Takes new password and user object, hashes password using hash_password() method and saves it to db"""
        password_hashed = User.hash_password(password)
        self.password = password_hashed
        db.session.commit()

    @staticmethod
    def password_generator():
        """generates pseudo-random string consisting of letters and numbers, length 10 signs"""

        signs = "abcdefghijklmnoprstuvwxyz1234567890"
        phrase = [random.choice([sign for sign in signs]) for num in range(10)]
        random.shuffle(phrase)
        password = "".join(phrase)
        return password


class Task(db.Model):
    """Task class"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task = db.Column(db.String(255), nullable=False)
    executed = db.Column(db.SmallInteger, nullable=False)
    data_pub = db.Column(db.String(40))
    username_id = db.Column(db.Integer, db.ForeignKey("user.id"))  # user to nazwa tabeli

    def __str__(self):
        return self.task

    @staticmethod
    def get_string_date(date):
        """Changes 'date 2011-08-12T20:17:46.38" format to '2011-08-12 20:17:46.38'
        Returns date in new format or empty string if there was no date given"""

        if date:
            data_pub = " ".join(date.split('T'))
        else:
            data_pub = ""
        return data_pub

    @classmethod
    def handle_task_adding(cls, task_text, task_date, user_id):
        """Handles task adding, takes task text and date, checks if length is correct, changes date format
         using get_string_date() method, save task to db and returns True. Otherwise returns False."""
        if 255 > len(task_text) > 0:
            data_pub = cls.get_string_date(task_date)
            task = cls(task=task_text, executed=0, data_pub=data_pub, username_id=user_id)
            db.session.add(task)
            db.session.commit()
            return True
        else:
            return False

    @classmethod
    def get_all_tasks_by_username(cls, current_user, page):
        """Returns all tasks of given user with correct pagination"""
        tasks = cls.query.filter_by(username_id=current_user.id).order_by(
            Task.data_pub.desc()).paginate(page, current_user.tasks_per_page, True)
        return tasks


class Question(db.Model):
    """Poll Question class"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_text = db.Column(db.String(255), nullable=False)
    pub_date = db.Column(db.DateTime)
    choices = db.relationship('Choice', backref="Quest", lazy='dynamic')

    def __str__(self):
        return self.question_text


class Choice(db.Model):
    """Poll question choices class"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    choice_text = db.Column(db.String(100), nullable=False)
    votes = db.Column(db.Integer, server_default='0')

    def __str__(self):
        return self.choice_text

    @classmethod
    def handle_selected_choices(cls, selected_choice1, selected_choice3):
        """takes two choices, checks if are not None, saves them to db and returns True.
        If at least one of them is None then returns False"""

        if selected_choice1 and selected_choice3:
            choice1 = cls.query.filter_by(id=selected_choice1).first()
            choice1.votes += 1
            choice3 = cls.query.filter_by(id=selected_choice3).first()
            choice3.votes += 1
            db.session.commit()
            return True
        else:
            return False


class Opinion(db.Model):
    """Poll opinion class"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    opinion_text = db.Column(db.String(255))
    pub_date = db.Column(db.DateTime)
    author = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __str__(self):
        return self.opinion_text

    @classmethod
    def handle_opinion(cls, opinion_text, user_id):
        """takes opinion_text, checks if length is correct, saves it to db using given user_id and
        returns True. Otherwise returns False."""

        if len(opinion_text) < 255:
            opinion = cls(opinion_text=opinion_text, pub_date=datetime.now(), author=user_id)
            db.session.add(opinion)
            db.session.commit()
            return True
        else:
            return False


class ErrorOpinion(db.Model):
    """Poll bug report class"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    error_text = db.Column(db.String(255))
    pub_date = db.Column(db.DateTime)
    author = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __str__(self):
        return self.error_text

    @classmethod
    def handle_error_opinion(cls, error_text, user_id):
        """takes error text, checks if length is correct, saves it to db using given user_id and
         returns True. Otherwise returns False."""

        if len(error_text) < 255:
            error_opinion = cls(error_text=error_text, pub_date=datetime.now(), author=user_id)
            db.session.add(error_opinion)
            db.session.commit()
            return True
        else:
            return False
