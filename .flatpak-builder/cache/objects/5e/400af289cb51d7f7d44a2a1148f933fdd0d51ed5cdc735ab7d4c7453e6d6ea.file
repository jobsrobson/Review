import sqlite3
import os
from datetime import datetime, timedelta

# Use XDG_DATA_HOME for Flatpak compatibility
DATA_DIR = os.path.join(os.path.expanduser('~'), '.local', 'share', 'review')
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, 'topics.db')

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = DB_PATH
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Topics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                area TEXT,
                start_date TEXT NOT NULL,
                tags TEXT,
                color TEXT,
                description TEXT,
                time_spent INTEGER DEFAULT 0
            )
        ''')
        
        # Revisions table
        # Status can be: 'pending', 'studied', 'missed'
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS revisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                scheduled_date TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                interval_days INTEGER,
                FOREIGN KEY (topic_id) REFERENCES topics (id) ON DELETE CASCADE
            )
        ''')
        
        # Areas table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS areas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT
            )
        ''')
        
        # Managed Tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS managed_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT
            )
        ''')
        
        self.conn.commit()
        
        # Migration: Add description if not exists
        try:
            cursor.execute('ALTER TABLE topics ADD COLUMN description TEXT')
            self.conn.commit()
        except sqlite3.OperationalError:
            pass

        # Migration: Add time_spent if not exists
        try:
            cursor.execute('ALTER TABLE topics ADD COLUMN time_spent INTEGER DEFAULT 0')
            self.conn.commit()
        except sqlite3.OperationalError:
            pass
            
        # Migration: Add color to areas if not exists
        try:
            cursor.execute('ALTER TABLE areas ADD COLUMN color TEXT')
            self.conn.commit()
        except sqlite3.OperationalError:
            pass

    def add_topic(self, title, area, start_date, tags, color, description=""):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO topics (title, area, start_date, tags, color, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, area, start_date, tags, color, description))
        topic_id = cursor.lastrowid
        self.conn.commit()
        return topic_id

    def get_topics(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT t.*, a.color 
            FROM topics t 
            LEFT JOIN areas a ON t.area = a.name 
            ORDER BY t.area, t.title
        ''')
        return cursor.fetchall()

    def get_areas(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM areas ORDER BY name')
        return cursor.fetchall()

    def add_area(self, name, color=None):
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT INTO areas (name, color) VALUES (?, ?)', (name, color))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def delete_area(self, area_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM areas WHERE id = ?', (area_id,))
        self.conn.commit()

    def update_area(self, area_id, name, color):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE areas SET name = ?, color = ? WHERE id = ?', (name, color, area_id))
        self.conn.commit()

    def get_managed_tags(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM managed_tags ORDER BY name')
        return cursor.fetchall()

    def add_managed_tag(self, name, color):
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT INTO managed_tags (name, color) VALUES (?, ?)', (name, color))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def delete_managed_tag(self, tag_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM managed_tags WHERE id = ?', (tag_id,))
        self.conn.commit()

    def update_managed_tag(self, tag_id, name, color):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE managed_tags SET name = ?, color = ? WHERE id = ?', (name, color, tag_id))
        self.conn.commit()

    def add_revision(self, topic_id, scheduled_date, interval_days):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO revisions (topic_id, scheduled_date, interval_days)
            VALUES (?, ?, ?)
        ''', (topic_id, scheduled_date, interval_days))
        self.conn.commit()

    def get_revisions_for_topic(self, topic_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM revisions WHERE topic_id = ? ORDER BY scheduled_date ASC', (topic_id,))
        return cursor.fetchall()

    def update_revision_status(self, revision_id, status):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE revisions SET status = ? WHERE id = ?', (status, revision_id))
        self.conn.commit()

    def update_topic(self, topic_id, title, area, start_date, tags, color, description):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE topics 
            SET title = ?, area = ?, start_date = ?, tags = ?, color = ?, description = ?
            WHERE id = ?
        ''', (title, area, start_date, tags, color, description, topic_id))
        self.conn.commit()

    def update_time_spent(self, topic_id, duration_seconds):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE topics SET time_spent = time_spent + ? WHERE id = ?', (duration_seconds, topic_id))
        self.conn.commit()

    def update_revision_date(self, revision_id, new_date):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE revisions SET scheduled_date = ? WHERE id = ?', (new_date, revision_id))
        self.conn.commit()

    def delete_topic(self, topic_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM topics WHERE id = ?', (topic_id,))
        self.conn.commit()

    def reset_database(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM topics")
        cursor.execute("DELETE FROM revisions")
        cursor.execute("DELETE FROM areas")
        cursor.execute("DELETE FROM managed_tags")
        # Reset sequences
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('topics', 'revisions', 'areas', 'managed_tags')")
        self.conn.commit()

    def get_area_by_name(self, name):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM areas WHERE name = ?', (name,))
        return cursor.fetchone()

    def get_tag_by_name(self, name):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM managed_tags WHERE name = ?', (name,))
        return cursor.fetchone()

    def is_empty(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM topics")
        return cursor.fetchone()[0] == 0

    def close(self):
        self.conn.close()
