from todo import db


class User(db.Model):
    """User class"""

    # tworzymy kolumny w bazie danych jak atrybuty klasy
    username = db.Column(db.Text, primary_key=True, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False, index=True)
    email = db.Column(db.Text, unique=True, index=True)
    tasks = db.relationship('Task', backref='author', lazy='dynamic')

    def __str__(self):
        return self.username

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
    data_pub = db.Column(db.Text)
    username = db.Column(db.Text, db.ForeignKey("user.username"), nullable=False,)     #user to nazwa tabeli

    def __str__(self):
        return self.task


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_text = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime)
    choices = db.relationship('Choice', backref="Quest", lazy='dynamic')

    def __str__(self):
        return self.question_text


class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.Text, db.ForeignKey("question.question_text"), nullable=False)
    choice_text = db.Column(db.Text, nullable=False)
    votes = db.Column(db.Integer, server_default='0')

    def __str__(self):
        return self.choice_text


class Opinion(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    opinion_text = db.Column(db.Text)
    error_text = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)

    def __str__(self):
        return self.id