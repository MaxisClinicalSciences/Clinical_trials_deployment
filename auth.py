import pymysql
import hashlib
import streamlit as st



# Database connection setup
def create_connection():
    try:
        connection = pymysql.connect(
            host=st.secrets["MYSQL_HOST"],       # Use secrets for MySQL host
            user=st.secrets["MYSQL_USER"],       # Use secrets for MySQL username
            password=st.secrets["MYSQL_PASSWORD"], # Use secrets for MySQL password
            database=st.secrets["MYSQL_DB"],     # Use secrets for MySQL database name
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
    try:
        connection = create_connection()
        with connection.cursor() as cursor:
            sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
            cursor.execute(sql, (username, hash_password(password)))
            connection.commit()
            return True
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return False
    finally:
        connection.close()
