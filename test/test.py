# -*- coding: utf-8 -*-
import unittest
from todo import app, db
from config import basedir
from todo.models import User, Task, Question, Choice, Opinion
import os
from passlib.hash import argon2
from datetime import datetime


class FlaskTest(unittest.TestCase):
    """Testing class"""
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test/test.db')
        self.app = app.test_client()
        db.create_all()
        password = argon2.using(rounds=4).hash("password")
        user1 = User(username='user', password=password, email="test@test.com")
        task1 = Task(id=0, task="test task1 test", executed=False, data_pub="2017-01-19T04:00", username="user")
        task2 = Task(id=1, task="test task2 test", executed=False, data_pub="2017-01-19T04:00", username="user")
        question1 = Question(id=1, question_text='Do You like this website?', pub_date=datetime.now())
        question2 = Question(id=2, question_text='What do you like? What would You improve?', pub_date=datetime.now())
        question3 = Question(id=3, question_text='Does this website work properly?', pub_date=datetime.now())
        question4 = Question(id=4, question_text='If not then what works wrong?', pub_date=datetime.now())
        choice1 = Choice(id=1, question='Do You like this website?', choice_text='Yes', votes=0)
        choice2 = Choice(id=2, question='Do You like this website?', choice_text='No', votes=0)
        choice3 = Choice(id=3, question='Does this website work properly?', choice_text='Yes', votes=0)
        choice4 = Choice(id=4, question='Does this website work properly?', choice_text='No', votes=0)
        db.session.add(task1)
        db.session.add(task2)
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

    def register(self, username, password, confpass, email):
        return self.app.post('/register', data=dict(login=username, password=password, password2=confpass, email=email),
                             follow_redirects=True)

    def login(self, username, password):
        return self.app.post('/', data=dict(login=username, password=password), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def user(self, task, date):
        return self.app.post('/user/<username>', data=dict(task=task, date=date), follow_redirects=True)

    def executed(self, task_id):
        return self.app.post('/executed', data=dict(execute=task_id), follow_redirects=True)

    def erase(self, erase):
        return self.app.post('/erase', data=dict(erase=erase), follow_redirects=True)

    def delete_account(self):
        return self.app.post('/delete_account', follow_redirects=True)

    def change_profile_data(self, username, password, password2, email):
        return self.app.post('/settings', data=dict(login=username, password=password, password2=password2,
                                                               email=email), follow_redirects=True)

    # Tests

    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

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
        self.assertIn(b'Incorrect data', response.data)

    def test_invalid_user_login_empty_login_and_password(self):
        response = self.login("", "")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Incorrect login or password', response.data)

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
        self.assertIn(b'Error!: You cannot add empty task!', response.data)
        self.assertFalse(Task.query.filter_by(task="").first())

    def test_valid_execute_task(self):
        self.login('user', 'password')
        response = self.executed(0)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Task.query.filter_by(id=0).first().executed)

    def test_valid_erase_multi_tasks(self):
        self.login('user', 'password')
        response = self.erase([0, 1])
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.query.filter_by(username='user').all())
        self.assertIn(b'Tasks deleted!', response.data)

    def test_valid_delete_account(self):
        self.login('user', 'password')
        response = self.delete_account()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.query.filter_by(username='user').first())
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

    def test_invalid_change_profile_data_passsword_do_not_match(self):
        self.login('user', 'password')
        response = self.change_profile_data('user1234', 'password23', 'password2', 'test2@test.com')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Passwords do not match', response.data)
        user = User.query.filter_by(username="user1234").first()
        self.assertFalse(argon2.verify('password23' or 'password2', user.password))

    def test_invalid_change_profile_data_login_already_exists(self):
        self.register('user1', 'password1', 'password1', 'test@gmail.com')
        self.login('user', 'password')
        response = self.change_profile_data('user1', '', '', '')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login already exists', response.data)
        self.assertTrue(len(User.query.filter_by(username="user1").all()) == 1)
        self.assertTrue(len(User.query.filter_by(username="user").all()) == 1)

    def test_invalid_change_profile_data_email_already_exists(self):
        self.register('user1', 'password1', 'password1', 'test@gmail.com')
        self.login('user', 'password')
        response = self.change_profile_data('', '', '', 'test@gmail.com')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'email address already exists', response.data)
        self.assertTrue(len(User.query.filter_by(email="test@gmail.com").all()) == 1)
        self.assertTrue(len(User.query.filter_by(email="test@test.com").all()) == 1)

    def test_valid_change_profile_message_email_changed(self):
        self.login('user', 'password')
        response = self.change_profile_data('', '', '', 'test@gmail.com')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Changes were saved', response.data)

    def test_invalid_change_profile_message_email_changed(self):
        self.login('user', 'password')
        response = self.change_profile_data('', '', '', 'testil.com')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'incorrect email address', response.data)

    def test_valid_change_profile_message_login_changed(self):
        self.login('user', 'password')
        response = self.change_profile_data('usserr', '', '', '')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Changes were saved', response.data)

    def test_valid_change_profile_message_password_changed(self):
        self.login('user', 'password')
        response = self.change_profile_data('', 'password23', 'password23', '')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Changes were saved', response.data)

    def test_remind_password_page(self):
        response = self.app.get('/password_reset', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_valid_password_reset(self):
        self.register('user1', 'password1', 'password1', 'tyson3031@onet.pl')
        response = self.app.post('/password_reset', data=dict(email='tyson3031@onet.pl'), follow_redirects=True)
        self.assertIn(b'New password has been sent to given email address!', response.data)
        self.assertEqual(response.status_code, 200)

    def test_invalid_password_reset(self):
        response = self.app.post('/password_reset', data=dict(email='bad-email.pl'), follow_redirects=True)
        self.assertIn(b'No user with given email address!', response.data)
        self.assertEqual(response.status_code, 200)

    def test_poll_page(self):
        self.login('user', 'password')
        response = self.app.get('/poll', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_valid_vote_yes(self):
        self.login('user', 'password')
        response = self.app.post('/poll', data=dict(choice1=1, choice2='', choice3=3, choice4='',), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        choice1 = Choice.query.filter_by(id=1).first()
        choice3 = Choice.query.filter_by(id=3).first()
        self.assertEqual(choice1.votes, 1)
        self.assertEqual(choice3.votes, 1)

    def test_valid_vote_no(self):
        self.login('user', 'password')
        response = self.app.post('/poll', data=dict(choice1=2, choice2='', choice3=4, choice4=''), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        choice1 = Choice.query.filter_by(id=2).first()
        choice3 = Choice.query.filter_by(id=4).first()
        self.assertEqual(choice1.votes, 1)
        self.assertEqual(choice3.votes, 1)

    def test_valid_vote_opinion(self):
        self.login('user', 'password')
        response = self.app.post('/poll', data=dict(choice1=1, choice2="It's awesome website!", choice3=3, choice4=''),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Opinion.query.filter_by(opinion_text="It's awesome website!").first())
        self.assertTrue(Opinion.query.filter_by(error_text='').first())

    def test_valid_vote_error(self):
        self.login('user', 'password')
        response = self.app.post('/poll', data=dict(choice1=1, choice2='',  choice3=3, choice4="It's broken!"), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Opinion.query.filter_by(error_text="It's broken!").first())
        self.assertTrue(Opinion.query.filter_by(opinion_text='').first())

    def test_valid_vote_error_and_opinion(self):
        self.login('user', 'password')
        response = self.app.post('/poll', data=dict(choice1=1, choice2="It's awesome website!", choice3=3,
                                                    choice4="It's broken!"), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Opinion.query.filter_by(error_text="It's broken!").first())
        self.assertTrue(Opinion.query.filter_by(opinion_text="It's awesome website!").first())

    def test_invalid_vote_not_all_options_chosen_version1(self):
        self.login('user', 'password')
        response = self.app.post('/poll', data=dict(choice1=1, choice2='', choice3='', choice4=''), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        choice1 = Choice.query.filter_by(id=1).first()
        self.assertEqual(choice1.votes, 0)
        self.assertIn(b"You did not select a choice in all questions.", response.data)

    def test_invalid_vote_not_all_options_chosen_version2(self):
        self.login('user', 'password')
        response = self.app.post('/poll', data=dict(choice1='', choice2='', choice3=3, choice4=''), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        choice1 = Choice.query.filter_by(id=3).first()
        self.assertEqual(choice1.votes, 0)
        self.assertIn(b"You did not select a choice in all questions.", response.data)

    def test_invalid_vote_not_all_options_chosen_version3_with_opinion_and_error(self):
        self.login('user', 'password')
        response = self.app.post('/poll', data=dict(choice1=1, choice2="It's awesome website!", choice3='',  choice4="It's broken!"),
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        choice1 = Choice.query.filter_by(id=1).first()
        self.assertEqual(choice1.votes, 0)
        self.assertIn(b"You did not select a choice in all questions.", response.data)
        self.assertFalse(Opinion.query.filter_by(error_text="It's broken!").first())
        self.assertFalse(Opinion.query.filter_by(opinion_text="It's awesome website!").first())


if __name__ == '__main__':
    unittest.main()
    os.chdir(basedir)
    os.remove('test.db')