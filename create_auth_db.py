import sqlite3

def create_users_table():
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            first_name TEXT NOT NULL,
            second_name TEXT NOT NULL,
            contacts TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            username TEXT NOT NULL UNIQUE,
            lots_ids TEXT DEFAULT [],          
            strikes  INTEGER DEFAULT 0,
            bot_chat_id  INTEGER,
            status  TEXT DEFAULT unbanned,
            balance  INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            images TEXT,
            start_price INTEGER,
            seller_url TEXT,
            location TEXT,
            description TEXT,
            start_time TEXT,
            end_time TEXT,
            status TEXT DEFAULT обрабатывается,
            attached_files TEXT,
            buffer TEXT,
            waiting_publication INTEGER DEFAULT 0,
            current_bet INTEGER,
            all_bets TEXT,
            ninja_bet INTEGER,
            message_id INTEGER,
            lot_creator TEXT,
            approver TEXT,
            current_lot_winner TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS strikes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            comment TEXT,
            value INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS finances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            current_balance INTEGER,
            lot_id INTEGER,
            count INTEGER,
            comment TEXT
        )
    ''')

    connection.commit()
    connection.close()

if __name__ == '__main__':
    create_users_table()
