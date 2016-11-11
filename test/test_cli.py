
import sys

from mock import call

sys.path.append('..')
from notesapp import main


def test_cli_executes_create_command(clear_db, mock_api, mock_stdin):
    expected_json = '{"id": "2", "content": "Hello, world!"}'
    mock_stdin(['create', expected_json])

    clear_db()
    main()

    mock_api.create.assert_called_with(expected_json)


def test_cli_commands_are_case_insensitive(mock_api, mock_stdin):
    expected_json = '{"id": "4758392"}'
    mock_stdin(['CREate', expected_json])
    main()
    mock_api.create.assert_called_with(expected_json)


def test_cli_accepts_multiple_commands(clear_db, mock_api, mock_stdin):
    expected_first = '{"id": "1"}'
    expected_second = '{"id": "2"}'
    mock_stdin(['create', expected_first, 'create', expected_second])

    clear_db()
    main()

    mock_api.create.assert_has_calls([call(expected_first), call(expected_second)])


def test_cli_search_command_prints_results_to_stdout(mock_api, mock_stdin, capsys):
    expected_term = 'expected_term'
    mock_stdin(['search', expected_term])
    mock_api.search.return_value = [1, 2]

    main()

    mock_api.search.assert_called_with(expected_term)
    actual, _ = capsys.readouterr()
    assert actual == '1, 2\n'
