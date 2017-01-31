from todo import db


class User(db.Model):
    """User class"""

    # tworzymy kolumny w bazie danych jak atrybuty klasy
    username = db.Column(db.Text, primary_key=True, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False, index=True)
    email = db.Column(db.Text, unique=True, index=True)
    tasks = db.relationship('Task', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

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
    data_pub = db.Column(db.TEXT)
    username = db.Column(db.Text, db.ForeignKey("user.username"), nullable=False,)     #user to nazwa tabeli

    def __repr__(self):
        return '<User {}>'.format(self.task)
