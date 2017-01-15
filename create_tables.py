from todo.models import get_db

def create_tables():
    """Creating tables in database"""

    db = get_db()
    db.execute('CREATE TABLE IF NOT EXISTS users (login TEXT PRIMARY KEY NOT NULL,'
               ' password TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS tasks ('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               ' task TEXT NOT NULL,'
               ' executed BOOLEAN NOT NULL,'
               ' data_pub DATETIME NOT NULL,'
               ' login TEXT NOT NULL,'
               ' FOREIGN KEY(login) REFERENCES users(login))')