# Messages being used by views functions


class LoginMessages:
    incorrect_password_error_message = "Incorrect password"
    no_user_error_message = "No such user"
    incorrect_data_error_message = "Incorrect login or password."
    success_message = 'Logged in successfully'


class LogoutMessages:
    success_message = 'logged out successfully'


class RegisterMessages:
    incorrect_passwords_error_message = "Passwords do not match"
    already_exist_error_message = "Login or email already exists"
    incorrect_email_error_message = "Incorrect email address"
    incorrect_data_error_message = "Incorrect data. Max login and password length 40 characters." \
                                   " Max email length 100 characters"
    success_message = "Profile was created successfully"


class UserMessages:
    error_message = 'Error: Task is empty or is too long. Max length 255 characters!'
    success_message = 'New task added.'


class PollMessages:
    no_choices_error_message = "You did not select a choice in all questions."
    mex_length_error_message = "Max 255 characters!"


class ExecutedMessages:
    success_message = 'New task added.'


class UndoMessages:
    success_message = 'Task changed to not executed!'


class EraseMessages:
    success_message = 'Tasks deleted!'


class SettingsMessages:
    email_exists_error_message = "email address already exists"
    incorrect_email_error_message = "Incorrect email address"
    incorrect_login_data_error_message = "login already exists or login too long. Max 40 characters"
    incorrect_password_data_error_message = "Passwords do not match or password too long. Max 40 characters"
    success_message = 'Changes were saved'


class AppSettingsMessages:
    incorrect_number_error_message = "Invalid number!"
    incorrect_value_error_message = "Invalid number! Max value 100"
    success_message = "New value: {} tasks per page!"


class DeleteAccountMessages:
    success_message = 'Account was deleted permanently'


class PasswordResetMessages:
    success_message = 'New password has been sent to given email address!'
    title_of_message = "Reset password"
    body_of_message = "Hello {}! \nYour password has been changed. New password: {}. We recommend to change it" \
                      " immediately. \n\nRegards, \ntodo team!"
    unidentified_error_message = """"There was a problem with resetting Your email address. Password was not reset.
                 Problem may be connected with email server. Try again in few minutes."""
    no_user_error_message = "No user with given email address or address is wrong!"