import mysql.connector
from .schema import setup_database
from .data_loader import process_all_stocks

def initialize_database():
    print("Database Init Start")
    setup_database()
    process_all_stocks()
    print("Database Init Complete")

def get_db_connection():
    from .schema import DB_CONFIG
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn

def execute_query(query, params=()):
    """
    look up information in database
    Return : dict
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result
    finally:
        cursor.close()
        conn.close()

def execute_update(query, params=()):
    """
    only for changing database
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()