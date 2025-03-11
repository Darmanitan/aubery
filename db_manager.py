import sqlite3
import asyncio
import json

def initialize_user(id, notificationMethod):
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    cursor.execute(f"INSERT INTO users VALUES ('{id}', '', '{notificationMethod}')")
    db.commit()
    db.close()

def fetch_user(id):
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id='{id}'")
    return cursor.fetchall()

def create_table():
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, wishlist TEXT NOT NULL, notificationMethod INTEGER)")
    db.commit()
    db.close()

def add_game(user_id, game_id):
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT wishlist FROM users WHERE id={user_id}")
    result = cursor.fetchone()
    if result:
        wishlist = json.loads(result[0])
        wishlist.append(int(game_id))
    else:
        wishlist = []
        wishlist.append(game_id)
    cursor.execute(f"UPDATE users SET wishlist='{json.dumps(wishlist)}' WHERE id={user_id}")
    db.commit()
    db.close()