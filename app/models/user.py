from app.db import execute_query, execute_update
from app.logger import logger
from werkzeug.security import generate_password_hash, check_password_hash
class User:
    def __init__(self, username, email, firstname, lastname, password=None):
        self._id = None
        self._username = username
        self._email = email
        self._firstname = firstname
        self._lastname = lastname
        self._password_hash = generate_password_hash(password) if password else "OAuth"

        logger.info(f"[USER] - new user {username}")


    @staticmethod
    def get_by_username(username):
        """get user info by username"""
        query = "SELECT id, username, email, firstname, lastname, password_hash FROM users WHERE username = %s"
        result = execute_query(query, (username,))

        if result:
            return result[0]
        return None


    @staticmethod
    def get_by_email(email):
        """get user info by email if user forget password"""
        query = "SELECT id, username, email, firstname, lastname, password_hash FROM users WHERE email = %s"
        result = execute_query(query, (email,))

        if result:
            return result[0]
        return None


    def save(self):
        """
        function 1: update user information for user who already has id
        function 2: complete user.id property
        """
        if self._id: #update
            query = """UPDATE users SET username=%s, email=%s, firstname=%s, lastname=%s, password_hash=%s WHERE id=%s"""
            execute_update(query, (self._id, self._username, self._email,
                                  self._firstname, self._lastname, self._password_hash))
            logger.info("[DATABASE] - user update info")

        else:  # complete user.id for new user
            query = """INSERT INTO users (username, email, firstname, lastname, password_hash) VALUES (%s, %s, %s, %s, %s)"""
            execute_update(query, (self._username, self._email,
                                  self._firstname, self._lastname, self._password_hash))
            logger.info(f"[DATABASE] - new user added {self._username}")

            query = "SELECT id FROM users WHERE email = %s"
            result = execute_query(query, (self._email,))
            if result:
                self._id = result[0]['id']

    @staticmethod
    def check_password(username, password):
        """check password"""
        query = "SELECT username, email, firstname, lastname, password_hash FROM users WHERE username = %s"
        result = execute_query(query, (username,))
        if not result:
            logger.info("[USER] - user update info")
            return False
        password_hash = result[0]['password_hash']

        return check_password_hash(password_hash, password)

    @staticmethod
    def change_password(user_id, new_password):
        password_hash = generate_password_hash(new_password)
        query = "UPDATE users SET password_hash = %s WHERE id = %s"
        execute_update(query, (password_hash, user_id))
        logger.info("[DATABASE] - update password")

    @staticmethod
    def delete_user(user_id):
        query = "DELETE FROM users WHERE id = %s"
        execute_update(query, (user_id,))
        logger.info(f"[DATABASE] - user{user_id} was deleted")

    @staticmethod
    def get_all_users():
        """
        Get all user in the system.
        """
        query = """ SELECT * FROM users"""
        result = execute_query(query, ())
        return result



