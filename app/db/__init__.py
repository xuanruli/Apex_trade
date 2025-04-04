import sqlite3
from .schema import setup_database
from .data_loader import process_all_stocks
import os
app_root = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(app_root, 'db/apex_data.db')

def initialize_database():
    print("Database Init Start")
    setup_database()
    process_all_stocks()
    print("Database Init Complete")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def execute_query(query, params=()):
    """
    look up information in database
    Return : dict
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)

        columns = [desc[0] for desc in cursor.description]
        result = []
        for row in cursor.fetchall():
            result.append(dict(zip(columns, row)))

        return result
    finally:
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
        conn.close()