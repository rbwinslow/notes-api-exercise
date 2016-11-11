import os
from sqlite3 import connect

import re


class NotesStore:
    _wild_suffix_pattern = re.compile(r'\*$')

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


    def match_notes(self, terms=None, tags=None):
        term_match_ids = None
        tag_match_ids = None

        if terms:
            term_match_ids = self._notes_matching_all_terms(terms)

        if tags:
            tag_match_ids = self._notes_matching_all_tags(tags)

        if term_match_ids is None:
            term_match_ids = tag_match_ids
        if tag_match_ids is None:
            tag_match_ids = term_match_ids
        return list(term_match_ids.intersection(tag_match_ids))


    def _clean_up_tags(self, cursor, id):
        cursor.execute('DELETE FROM tags '
                       'WHERE id IN (SELECT tag_id FROM notes_tags WHERE note_id = ?) '
                       'AND (SELECT COUNT(*) FROM notes_tags WHERE tag_id = id) = 1', (id,))
        cursor.execute('DELETE FROM notes_tags WHERE note_id = ?', (id,))


    def _make_likes(self, count, field, operator):
        clause = 'LOWER({0}) LIKE ?'.format(field)
        return ' {0} '.format(operator).join([clause for n in range(0, count)])


    def _notes_matching_all_terms(self, terms):
        wildcards = self._terms_to_sql_wildcards(terms)
        query = 'SELECT id, content FROM notes WHERE {0}'.format(self._make_likes(len(wildcards), 'content', 'AND'))
        rows = list(self.sql.cursor().execute(query, wildcards))

        progs = [re.compile(r'{0}( |$)'.format(self._wild_suffix_pattern.sub(r'\w*', term)), re.IGNORECASE)
                 for term in terms]
        return set(row[0] for row in rows if all(prog.search(row[1]) for prog in progs))


    def _notes_matching_all_tags(self, tags):
        cursor = self.sql.cursor()
        wildcards = self._terms_to_sql_wildcards(tags)
        query_format = 'SELECT notes.id FROM notes, notes_tags, tags ' \
                       'WHERE notes.id = notes_tags.note_id AND notes_tags.tag_id = tags.id AND {0}'
        query = query_format.format(self._make_likes(len(wildcards), 'tags.value', 'OR'))
        note_ids = set(row[0] for row in cursor.execute(query, wildcards))

        ids_with_tags = []
        query_format = 'SELECT tags.value FROM notes_tags, tags ' \
                       'WHERE notes_tags.note_id = {0} AND notes_tags.tag_id = tags.id'
        for id in note_ids:
            query = query_format.format(id)
            note_tags = [row[0] for row in cursor.execute(query)]
            ids_with_tags.append((id, ' '.join(note_tags)))

        progs = [re.compile(r'{0}( |$)'.format(self._wild_suffix_pattern.sub(r'\w*', tag)), re.IGNORECASE)
                 for tag in tags]
        return set(tpl[0] for tpl in ids_with_tags if all(prog.search(tpl[1]) for prog in progs))


    def _terms_to_sql_wildcards(self, terms):
        return ['%{0}%'.format(term.rstrip('*')).lower() for term in terms]



class notes_store_session:
    def __enter__(self):
        self.store = NotesStore()
        return self.store

    def __exit__(self, *args):
        self.store.close()
