import os
basedir = os.path.abspath(os.path.dirname(__file__))    # ścieżka dostepu do katalogu głównego

CSRF_ENABLED = True          # ochrona przed atakiami typu CSRF
SECRET_KEY = 'verysecretvalue'        # sekretna wartosc niezbeda do autoryzacji w niektorych przypadkach
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'base.db')       # połączenie z bazą danych
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')    # repozytorium trzymające informacje o migracjach
SITE_NAME = 'My Tasks'      # nazwa strony
SQLALCHEMY_TRACK_MODIFICATIONS = True
