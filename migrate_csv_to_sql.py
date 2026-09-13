'''
Migration script: CSV -> SQLite

Migrates existing credits.csv data into the new two-table SQLite schema.

- Users WITH a Telegram ID: inserted as-is
- Users WITHOUT a Telegram ID: assigned a temporary negative ID as placeholder.
  When they next interact with the bot, add_old_credits() will match them
  by username and replace the placeholder with their real Telegram user ID.

Usage:
    python migrate_csv_to_sql.py                          # uses defaults
    python migrate_csv_to_sql.py --csv credits.csv --db credits.db
'''

import csv
import argparse
import math
from db import get_connection, create_db


def migrate(csv_path):
    create_db()
    conn = get_connection()
    cursor = conn.cursor()

    placeholder_id = -1

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['name']
            lang = row.get('lang', 'FIN') or 'FIN'
            money = float(row['money']) if row['money'] else 0
            latest_change = row.get('latest_change', '')
            latest_change_time = row.get('latest_change_time', '')

            # Check if we have a valid Telegram user ID
            raw_id = row.get('id', '')
            has_valid_id = False
            if raw_id:
                try:
                    user_id = int(float(raw_id))
                    if not math.isnan(float(raw_id)) and user_id > 0:
                        has_valid_id = True
                except (ValueError, OverflowError):
                    pass

            if not has_valid_id:
                user_id = placeholder_id
                placeholder_id -= 1

            # Insert into users table
            cursor.execute('''
                INSERT OR IGNORE INTO users (id, name, lang)
                VALUES (?, ?, ?)
            ''', (user_id, name, lang))

            # Insert into credits table
            cursor.execute('''
                INSERT OR IGNORE INTO credits (user_id, money, latest_change, latest_change_time)
                VALUES (?, ?, ?, ?)
            ''', (user_id, money, latest_change, latest_change_time))

            status = 'OK' if has_valid_id else f'placeholder id={user_id}'
            print(f'  Migrated: {name:20s}  balance={money:8.2f}  ({status})')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migrate credits.csv to SQLite')
    parser.add_argument('--csv', default='credits.csv', help='Path to CSV file')
    args = parser.parse_args()

    print(f'Migrating {args.csv} ...')
    migrate(args.csv)
    print('Done!')
