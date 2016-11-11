import os
from pytest import fixture
from sqlite3 import connect


@fixture
def clear_db():
    return lambda: os.remove('notes.db')


@fixture()
def notes_cursor():
    return lambda: connect('notes.db').cursor()


@fixture()
def table_columns(notes_cursor):
    return lambda name: [{'name': tuple[1], 'pk': tuple[5], 'type': tuple[2]}
                         for tuple in notes_cursor().execute('PRAGMA table_info("{0}")'.format(name))]
