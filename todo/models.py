import sqlite3
from todo import app
from flask import g

class User():
    """User class"""

    def __init__(self, id):
        self.username = id
        db = get_db()
        self.hashpassword = db.execute('SELECT password FROM users WHERE login = ?;', (self.username,)).fetchone()["password"]

    def is_active(self):
        """logged in user always active"""
        return True

    def get_id(self):
        """Returns username as id"""
        return self.username

    def is_authenticated(self):
        """Returns True"""
        return True

    def is_anonymous(self):
        """always False, no anonymous users"""
        return False

def get_db():
    """Connecting with database"""

    if not hasattr(g, 'db'):        # jeżeli brak połączenia, to je tworzymy
        con = sqlite3.connect(app.config['DATABASE'])
        con.row_factory = sqlite3.Row
        g.db = con      # zapisujemy połączenie w kontekście aplikacji
    return g.db      # zwracamy połączenie z bazą
