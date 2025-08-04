import unittest
from unittest.mock import MagicMock, patch

from paramiko import SSHException, SSHClient
from paramiko.sftp_client import SFTPClient
from paramiko.sftp_file import SFTPFile

from wg_assistant.wireguard.client.remote import RemoteClient


class TestRemoteClient(unittest.TestCase):

    @patch('wg_assistant.wireguard.client.remote.SSHClient', autospec=True)
    def setUp(self, mock_ssh_client):
        self.mock_client_instance = MagicMock(spec=SSHClient)
        mock_ssh_client.return_value = self.mock_client_instance
        self.remote = RemoteClient(
            server='wg.example.com',
            port=22,
            username='root',
            password='password',
            key_filename='~/.ssh/id_ed25519',
        )

    def test_connect_called_on_init(self):
        self.mock_client_instance.connect.assert_called_once_with(
            hostname='wg.example.com',
            port=22,
            username='root',
            password='password',
            key_filename='~/.ssh/id_ed25519',
        )

    def test_execute_runs_command(self):
        self.remote.execute('ls')
        self.mock_client_instance.exec_command.assert_called_once_with('ls')

    def test_get_file_contents_reads_and_decodes(self):
        mock_file = MagicMock(spec=SFTPFile)
        mock_file.read.return_value = b'file content'

        mock_sftp = MagicMock(spec=SFTPClient)
        mock_sftp.file.return_value.__enter__.return_value = mock_file
        self.mock_client_instance.open_sftp.return_value = mock_sftp

        content = self.remote.get_file_contents('/etc/wireguard/wg0.conf')

        self.assertEqual(content, 'file content')
        mock_sftp.file.assert_called_once_with('/etc/wireguard/wg0.conf', mode='r')

    def test_put_file_contents_writes(self):
        mock_file = MagicMock(spec=SFTPFile)
        mock_sftp = MagicMock(spec=SFTPClient)
        mock_sftp.file.return_value.__enter__.return_value = mock_file
        self.mock_client_instance.open_sftp.return_value = mock_sftp

        self.remote.put_file_contents('/tmp/test.conf', 'some config')

        mock_file.write.assert_called_once_with('some config')
        mock_sftp.file.assert_called_once_with('/tmp/test.conf', mode='w')

    def test_retry_on_execute_failure(self):
        self.mock_client_instance.exec_command.side_effect = [SSHException(), 'ok']
        self.remote.connect = MagicMock(spec=SSHClient)

        self.remote.execute('ls')
        self.assertEqual(self.mock_client_instance.exec_command.call_count, 2)
        self.assertEqual(self.remote.connect.call_count, 1)

    def test_retry_on_get_file_failure(self):
        self.remote.connect = MagicMock(spec=SSHClient)
        sftp_mock = MagicMock(spec=SFTPClient)
        file_mock = MagicMock(spec=SFTPFile)
        file_mock.read.side_effect = [SSHException(), b'ok']
        sftp_mock.file.return_value.__enter__.return_value = file_mock
        self.mock_client_instance.open_sftp.return_value = sftp_mock

        self.remote.get_file_contents('/path/to/file')

        self.assertEqual(file_mock.read.call_count, 2)
        self.assertEqual(self.remote.connect.call_count, 1)

    def test_retry_on_put_file_failure(self):
        self.remote.connect = MagicMock(spec=SSHClient)
        sftp_mock = MagicMock(spec=SFTPClient)
        file_mock = MagicMock(spec=SFTPFile)
        file_mock.write.side_effect = [SSHException(), None]
        sftp_mock.file.return_value.__enter__.return_value = file_mock
        self.mock_client_instance.open_sftp.return_value = sftp_mock

        self.remote.put_file_contents('/path/to/file', 'data')

        self.assertEqual(file_mock.write.call_count, 2)
        self.assertEqual(self.remote.connect.call_count, 1)
