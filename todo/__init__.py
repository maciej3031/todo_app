# -*- coding: utf-8 -*-
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_sslify import SSLify

app = Flask(__name__)               # stworzenie aplikacji
app.config.from_object('config')       # konfiguracja aplikacji wczytana z modułu config.py
db = SQLAlchemy(app)            # utworzenie obiektu bazy danych
mail = Mail(app)            # utworzenie możliwości wysyłania emaili
sslify = SSLify(app)

login_manager = LoginManager()
login_manager.init_app(app)         #połączenie flask-login z flask
login_manager.login_view = "login"
login_manager.login_message = ""        #komunikat po zalogowaniu

from todo import views, models