import unittest
from todo import app, db
from config import basedir
from todo.models import User, Task
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
        task1 = Task(id=0, task="test task1 test", executed=False, data_pub=datetime.now().replace(microsecond=0),
                     username="user")
        task2 = Task(id=1, task="test task2 test", executed=False, data_pub=datetime.now().replace(microsecond=0),
                     username="user")
        db.session.add(task1)
        db.session.add(task2)
        db.session.add(user1)
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

    def insert(self, task):
        return self.app.post('/insert', data=dict(task=task), follow_redirects=True)

    def executed(self, task_id):
        return self.app.post('/executed', data=dict(execute=task_id), follow_redirects=True)

    def erase(self, erase):
        return self.app.post('/erase', data=dict(erase=erase), follow_redirects=True)

    def delete_account(self):
        return self.app.post('/delete_account', follow_redirects=True)

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

    def test_invalid_user_registration_duplicate_user(self):
        response = self.register('user', 'password', 'password', 'test@gmail.com')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login or email already exists', response.data)

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

    def test_insert_task(self):
        self.login('user', 'password')
        response = self.insert('task1 task1 task1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New task added.', response.data)
        self.assertTrue(Task.query.filter_by(task="task1 task1 task1").first())

    def test_insert_invalid_empty_task(self):
        self.login('user', 'password')
        response = self.insert('')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Error!: You cannot add empty task!', response.data)
        self.assertFalse(Task.query.filter_by(task="").first())

    def test_execute_task(self):
        self.login('user', 'password')
        response = self.executed(0)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Task.query.filter_by(id=0).first().executed)

    def test_erase_multi_tasks(self):
        self.login('user', 'password')
        response = self.erase([0, 1])
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.query.filter_by(username='user').all())

    def test_delete_account(self):
        self.login('user', 'password')
        response = self.delete_account()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.query.filter_by(username='user').first())
        self.assertFalse(User.query.filter_by(username='user').first())
        self.assertIn(b'Account was deleted permanently', response.data)

if __name__ == '__main__':
    unittest.main()
    os.chdir(basedir)
    os.remove('test.db')