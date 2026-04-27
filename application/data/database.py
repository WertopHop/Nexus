import sqlite3
from datetime import datetime
from pathlib import Path
from utils import get_user_data_dir
from data.coding import (generate_key_from_password, encode_message, decode_message)

class Database:
    def __init__(self, peer_id=None, password=None):
        data_dir = Path(get_user_data_dir())
        db_name = f"{peer_id}_data.db"
        self.db_path = data_dir / db_name
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.key = generate_key_from_password(password, peer_id.encode())
        self.initialize_database()

    def initialize_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                contact_id INTEGER,
                message TEXT,
                direction boolean DEFAULT 1,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(contact_id) REFERENCES contacts(id)
            )
        ''')
        self.connection.commit()

    def add_contact(self, name):
        try:
            encoded_name = encode_message(name, self.key)
            self.cursor.execute('INSERT INTO contacts (name) VALUES (?)', (encoded_name,))
            self.connection.commit()
        except sqlite3.IntegrityError:
            pass

    def add_message(self, contact_name, message, direction=True, timestamp=None):
        try:
            encoded_contact_name = encode_message(contact_name, self.key)
            self.cursor.execute('SELECT id FROM contacts WHERE name = ?', (encoded_contact_name,))
            contact = self.cursor.fetchone()
            if contact:
                contact_id = contact[0]
                encoded_message = encode_message(message, self.key)
                self.cursor.execute('INSERT INTO messages (contact_id, message, direction, timestamp) VALUES (?, ?, ?, ?)', (contact_id, encoded_message, direction, datetime.now()))
                self.connection.commit()
        except Exception as e:
            print(f"Error adding message: {e}")

    def get_contacts(self):
        self.cursor.execute('SELECT name FROM contacts')
        return [decode_message(row[0], self.key) for row in self.cursor.fetchall()]

    def get_messages(self, contact_name):
        encoded_contact_name = encode_message(contact_name, self.key)
        self.cursor.execute('''
            SELECT m.message, m.direction, m.timestamp FROM messages m
            JOIN contacts c ON m.contact_id = c.id
            WHERE c.name = ?
            ORDER BY m.timestamp ASC
        ''', (encoded_contact_name,))
        return [(decode_message(row[0], self.key), row[1], row[2]) for row in self.cursor.fetchall()]
    
    def delete_contact(self, name):
        encoded_name = encode_message(name, self.key)
        self.cursor.execute('DELETE FROM messages WHERE contact_id IN (SELECT id FROM contacts WHERE name = ?)', (encoded_name,))
        self.cursor.execute('DELETE FROM contacts WHERE name = ?', (encoded_name,))
        self.connection.commit()

    def close(self):
        self.connection.close()


if __name__ == "__main__":
    db = Database()
    db.close()
        