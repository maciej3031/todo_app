# -*- coding: utf-8 -*-

import os
import pymysql
basedir = os.path.abspath(os.path.dirname(__file__))    # ścieżka dostepu do katalogu głównego

CSRF_ENABLED = True          # ochrona przed atakiami typu CSRF
SECRET_KEY = 'verysecretvalue'        # sekretna wartosc niezbeda do autoryzacji w niektorych przypadkach

# połączenie z bazą danych
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'base.db')

SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')    # repozytorium trzymające informacje o migracjach
SITE_NAME = 'My Tasks'      # nazwa strony
SQLALCHEMY_TRACK_MODIFICATIONS = True

#EMAIL SETTINGS
MAIL_USE_TLS = False
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'example_mail'
MAIL_PASSWORD = 'example_pass'

# pagination
TASKS_PER_PAGE = 9


