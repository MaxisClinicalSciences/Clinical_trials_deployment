# db.py
import pymysql

def get_db_connection():
    connection = pymysql.connect(
        host=st.secrets["MYSQL_HOST"],  # MySQL host (cloud or exposed local)
        user=st.secrets["MYSQL_USER"],  # MySQL username
        password=st.secrets["MYSQL_PASSWORD"],  # MySQL password
        database=st.secrets["MYSQL_DB"],  # MySQL database name
        port=3306  # MySQL port (3306 is the default)
    )
    return connection
