SIMPLE TO DO APPLICATION
Python version 3.5.2+

HOW TO RUN

1) Create virtual-env
2) Install requirements using: 'pip install -r requirements.txt'
3) Run 'python db_create.py'
4) Run 'python db_migrate.py'
5) Run 'python run.py'

1. Basic information
Application is developed in Python, using the Flask framework. Front end is based on pure HTML5 and CSS. Database is created in MySQL. Deployed on pythonanywhere.

2. Functionality
Application allows to:
- register an account using login, password and email. Password is hashed using Argon2.
- log a registered user in using login and email.
- reset password, giving email address.
- use 'remember me' feature.
- add, execute or delete tasks with or without chosen date and time.
- change account settings such as: e-mail, login, password, pagination
- delete account.
- fill the poll on how do you like the website and hot it works.
- change page
- log a user out

3. Application structure
- application is developed using MVT design pattern.
- database model is define in todo/models.py
- views handles all the requests are defined in todo/views.py
- static files are located in todo/static
- html templates created using jinja2 language are located in todo/templates
- configuration settings are located in config.py
- migrations are created based on the tutorial: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database
- migrations are located in db_repository
- migrations are carried out by db_downgrade.py, db_migrate.py, db_upgrade.py
- application can be initiate by launching run.py
- all the unit tests are located in test/test.py
