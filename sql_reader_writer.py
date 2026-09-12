from datetime import datetime
from db import get_connection


def add_old_credits(username, user_id):
    '''
    Check if user has assigned credits by username.
    If True, the user's id is updated and returns True.
    If not, return False.
    '''
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM users WHERE name = ?', (username,))
    row = cursor.fetchone()

    if row is not None:
        old_id = row['id']
        cursor.execute('''
            UPDATE users SET id = ? WHERE name = ?
        ''', (user_id, username))
        cursor.execute('''
            UPDATE credits
            SET latest_change = ?, latest_change_time = ?
            WHERE user_id = ?
        ''', ('add user', str(datetime.now()), user_id))
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False


def find_user(id):
    '''
    Check if user id exists in the users table.
    '''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM users WHERE id = ?', (id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None


def add_user(username, id):
    '''
    Adds a new user into the users and credits tables.
    '''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (id, name, lang) VALUES (?, ?, 'FIN')
    ''', (id, username))
    cursor.execute('''
        INSERT INTO credits (user_id, money, latest_change, latest_change_time)
        VALUES (?, 0, 'add new user', ?)
    ''', (id, str(datetime.now())))
    conn.commit()
    conn.close()


def add_money(username, user_id, money):
    '''
    Adds money to the user's balance.

    Returns the current amount of money after the addition.
    '''
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT money FROM credits WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    current_money = round(float(row['money']) + float(money), 2)

    cursor.execute('''
        UPDATE credits
        SET money = ?, latest_change = ?, latest_change_time = ?
        WHERE user_id = ?
    ''', (current_money, 'add money', str(datetime.now()), user_id))
    cursor.execute('UPDATE users SET name = ? WHERE id = ?', (username, user_id))
    conn.commit()
    conn.close()

    return current_money


def use_money(username, user_id, money):
    '''
    Subtracts money from the user's balance.

    Returns the current amount of money after the subtraction.
    If the balance would go negative, the subtraction is not applied
    but the negative result is still returned.
    '''
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT money FROM credits WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    current_money = float(row['money']) - float(money)

    if current_money >= 0:
        current_money = round(current_money, 2)
        cursor.execute('''
            UPDATE credits
            SET money = ?, latest_change = ?, latest_change_time = ?
            WHERE user_id = ?
        ''', (current_money, 'use money', str(datetime.now()), user_id))
        cursor.execute('UPDATE users SET name = ? WHERE id = ?', (username, user_id))
        conn.commit()
        conn.close()
        return current_money
    else:
        # Update the username but don't change the balance
        cursor.execute('UPDATE users SET name = ? WHERE id = ?', (username, user_id))
        conn.commit()
        conn.close()
        return round(current_money, 2)


def check_money(user_id):
    '''
    Returns the current amount of money for the user.
    '''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT money FROM credits WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return float(row['money'])


def set_language(user_id, language):
    '''
    Sets the language preference for the user.
    '''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET lang = ? WHERE id = ?', (language, user_id))
    conn.commit()
    conn.close()


def read_language(user_id):
    '''
    Returns the language preference for the user.
    Defaults to FIN if not set.
    '''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT lang FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None or row['lang'] is None:
        set_language(user_id, 'FIN')
        return 'FIN'

    return row['lang']
