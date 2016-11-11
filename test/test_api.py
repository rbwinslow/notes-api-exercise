from notes.api import NotesAPI
from notes.store import notes_store_session


def test_create_inserts_database_record(clear_db):
    clear_db()

    api = NotesAPI()
    api.create('{"id": "12345678", "tag": ["alfa", "bravo"], "content": "Hello World"}')

    with notes_store_session() as store:

        all_notes = list(store.notes())
        assert len(all_notes) == 1
        assert all_notes[0]['id'] == 12345678
        assert all_notes[0]['content'] == 'Hello World'

        all_tags = list(store.tags())
        assert len(all_tags) == 2
        assert any(tag['value'] == 'alfa' for tag in all_tags)
        assert any(tag['value'] == 'bravo' for tag in all_tags)


def test_update_modifies_database_record_in_place(clear_db):
    clear_db()

    api = NotesAPI()
    api.create('{"id": "123", "content": "does not matter"}')
    api.update('{"id": "123", "content": "expected"}')

    with notes_store_session() as store:
        all_notes = list(store.notes())
        assert len(all_notes) == 1
        assert all_notes[0]['content'] == 'expected'


def test_delete_removes_note(clear_db):
    clear_db()

    api = NotesAPI()
    api.create('{"id": "42"}')
    api.delete('42')

    with notes_store_session() as store:
        assert len(list(store.notes())) == 0


def test_search_with_no_tag_prefix_matches_exact_words_in_content(clear_db):
    clear_db()

    api = NotesAPI()
    api.create('{"id": "1", "content": "Sweet Potato Pie"}')
    api.create('{"id": "2", "content": "Mash four potatoes together"}')
    actual = api.search('potato')

    assert len(actual) == 1
    assert actual[0] == 'Sweet Potato Pie'
