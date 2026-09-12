import os
import sqlite3

DB_PATH = os.environ.get("DB_PATH", "credits.db")


def get_connection():
    '''
    Returns a connection to the SQLite database with foreign keys enabled.
    '''
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def create_db():
    '''
    Creates the users and credits tables if they do not already exist.
    '''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id      INTEGER PRIMARY KEY,
            name    TEXT,
            lang    TEXT    DEFAULT 'FIN'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credits (
            user_id             INTEGER PRIMARY KEY,
            money               REAL    DEFAULT 0,
            latest_change       TEXT,
            latest_change_time  TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()
