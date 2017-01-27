# import sqlite3
from todo import app, db
# from flask import g


class User(db.Model):
    """User class"""

    # tworzymy kolumny w bazie danych jak atrybuty klasy
    username = db.Column(db.Text, primary_key=True, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False, index=True)
    email = db.Column(db.Text, unique=True, index=True)
    tasks = db.relationship('Task', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    # def __init__(self, id):
    #     self.username = id
    #     db = get_db()
    #     self.password = db.execute('SELECT password FROM users WHERE username = ?;', (self.username,)).fetchone()["password"]

    def is_active(self):
        """logged in user always active"""
        return True

    def get_id(self):
        """Returns username as id"""
        try:
            return unicode(self.username)   # python 2
        except NameError:
            return str(self.username)   # python 3

    def is_authenticated(self):
        """Returns True"""
        return True

    def is_anonymous(self):
        """always False, no anonymous users"""
        return False


class Task(db.Model):
    """Task class"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task = db.Column(db.Text, nullable=False)
    executed = db.Column(db.Boolean, nullable=False)
    data_pub = db.Column(db.DateTime, nullable=False)
    username = db.Column(db.Text, db.ForeignKey("user.username"), nullable=False,)     #user to nazwa tabeli

    def __repr__(self):
        return '<User {}>'.format(self.task)


# def get_db():
#     """Connecting with database"""
#
#     if not hasattr(g, 'db'):        # jeżeli brak połączenia, to je tworzymy
#         con = sqlite3.connect(app.config['DATABASE'])
#         con.row_factory = sqlite3.Row
#         g.db = con      # zapisujemy połączenie w kontekście aplikacji
#     return g.db      # zwracamy połączenie z bazą
