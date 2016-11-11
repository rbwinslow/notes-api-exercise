import os
from sqlite3 import connect


class NotesStore:

    def __init__(self):
        if not os.path.isfile('notes.db'):
            self.initialize_db()
        self.sql = connect('notes.db')

    def initialize_db(self):
        sql = connect('notes.db')
        cursor = sql.cursor()

        cursor.execute('CREATE TABLE notes (id INTEGER PRIMARY KEY, content TEXT)')
        cursor.execute('CREATE TABLE tags (id INTEGER PRIMARY KEY AUTOINCREMENT, value TEXT NOT NULL)')
        cursor.execute('CREATE TABLE notes_tags (note_id INTEGER NOT NULL, tag_id INTEGER NOT NULL)')
        sql.commit()
        sql.close()

    def close(self):
        self.sql.close()

    def notes(self):
        cursor = self.sql.cursor()
        cursor.execute('SELECT * FROM notes')
        return ({'id': row[0], 'content': row[1]} for row in cursor)

    def tags(self):
        cursor = self.sql.cursor()
        cursor.execute('SELECT * FROM tags')
        return ({'id': row[0], 'value': row[1]} for row in cursor)

    def update_note(self, note_attrs):
        cursor = self.sql.cursor()
        cursor.execute('INSERT INTO notes (id, content) VALUES (?,?)', (note_attrs['id'], note_attrs['content']))
        if 'tag' in note_attrs and len(note_attrs['tag']) > 0:
            for tag in note_attrs['tag']:
                cursor.execute('INSERT INTO tags (value) VALUES (?)', (tag,))
                cursor.execute('INSERT INTO notes_tags (note_id, tag_id) VALUES (?,?)',
                               (note_attrs['id'], cursor.lastrowid))

        self.sql.commit()


class notes_store_session:
    def __enter__(self):
        self.store = NotesStore()
        return self.store

    def __exit__(self, *args):
        self.store.close()
