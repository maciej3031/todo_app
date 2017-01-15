from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)               # stworzenie aplikacji
app.config.from_object('config')       # konfiguracja aplikacji wczytana z modułu config.py

login_manager = LoginManager()
login_manager.init_app(app)         #połączenie flask-login z flask
login_manager.login_view = "login"
login_manager.login_message = ""        #komunikat po zalogowaniu

import todo.views