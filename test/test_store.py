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


def test_store_update_modifies_existing_record_with_given_id_instead_of_trying_to_insert_new(clear_db, notes_cursor):
    expected = 'expected content'

    clear_db()
    with notes_store_session() as store:
        store.update_note({'id': '2', 'content': 'does not matter'})
        store.update_note({'id': '2', 'content': expected})

    notes = list(notes_cursor().execute('SELECT * FROM notes'))
    assert len(notes) == 1
    assert notes[0][1] == expected


def test_store_update_reassigns_tags_when_note_already_exists(clear_db, notes_cursor):
    expected = 'expected'

    clear_db()
    with notes_store_session() as store:
        store.update_note({'id': '42', 'tag': ['foo'], 'content': expected})
        store.update_note({'id': '42', 'tag': ['bar']})

    actual = next(notes_cursor().execute('SELECT content FROM notes, notes_tags, tags '
                                         'WHERE notes.id = notes_tags.note_id AND notes_tags.tag_id = tags.id '
                                         'AND tags.value = "bar"'))
    assert actual[0] == expected


def test_store_update_deletes_tag_relations_between_notes_and_old_tags(clear_db, notes_cursor):
    clear_db()
    with notes_store_session() as store:
        store.update_note({'id': '42', 'tag': ['foo']})
        store.update_note({'id': '42', 'tag': ['bar']})

    join = list(notes_cursor().execute('SELECT * FROM notes, notes_tags, tags '
                                       'WHERE notes.id = notes_tags.note_id AND notes_tags.tag_id = tags.id '
                                       'AND tags.value = "foo"'))
    assert len(join) == 0


def test_store_update_kills_tags_when_tags_attr_empty_list_but_does_nothing_when_no_tags_attr(clear_db, notes_cursor):
    clear_db()

    with notes_store_session() as store:
        store.update_note({'id': '99', 'tag': ['foo']})
        store.update_note({'id': '99', 'tag': []})
        store.update_note({'id': '100', 'tag': ['bar']})
        store.update_note({'id': '100', 'content': 'does not matter'})

    assert len(list(notes_cursor().execute('SELECT * FROM notes_tags WHERE note_id = 99'))) == 0
    assert len(list(notes_cursor().execute('SELECT * FROM notes_tags WHERE note_id = 100'))) == 1


def test_store_update_deletes_tags_that_are_no_longer_used(clear_db, notes_cursor):
    clear_db()

    with notes_store_session() as store:
        store.update_note({'id': '42', 'tag': ['foo']})
        store.update_note({'id': '42', 'tag': []})

    assert len(list(notes_cursor().execute('SELECT * FROM tags'))) == 0


def test_store_delete_removes_note(clear_db, notes_cursor):
    clear_db()

    with notes_store_session() as store:
        store.update_note({'id': 66})
        store.delete_note(66)

    assert len(list(notes_cursor().execute('SELECT * FROM notes'))) == 0


def test_store_delete_cleans_up_tags(clear_db, notes_cursor):
    clear_db()

    with notes_store_session() as store:
        store.update_note({'id': 99, 'tag': ['foo']})
        store.update_note({'id': 100, 'tag': ['foo', 'bar']})
        store.delete_note(100)

    tags = list(notes_cursor().execute('SELECT value FROM tags'))
    assert len(tags) == 1
    assert tags[0][0] == 'foo'

    links = list(notes_cursor().execute('SELECT notes_tags.note_id, tags.value FROM notes_tags, tags WHERE notes_tags.tag_id = tags.id'))
    assert len(links) == 1
    assert links[0][0] == 99
    assert links[0][1] == 'foo'


def test_store_matches_an_exact_word_in_content_without_case_sensitivity(clear_db):
    expected = 1

    clear_db()
    with notes_store_session() as store:
        store.update_note({'id': expected, 'content': 'Sweet Potato Pie'})
        store.update_note({'id': 2, 'content': 'Mash four potatoes together'})
        actual = store.match_notes(['potato'])

    assert len(actual) == 1
    assert actual[0] == expected


def test_store_matches_a_word_prefix_in_content(clear_db):
    clear_db()
    with notes_store_session() as store:
        store.update_note({'id': 1, 'content': 'Pot: Kettle; Kettle: Pot'})
        store.update_note({'id': 2, 'content': 'Sweet Potato Pie'})
        store.update_note({'id': 3, 'content': 'Does Not Matter'})
        actual = store.match_notes(['pOT*'])

    assert len(set(actual)) == 2


def test_store_matches_multiple_words_in_content(clear_db):
    expected = 1

    clear_db()
    with notes_store_session() as store:
        store.update_note({'id': expected, 'content': 'Potato Pancake'})
        store.update_note({'id': 2, 'content': 'potato pancakes'})
        store.update_note({'id': 3, 'content': 'potato'})
        actual = store.match_notes(['PANcake', 'poTATo'])

    assert len(actual) == 1
    assert actual[0] == expected


def test_store_matches_an_exact_tag_name_without_case_sensitivity(clear_db):
    expected = 1

    clear_db()
    with notes_store_session() as store:
        store.update_note({'id': expected, 'tag': ['Potato'], 'content': 'expected'})
        store.update_note({'id': 2, 'tag': ['potatoes'], 'content': 'not expected'})
        actual = store.match_notes(tags=['potato'])

    assert len(actual) == 1
    assert actual[0] == expected


def test_store_matches_tag_prefix(clear_db):
    clear_db()

    with notes_store_session() as store:
        store.update_note({'id': 1, 'tag': ['potato'], 'content': 'one'})
        store.update_note({'id': 2, 'tag': ['pot'], 'content': 'two'})
        store.update_note({'id': 3, 'tag': ['pancake'], 'content': 'three'})
        actual = store.match_notes(tags=['POT*'])

    assert len(set(actual)) == 2


def test_store_matches_multiple_tags(clear_db):
    clear_db()

    with notes_store_session() as store:
        store.update_note({'id': 1, 'tag': ['potato'], 'content': 'one'})
        store.update_note({'id': 2, 'tag': ['pot', 'pancake'], 'content': 'two'})
        store.update_note({'id': 3, 'tag': ['potato', 'pancake'], 'content': 'three'})
        store.update_note({'id': 4, 'tag': ['foobar', 'pancake'], 'content': 'four'})
        actual = store.match_notes(tags=['pot*', 'pancake'])

    assert len(set(actual)) == 2
    assert 2 in actual
    assert 3 in actual


def test_store_matches_combinations_of_tags_and_content_terms(clear_db):
    expected = 2

    clear_db()
    with notes_store_session() as store:
        store.update_note({'id': 1, 'content': 'pot content'})
        store.update_note({'id': expected, 'tag': ['pancake'], 'content': 'Potatoes are expected'})
        store.update_note({'id': 3, 'tag': ['pan'], 'content': 'does not matter'})
        actual = store.match_notes(terms=['pot*'], tags=['pan*'])

    assert len(set(actual)) == 1
    assert actual[0] == expected
