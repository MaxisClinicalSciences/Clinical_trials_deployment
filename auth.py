import pymysql
import hashlib

def get_db_connection():
    conn = pymysql.connect(
        host=st.secrets["https://stale-bobcats-lead.loca.lt"],  # MySQL host (cloud or exposed local)
        user=st.secrets["root"],  # MySQL username
        password=st.secrets["root"],  # MySQL password
        database=st.secrets["webapp"],  # MySQL database name
        port=3306  # MySQL port (3306 is the default)
    )
    return conn

# # Database connection setup
# def create_connection():
#     connection = pymysql.connect(
#         host=' https://stale-bobcats-lead.loca.lt',  # MySQL host (cloud or exposed local)
#         user='root',  # MySQL username
#         password='root',  # MySQL password
#         database='webapp',  # MySQL database name
#         cursorclass=pymysql.cursors.DictCursor
#     )
#     return connection

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
