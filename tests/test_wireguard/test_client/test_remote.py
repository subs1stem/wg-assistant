import socket
from unittest.mock import MagicMock, patch

import pytest
from paramiko import SSHClient, SFTPClient, SFTPFile
from paramiko.ssh_exception import SSHException, NoValidConnectionsError

from wg_assistant.wireguard.client.remote import RemoteClient


@pytest.fixture
def mock_ssh_client():
    with patch('wg_assistant.wireguard.client.remote.SSHClient') as mock_ssh_client:
        mock_instance = MagicMock(spec=SSHClient)
        mock_ssh_client.return_value = mock_instance
        yield mock_instance


def test_init_calls_connect(mock_ssh_client):
    RemoteClient(server='wg.example.com', username='root')
    mock_ssh_client.set_missing_host_key_policy.assert_called_once()
    mock_ssh_client.connect.assert_called_once_with(
        hostname='wg.example.com',
        port=22,
        username='root',
        password=None,
        key_filename=None,
    )


def test_connect_raises_connection_error(mock_ssh_client):
    fake_addr = ('127.0.0.1', 22)
    fake_error = socket.error('connection refused')

    mock_ssh_client.connect.side_effect = NoValidConnectionsError(errors={fake_addr: fake_error})

    client = RemoteClient.__new__(RemoteClient)
    client.server = 'wg.example.com'
    client.port = 22
    client.username = 'root'
    client.password = None
    client.key_filename = None
    client.client = mock_ssh_client

    with pytest.raises(ConnectionError) as exc_info:
        client.connect()

    assert 'Error connecting to WireGuard server host' in str(exc_info.value)


def test_execute_success(mock_ssh_client):
    mock_ssh_client.exec_command.return_value = ('stdin', 'stdout', 'stderr')
    client = RemoteClient(server='wg.example.com', username='root')

    result = client.execute('ls')

    assert result == ('stdin', 'stdout', 'stderr')
    mock_ssh_client.exec_command.assert_called_once_with('ls')


def test_execute_retries_on_ssh_exception(mock_ssh_client):
    call_count = {'count': 0}

    def side_effect(*_, **__):
        if call_count['count'] == 0:
            call_count['count'] += 1
            raise SSHException('fail once')
        return 'in', 'out', 'err'

    mock_ssh_client.exec_command.side_effect = side_effect
    client = RemoteClient('host', username='user')

    result = client.execute('ls')

    assert result == ('in', 'out', 'err')
    assert mock_ssh_client.connect.call_count == 2


def test_get_file_contents(mock_ssh_client):
    mock_file = MagicMock(spec=SFTPFile)
    mock_sftp = MagicMock(spec=SFTPClient)

    mock_file.read.return_value = b'data123'
    mock_sftp.file.return_value.__enter__.return_value = mock_file

    mock_ssh_client.open_sftp.return_value = mock_sftp

    client = RemoteClient('host', username='user')
    content = client.get_file_contents('/tmp/file')
    assert content == 'data123'
    mock_sftp.file.assert_called_once_with('/tmp/file', mode='r')


def test_put_file_contents(mock_ssh_client):
    mock_sftp = MagicMock(spec=SFTPClient)
    mock_file = MagicMock(spec=SFTPFile)

    mock_sftp.file.return_value.__enter__.return_value = mock_file
    mock_ssh_client.open_sftp.return_value = mock_sftp

    client = RemoteClient('host', username='user')
    client.put_file_contents('/tmp/file', 'hello')
    mock_file.write.assert_called_once_with('hello')
    mock_sftp.file.assert_called_once_with('/tmp/file', mode='w')
