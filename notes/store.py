import os
from sqlite3 import connect

import re


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
        id = note_attrs['id']
        content = note_attrs['content'] if 'content' in note_attrs else None

        cursor = self.sql.cursor()
        cursor.execute('SELECT id FROM notes WHERE id = ?', (id,))
        if not any(cursor):
            cursor.execute('INSERT INTO notes (id, content) VALUES (?,?)', (id, '' if content is None else content))
        elif content is not None:
            cursor.execute('UPDATE notes SET content = ? WHERE id = ?', (content, id))

        if 'tag' in note_attrs:
            self._clean_up_tags(cursor, id)
            for tag in note_attrs['tag']:
                cursor.execute('INSERT INTO tags (value) VALUES (?)', (tag,))
                cursor.execute('INSERT INTO notes_tags (note_id, tag_id) VALUES (?,?)',
                               (id, cursor.lastrowid))

        self.sql.commit()

    def delete_note(self, id):
        cursor = self.sql.cursor()
        self._clean_up_tags(cursor, id)
        cursor.execute('DELETE FROM notes WHERE id = ?', (id,))
        self.sql.commit()

    def match_content(self, term):
        root = term.rstrip('*')
        wildcard = '%{0}%'.format(root).lower()
        raw = [r[0] for r in self.sql.cursor().execute('SELECT content FROM notes WHERE LOWER(content) LIKE ?',
                                                       (wildcard,))]
        prog = re.compile(r'{0}{1}( |$)'.format(root, r'\w*' if term.endswith('*') else ''), re.IGNORECASE)
        return [s for s in raw if prog.search(s)]

    def _clean_up_tags(self, cursor, id):
        cursor.execute('DELETE FROM tags '
                       'WHERE id IN (SELECT tag_id FROM notes_tags WHERE note_id = ?) '
                       'AND (SELECT COUNT(*) FROM notes_tags WHERE tag_id = id) = 1', (id,))
        cursor.execute('DELETE FROM notes_tags WHERE note_id = ?', (id,))


class notes_store_session:
    def __enter__(self):
        self.store = NotesStore()
        return self.store

    def __exit__(self, *args):
        self.store.close()
