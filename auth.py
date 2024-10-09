import pymysql
import hashlib

# Database connection setup
def create_connection():
    connection = pymysql.connect(
         host=st.secrets["MYSQL_HOST"],  # MySQL host (cloud or exposed local)
        user=st.secrets["MYSQL_USER"],  # MySQL username
        password=st.secrets["MYSQL_PASSWORD"],  # MySQL password
        database=st.secrets["MYSQL_DB"],  # MySQL database name
        port=3306,  # MySQL port (3306 is the default)
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

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
