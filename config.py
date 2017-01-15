import os
from todo import app
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True          # ochrona przed atakiami typu CSRF
SECRET_KEY = 'verysecretvalue'        # sekretna wartosc niezbeda do autoryzacji w niektorych przypadkach
DATABASE = os.path.join(basedir, 'base.db')       # połączenie z bazą danych
SITE_NAME = 'My tasks'      # nazwa strony