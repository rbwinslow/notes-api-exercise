import os

from notes.store import NotesStore, notes_store_session


def test_store_initializes_schema_when_file_not_present(clear_db, table_columns):
    clear_db()

    NotesStore()

    assert os.path.isfile('notes.db')

    cols = table_columns('notes')
    assert any(col['name'] == 'id' for col in cols)
    assert any(col['name'] == 'content' for col in cols)

    id_col = next(col for col in cols if col['name'] == 'id')
    assert id_col['type'] == 'INTEGER'
    assert id_col['pk'] == 1
    content_col = next(col for col in cols if col['name'] == 'content')
    assert content_col['type'] == 'TEXT'
    assert content_col['pk'] == 0

    cols = table_columns('tags')
    assert any(col['name'] == 'id' for col in cols)
    assert any(col['name'] == 'value' for col in cols)

    id_col = next(col for col in cols if col['name'] == 'id')
    assert id_col['type'] == 'INTEGER'
    assert id_col['pk'] == 1
    value_col = next(col for col in cols if col['name'] == 'value')
    assert value_col['type'] == 'TEXT'
    assert value_col['pk'] == 0

    cols = table_columns('notes_tags')
    assert any(col['name'] == 'note_id' for col in cols)
    assert any(col['name'] == 'tag_id' for col in cols)


def test_store_update_creates_note_record(clear_db, notes_cursor):
    expected_id = 1
    expected_content = 'foo bar'

    clear_db()
    with notes_store_session() as store:
        store.update_note({'id': expected_id, 'content': expected_content})

    notes = list(notes_cursor().execute('SELECT * FROM notes'))
    assert len(notes) == 1
    assert notes[0][0] == expected_id
    assert notes[0][1] == expected_content


def test_store_update_with_a_tag_creates_a_tag_record(clear_db, notes_cursor):
    clear_db()
    with notes_store_session() as store:
        store.update_note({'id': '123', 'tag': ['foo'], 'content': 'does not matter'})

    tags = list(notes_cursor().execute('SELECT * FROM tags'))
    assert len(tags) == 1
    assert tags[0][1] == 'foo'
    tag_id = tags[0][0]

    links = list(notes_cursor().execute('SELECT * FROM notes_tags'))
    assert len(links) == 1
    assert links[0][0] == 123
    assert links[0][1] == tag_id
