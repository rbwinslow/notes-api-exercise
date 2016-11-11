
import sys

sys.path.append('..')
from cli import main


def test_cli_executes_create_command(mocker):
    expected_json = '{"id": "2", "content": "Hello, world!"}'

    (mocker.patch('cli.stdin')).readline = mocker.MagicMock(side_effect=['create\n', '{0}\n'.format(expected_json)])
    mock_create = mocker.Mock()
    mocker.patch('cli.NotesAPI', return_value=(mocker.Mock(create=mock_create)))

    main()

    mock_create.assert_called_with(expected_json)
