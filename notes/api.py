import json

from .store import notes_store_session


class NotesAPI:

    def create(self, payload):
        with notes_store_session() as store:
            store.update_note(json.loads(payload))

    def update(self, payload):
        with notes_store_session() as store:
            store.update_note(json.loads(payload))

    def delete(self, id):
        with notes_store_session() as store:
            store.delete_note(id)

    def search(self, terms):
        with notes_store_session() as store:
            return store.match_notes(terms)
