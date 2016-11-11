import os
from pytest import fixture
from sqlite3 import connect


@fixture
def clear_db():
    def perform():
        if os.path.isfile('notes.db'):
            os.remove('notes.db')
    return perform


@fixture()
def mock_api(mocker):
    api_mock = mocker.Mock(**{m: mocker.Mock() for m in ('create', 'update', 'delete', 'search')})
    mocker.patch('notesapp.NotesAPI', return_value=api_mock)
    return api_mock


@fixture()
def mock_stdin(mocker):
    def perform(inputs):
        stdin_mock = mocker.patch('notesapp.stdin')
        stdin_mock.readline = mocker.MagicMock(side_effect=['{0}\n'.format(s) for s in inputs])
        isatty_calls = len(inputs) / 2
        stdin_mock.isatty = mocker.MagicMock(side_effect=[(n == isatty_calls - 1) for n in range(0, isatty_calls)])
    return lambda inputs: perform(inputs)


@fixture()
def notes_cursor():
    return lambda: connect('notes.db').cursor()


@fixture()
def table_columns(notes_cursor):
    return lambda name: [{'name': tuple[1], 'pk': tuple[5], 'type': tuple[2]}
                         for tuple in notes_cursor().execute('PRAGMA table_info("{0}")'.format(name))]
