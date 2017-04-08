# -*- coding: utf-8 -*-
import unittest
from todo import app, db
from config import basedir
from todo.models import User, Task, Question, Choice, Opinion, ErrorOpinion
import os
from passlib.hash import argon2
from datetime import datetime
from config import TASKS_PER_PAGE


class LoginLogoutTest(unittest.TestCase):
    """Login and logout testing class"""
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test/test.db')
        self.app = app.test_client()
        db.create_all()
        password = argon2.using(rounds=4).hash("password")
        user1 = User(username='user', password=password, email="test@test.com")
        db.session.add(user1)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # Helper methods

    def login(self, username, password):
        return self.app.post('/', data=dict(login=username, password=password), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    # Tests

    def test_main_login_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_invalid_user_login_too_long_login(self):
        response = self.login("qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm", "")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Incorrect login or password.', response.data)

    def test_invalid_user_login_too_long_password(self):
        response = self.login("", "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Incorrect login or password.', response.data)

    def test_invalid_user_login_empty_login_and_password(self):
        response = self.login("", "")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Incorrect login or password.', response.data)

    def test_invalid_user_login_no_such_user(self):
        response = self.login("user1234", "password")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No such user', response.data)

    def test_invalid_user_login_incorrect_password(self):
        response = self.login("user", "pass")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Incorrect password', response.data)

    def test_valid_user_login(self):
        response = self.login('user', 'password')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logged in successfully', response.data)

    def test_valid_user_logout(self):
        self.login('user', 'password')
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'logged out successfully', response.data)


class RegisterTest(unittest.TestCase):
    """Registration testing class"""
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test/test.db')
        self.app = app.test_client()
        db.create_all()
        password = argon2.using(rounds=4).hash("password")
        user1 = User(username='user', password=password, email="test@test.com")
        db.session.add(user1)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # Helper methods

    def register(self, username, password, confpass, email):
        return self.app.post('/register', data=dict(login=username, password=password, password2=confpass, email=email),
                             follow_redirects=True)
    # Tests

    def test_valid_user_registration(self):
        response = self.register('user1', 'password1', 'password1', 'test@gmail.com')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Profile was created successfully', response.data)
        self.assertTrue(User.query.filter_by(username="user1").first())

    def test_invalid_user_registration_invalid_email(self):
        response = self.register('user1', 'password1', 'password1', 'invalidemail.com')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Incorrect email address', response.data)
        self.assertFalse(User.query.filter_by(email="invalidemail.com").first())

    def test_invalid_user_registration_duplicate_email(self):
        response = self.register('user123', 'password', 'password', 'test@test.com')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login or email already exists', response.data)
        self.assertTrue(len(User.query.filter_by(email="test@test.com").all()) == 1)

    def test_invalid_user_registration_duplicate_user(self):
        response = self.register('user', 'password', 'password', 'test@gmail.com')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login or email already exists', response.data)
        self.assertTrue(len(User.query.filter_by(username="user").all()) == 1)

    def test_invalid_user_registration_passwords_do_not_match(self):
        response = self.register('user2', 'password', 'password2', 'test@gmail.com')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Passwords do not match', response.data)

    def test_invalid_user_registration_empty_login_and_password_and_email(self):
        response = self.register("", "", "", "")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Incorrect data. Max login and password length 40 characters. Max email length 100 characters', response.data)

    def test_invalid_user_registration_too_long_login(self):
            response = self.register("qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm", "123", "123", "test22@test.com")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Incorrect data. Max login and password length 40 characters. Max email length 100 characters', response.data)

    def test_invalid_user_registration_too_long_password(self):
            response = self.register("user12321", "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm",
                                     "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm", "test22@test.com")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Incorrect data. Max login and password length 40 characters. Max email length 100 characters', response.data)

    def test_invalid_user_registration_too_long_email(self):
                response = self.register("user12321", "123", "123", """qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxc
                vbnmqwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm@qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklz
                xcvbnmqwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm.com""")
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Incorrect data. Max login and password length 40 characters. Max email length 100 characters', response.data)


class TaskOperationsTest(unittest.TestCase):
    """Task adding, executing, deleting testing class"""
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test/test.db')
        self.app = app.test_client()
        db.create_all()
        password = argon2.using(rounds=4).hash("password")
        user1 = User(username='user', password=password, email="test@test.com")
        task1 = Task(id=0, task="test task1 test", executed=False, data_pub="2017-01-19T04:00", username_id=0)
        task2 = Task(id=1, task="test task2 test", executed=False, data_pub="2017-01-19T04:00", username_id=0)
        task3 = Task(id=2, task="test task2 test", executed=True, data_pub="2017-01-19T04:00", username_id=0)
        db.session.add(user1)
        db.session.add(task1)
        db.session.add(task2)
        db.session.add(task3)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # Helper methods

    def login(self, username, password):
        return self.app.post('/', data=dict(login=username, password=password), follow_redirects=True)

    def user(self, task, date):
        return self.app.post('/user/user', data=dict(task=task, date=date), follow_redirects=True)

    def executed(self, task_id):
        return self.app.post('/executed', data=dict(execute=task_id), follow_redirects=True)

    def undo(self, task_id):
        return self.app.post('/undo', data=dict(undo=task_id), follow_redirects=True)

    def erase(self, erase):
        return self.app.post('/erase', data=dict(erase=erase), follow_redirects=True)

    # Tests

    def test_valid_insert_task(self):
        self.login('user', 'password')
        response = self.user('task1 task1 task1', "2017-01-19T04:00")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New task added.', response.data)
        self.assertTrue(Task.query.filter_by(task="task1 task1 task1").first())

    def test_valid_insert_task_with_no_date(self):
        self.login('user', 'password')
        response = self.user('task1 task1 task1', "")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New task added.', response.data)
        self.assertTrue(Task.query.filter_by(task="task1 task1 task1").first())
        task = Task.query.filter_by(task="task1 task1 task1").first()
        self.assertTrue(task.data_pub == "")

    def test_invalid_insert_empty_task(self):
        self.login('user', 'password')
        response = self.user('', '2017-01-19T04:00')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Error: Task is empty or is too long. Max length 255 characters!', response.data)
        self.assertFalse(Task.query.filter_by(task="").first())

    def test_invalid_insert_too_long_task(self):
        self.login('user', 'password')
        response = self.user('''qwertyuioplkjhgfdsazxcvbnmpoiuytrewqasdfghjklmnbvqwertyuioplkjhgfdsazxcvbnmpoiuytrewqasd
        fghjklmnbvqwertyuioplkjhgfdsazxcvbnmpoiuytrewqasdfghjklmnbvqwertyuioplkjhgfdsazxcvbnmpoiuytrewqasdfghjklmnbv
        qwertyuioplkjhgfdsazxcvbnmpoiuytrewqasdfghjklmnbvqwertyuioplkjhgfdsazxcvbnmpoiuytrewqasdfghjklmnbvqwertyuioplkj
        hgfdsazxcvbnmpoiuytrewqasdfghjklmnbvqwertyuioplkjhgfdsazxcvbnmpoiuytrewqasdfghjklmnbvqwertyuioplkjhgfdsazxcvbnm
        poiuytrewqasdfghjklmnbvqwertyuioplkjhgfdsazxcvbnmpoiuytrewqasdfghjklmnbv123''', '2017-01-19T04:00')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Error: Task is empty or is too long. Max length 255 characters!', response.data)
        self.assertFalse(Task.query.filter_by(task="").first())

    def test_valid_execute_task(self):
        self.login('user', 'password')
        response = self.executed(0)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Task.query.filter_by(id=0).first().executed)

    def test_valid_undo_task(self):
        self.login('user', 'password')
        response = self.undo(2)
        self.assertIn(b'Task changed to not executed!', response.data)
        self.assertFalse(Task.query.filter_by(id=0).first().executed)
        self.assertEqual(response.status_code, 200)

    def test_valid_erase_multi_tasks(self):
        self.login('user', 'password')
        response = self.erase([0, 1, 2])
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.query.filter_by(username_id=0).all())
        self.assertIn(b'Tasks deleted!', response.data)


class SettingsTest(unittest.TestCase):
    """Settings testing class, changing profile data, deleting account"""

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test/test.db')
        self.app = app.test_client()
        db.create_all()
        password1 = argon2.using(rounds=4).hash("password")
        user1 = User(id=0, username='user', password=password1, email="test@test.com")
        password2 = argon2.using(rounds=4).hash("password1")
        user2 = User(id=1, username='user1', password=password2, email="test@gmail.com")
        task1 = Task(id=0, task="test task1 test", executed=False, data_pub="2017-01-19T04:00", username_id=0)
        task2 = Task(id=1, task="test task2 test", executed=False, data_pub="2017-01-19T04:00", username_id=0)
        db.session.add(task1)
        db.session.add(task2)
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # Helper methods

    def login(self, username, password):
        return self.app.post('/', data=dict(login=username, password=password), follow_redirects=True)

    def delete_account(self):
        return self.app.post('/delete_account', follow_redirects=True)

    def change_profile_data(self, username, password, password2, email):
        return self.app.post('/settings', data=dict(login=username, password=password, password2=password2,
                                                    email=email), follow_redirects=True)

    # Tests

    def test_valid_delete_account(self):
        self.login('user', 'password')
        response = self.delete_account()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.query.filter_by(username_id=0).first())
        self.assertFalse(User.query.filter_by(username='user').first())
        self.assertIn(b'Account was deleted permanently', response.data)

    def test_view_settings_page(self):
        response = self.app.get('/settings', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_valid_change_all_profile_data(self):
        self.login('user', 'password')
        response = self.change_profile_data('user1234', 'password23', 'password23', 'test2@test.com')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Changes were saved', response.data)
        user = User.query.filter_by(username="user1234").first()
        password = 'password23'
        self.assertTrue(user.username == "user1234" and user.email == "test2@test.com")
        self.assertTrue(argon2.verify(password, user.password))

    def test_invalid_change_profile_data_password_do_not_match(self):
        self.login('user', 'password')
        response = self.change_profile_data('user1234', 'password23', 'password2', 'test2@test.com')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Passwords do not match or password too long. Max 40 characters', response.data)
        user = User.query.filter_by(username="user1234").first()
        self.assertFalse(argon2.verify('password23' or 'password2', user.password))

    def test_invalid_change_profile_data_login_already_exists(self):
        self.login('user', 'password')
        response = self.change_profile_data('user1', '', '', '')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login already exists or login too long. Max 40 characters', response.data)
        self.assertTrue(len(User.query.filter_by(username="user1").all()) == 1)
        self.assertTrue(len(User.query.filter_by(username="user").all()) == 1)

    def test_invalid_change_profile_data_email_already_exists(self):
        self.login('user', 'password')
        response = self.change_profile_data('', '', '', 'test@gmail.com')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'email address already exists', response.data)
        self.assertTrue(len(User.query.filter_by(email="test@gmail.com").all()) == 1)
        self.assertTrue(len(User.query.filter_by(email="test@test.com").all()) == 1)

    def test_invalid_change_profile_data_email_too_long(self):
        self.login('user', 'password')
        response = self.change_profile_data('', '', '', """qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxc
                vbnmqwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm@qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklz
                xcvbnmqwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm.com""")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Incorrect email address', response.data)

    def test_invalid_change_profile_data_login_too_long(self):
        self.login('user', 'password')
        response = self.change_profile_data('qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm', '', '', '')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login already exists or login too long. Max 40 characters', response.data)

    def test_invalid_change_profile_data_password_too_long(self):
        self.login('user', 'password')
        response = self.change_profile_data('', 'qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm',
                                            'qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm', '')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Passwords do not match or password too long. Max 40 characters', response.data)

    def test_valid_change_profile_email_changed(self):
        self.login('user', 'password')
        response = self.change_profile_data('', '', '', 'test123@gmail.com')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Changes were saved', response.data)
        self.assertTrue(User.query.filter_by(email='test123@gmail.com').first())

    def test_invalid_change_profile_email_changed(self):
        self.login('user', 'password')
        response = self.change_profile_data('', '', '', 'testil.com')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Incorrect email address', response.data)

    def test_valid_change_profile_login_changed(self):
        self.login('user', 'password')
        response = self.change_profile_data('usserr', '', '', '')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Changes were saved', response.data)
        self.assertTrue(User.query.filter_by(username='usserr').first())

    def test_valid_change_profile_password_changed(self):
        self.login('user', 'password')
        response = self.change_profile_data('', 'password23', 'password23', '')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Changes were saved', response.data)
        user = User.query.filter_by(username="user").first()
        password = 'password23'
        self.assertTrue(argon2.verify(password, user.password))


class PasswordResetTest(unittest.TestCase):
    """Password reset testing class"""

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test/test.db')
        self.app = app.test_client()
        db.create_all()
        password1 = argon2.using(rounds=4).hash("password")
        user1 = User(username='user', password=password1, email="test@test.com")
        db.session.add(user1)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # Tests

    def test_rset_password_page(self):
        response = self.app.get('/password_reset', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_valid_password_reset(self):
        response = self.app.post('/password_reset', data=dict(email='test@test.com'), follow_redirects=True)
        self.assertIn(b'New password has been sent to given email address!', response.data)
        self.assertEqual(response.status_code, 200)

    def test_invalid_password_reset(self):
        response = self.app.post('/password_reset', data=dict(email='bad-email.pl'), follow_redirects=True)
        self.assertIn(b'No user with given email address or address is wrong!', response.data)
        self.assertEqual(response.status_code, 200)


class PollTest(unittest.TestCase):
    """Poll testing class"""
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test/test.db')
        self.app = app.test_client()
        db.create_all()
        password = argon2.using(rounds=4).hash("password")
        user1 = User(id=0, username='user', password=password, email="test@test.com")
        question1 = Question(id=1, question_text='Do You like this website?', pub_date=datetime.now())
        question2 = Question(id=2, question_text='What do you like? What would You improve?', pub_date=datetime.now())
        question3 = Question(id=3, question_text='Does this website work properly?', pub_date=datetime.now())
        question4 = Question(id=4, question_text='If not then what works wrong?', pub_date=datetime.now())
        choice1 = Choice(id=1, question='Do You like this website?', choice_text='Yes', votes=0)
        choice2 = Choice(id=2, question='Do You like this website?', choice_text='No', votes=0)
        choice3 = Choice(id=3, question='Does this website work properly?', choice_text='Yes', votes=0)
        choice4 = Choice(id=4, question='Does this website work properly?', choice_text='No', votes=0)
        db.session.add(user1)
        db.session.add(question1)
        db.session.add(question2)
        db.session.add(question3)
        db.session.add(question4)
        db.session.add(choice1)
        db.session.add(choice2)
        db.session.add(choice3)
        db.session.add(choice4)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # Helper methods

    def login(self, username, password):
        return self.app.post('/', data=dict(login=username, password=password), follow_redirects=True)

    def vote(self, choice1, choice2, choice3, choice4):
        return self.app.post('/poll', data=dict(choice1=choice1, choice2=choice2, choice3=choice3, choice4=choice4),
                             follow_redirects=True)

    # Tests

    def test_poll_page(self):
        self.login('user', 'password')
        response = self.app.get('/poll', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_valid_vote_yes(self):
        self.login('user', 'password')
        response = self.vote(1, '', 3, '')
        self.assertEqual(response.status_code, 200)
        choice1 = Choice.query.filter_by(id=1).first()
        choice3 = Choice.query.filter_by(id=3).first()
        self.assertEqual(choice1.votes, 1)
        self.assertEqual(choice3.votes, 1)

    def test_valid_vote_no(self):
        self.login('user', 'password')
        response = self.vote(2, '', 4, '')
        self.assertEqual(response.status_code, 200)
        choice1 = Choice.query.filter_by(id=2).first()
        choice3 = Choice.query.filter_by(id=4).first()
        self.assertEqual(choice1.votes, 1)
        self.assertEqual(choice3.votes, 1)

    def test_valid_vote_opinion(self):
        self.login('user', 'password')
        response = self.vote(1, "It's awesome website!", 3, '')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Opinion.query.filter_by(opinion_text="It's awesome website!").first())
        self.assertTrue(Opinion.query.filter_by(opinion_text="It's awesome website!").first().author == 0)

    def test_valid_vote_error(self):
        self.login('user', 'password')
        response = self.vote(1, '', 3, "It's broken!")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ErrorOpinion.query.filter_by(error_text="It's broken!").first())
        self.assertTrue(ErrorOpinion.query.filter_by(error_text="It's broken!").first().author == 0)

    def test_valid_vote_error_and_opinion(self):
        self.login('user', 'password')
        response = self.vote(1, "It's awesome website!", 3, "It's broken!")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ErrorOpinion.query.filter_by(error_text="It's broken!").first())
        self.assertTrue(Opinion.query.filter_by(opinion_text="It's awesome website!").first())
        self.assertTrue(ErrorOpinion.query.filter_by(error_text="It's broken!").first().author == 0)
        self.assertTrue(Opinion.query.filter_by(opinion_text="It's awesome website!").first().author == 0)

    def test_invalid_vote_error_too_long(self):
        self.login('user', 'password')
        response = self.vote(1, "", 3, """It's broken!It's broken!It's broken!It's broken!It's broken!It's broken!
        It's broken!It's broken!It's broken!It's broken!It's broken!It's broken!It's broken!It's broken!It's broken!
        It's broken!It's broken!It's broken!It's broken!It's broken!It's broken!It's broken!It's broken!It's broken!
        It's broken!It's broken!It's broken!It's broken!It's broken!It's broken!It's broken!It's broken!It's broken!
        It's broken!It's broken!It's broken!It's broken!It's broken!It's broken!It's broken!It's broken!It's broken!
        It's broken!""")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Max 255 characters!", response.data)

    def test_invalid_vote_opinion_too_long(self):
        self.login('user', 'password')
        response = self.vote(1, """It's awesome website!It's awesome website!It's awesome website!
        It's awesome website!It's awesome website!It's awesome website!It's awesome website!
        It's awesome website!It's awesome website!It's awesome website!It's awesome website!
        It's awesome website!It's awesome website!It's awesome website!It's awesome website!
        It's awesome website!It's awesome website!It's awesome website!It's awesome website!
        It's awesome website!It's awesome website!It's awesome website!It's awesome website!
        It's awesome website!It's awesome website!""", 3, "")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Max 255 characters!", response.data)

    def test_invalid_vote_not_all_options_chosen_version1(self):
        self.login('user', 'password')
        response = self.vote(1, '', '', '')
        self.assertEqual(response.status_code, 200)
        choice1 = Choice.query.filter_by(id=1).first()
        self.assertEqual(choice1.votes, 0)
        self.assertIn(b"You did not select a choice in all questions.", response.data)
        self.assertFalse(Opinion.query.all())

    def test_invalid_vote_not_all_options_chosen_version2(self):
        self.login('user', 'password')
        response = self.vote('', '', 3, '')
        self.assertEqual(response.status_code, 200)
        choice1 = Choice.query.filter_by(id=3).first()
        self.assertEqual(choice1.votes, 0)
        self.assertIn(b"You did not select a choice in all questions.", response.data)
        self.assertFalse(Opinion.query.all())

    def test_invalid_vote_not_all_options_chosen_version3_with_opinion_and_error(self):
        self.login('user', 'password')
        response = self.vote(1, "It's awesome website!", '', "It's broken!")
        self.assertEqual(response.status_code, 200)
        choice1 = Choice.query.filter_by(id=1).first()
        self.assertEqual(choice1.votes, 0)
        self.assertIn(b"You did not select a choice in all questions.", response.data)
        self.assertFalse(ErrorOpinion.query.filter_by(error_text="It's broken!").first())
        self.assertFalse(Opinion.query.filter_by(opinion_text="It's awesome website!").first())
        self.assertFalse(Opinion.query.all())


class PaginationTest(unittest.TestCase):
    """Pagination testing class"""

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test/test.db')
        self.app = app.test_client()
        db.create_all()
        password1 = argon2.using(rounds=4).hash("password")
        user1 = User(id=0, username='user1', password=password1, email="test@test.com", tasks_per_page=20)
        user2 = User(id=1, username='user2', password=password1, email="test2@test.com")
        db.session.add(user1)
        db.session.add(user2)
        for i in range(15):
            task = Task(id=i, task="test task test", executed=False, data_pub="2017-01-19T04:00", username_id=0)
            db.session.add(task)
            db.session.commit()
        for i in range(15):
            j = 20+i
            task = Task(id=j, task="test task test", executed=False, data_pub="2017-01-19T04:00", username_id=1)
            db.session.add(task)
            db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # Helper methods

    def login(self, username, password):
        return self.app.post('/', data=dict(login=username, password=password), follow_redirects=True)

    def change_app_data(self, tasks_per_page):
        return self.app.post('/app_settings', data=dict(tasks_per_page=tasks_per_page), follow_redirects=True)

    # Tests

    def test_valid_tasks_per_page_change(self):
        self.login('user2', 'password')
        response = self.change_app_data('15')
        self.assertIn(b'New value: 15 tasks per page!', response.data)
        user = User.query.filter_by(username='user2').first()
        self.assertTrue(user.tasks_per_page == 15)

    def test_invalid_tasks_per_page_change_too_large_number(self):
        self.login('user2', 'password')
        response = self.change_app_data('101')
        self.assertIn(b'Invalid number! Max value 100', response.data)
        user = User.query.filter_by(username='user2').first()
        self.assertTrue(user.tasks_per_page == TASKS_PER_PAGE)

    def test_invalid_tasks_per_page_change_zero_given(self):
        self.login('user2', 'password')
        response = self.change_app_data('0')
        self.assertIn(b'Invalid number! Max value 100', response.data)
        user = User.query.filter_by(username='user2').first()
        self.assertTrue(user.tasks_per_page == TASKS_PER_PAGE)

    def test_invalid_tasks_per_page_change_not_number_given(self):
        self.login('user2', 'password')
        response = self.change_app_data('abc')
        self.assertIn(b'Invalid number!', response.data)
        user = User.query.filter_by(username='user2').first()
        self.assertTrue(user.tasks_per_page == TASKS_PER_PAGE)

    def test_pagination_number_of_pages_user_defined_number(self):
        self.login('user1', 'password')
        response1 = self.app.get('/user/user1/1')
        response2 = self.app.get('/user/user1/2')
        response3 = self.app.get('/user/user1/3')
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 404)
        self.assertEqual(response3.status_code, 404)

    def test_pagination_number_of_pages_user_undefined_number(self):
        self.login('user2', 'password')
        response1 = self.app.get('/user/user2/1')
        response2 = self.app.get('/user/user2/2')
        response3 = self.app.get('/user/user2/3')
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response3.status_code, 404)

    def test_pagination_change_user_defined_number(self):
        self.login('user1', 'password')
        self.change_app_data('5')
        response1 = self.app.get('/user/user1/1')
        response2 = self.app.get('/user/user1/2')
        response3 = self.app.get('/user/user1/3')
        response4 = self.app.get('/user/user1/4')
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response3.status_code, 200)
        self.assertEqual(response4.status_code, 404)
        user = User.query.filter_by(username="user1").first()
        self.assertEqual(user.tasks_per_page, 5)

    def test_pagination_change_user_undefined_number(self):
        self.login('user2', 'password')
        self.change_app_data('5')
        response1 = self.app.get('/user/user2/1')
        response2 = self.app.get('/user/user2/2')
        response3 = self.app.get('/user/user2/3')
        response4 = self.app.get('/user/user2/4')
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response3.status_code, 200)
        self.assertEqual(response4.status_code, 404)
        user = User.query.filter_by(username="user2").first()
        self.assertEqual(user.tasks_per_page, 5)

if __name__ == '__main__':
    unittest.main()
    os.chdir(basedir)
    os.remove('test.db')