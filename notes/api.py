import json

from .store import notes_store_session


class NotesAPI:

    def create(self, payload):
        with notes_store_session() as store:
            store.update_note(json.loads(payload))