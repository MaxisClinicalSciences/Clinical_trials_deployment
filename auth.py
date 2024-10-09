import pymysql
import hashlib
import streamlit as st



# Database connection setup
def create_connection():
    try:
        connection = pymysql.connect(
            host=st.secrets["MYSQL_HOST"],
            port=int(st.secrets["MYSQL_PORT"]),  # Include port if necessary
            user=st.secrets["MYSQL_USER"],
            password=st.secrets["MYSQL_PASSWORD"],
            database=st.secrets["MYSQL_DB"],
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as e:
        st.error(f"Error connecting to the database: {e}")
        return None

# Hash password for secure storage
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Check if the credentials are valid (for login)
def check_credentials(username, password):
    try:
        connection = create_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE username=%s AND password=%s"
            cursor.execute(sql, (username, hash_password(password)))
            result = cursor.fetchone()
            return result is not None
    finally:
        connection.close()

# Register a new user (for registration)
def register_user(username, password):
    connection = create_connection()
    if connection is None:
        return False  # Connection failed, can't register user

    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
            cursor.execute(sql, (username, hash_password(password)))
            connection.commit()
            return True
    except pymysql.MySQLError as e:
        st.error(f"Error registering user: {e}")
        return False
    finally:
        if connection:  # Check if connection is not None before closing
            connection.close()
