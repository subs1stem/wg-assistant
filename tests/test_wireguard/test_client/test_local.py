from wg_assistant.wireguard.client.local import LocalClient


def test_execute_returns_stdout_and_stderr():
    client = LocalClient()
    _, stdout, stderr = client.execute('echo "hello"')

    out = stdout.read().strip()
    err = stderr.read().strip()

    assert out == 'hello'
    assert err == ''


def test_execute_captures_stderr():
    client = LocalClient()
    _, stdout, stderr = client.execute('ls some_fake_file')

    out = stdout.read().strip()
    err = stderr.read().strip()

    assert out == ''
    assert err != ''


def test_get_file_contents_reads_correctly(tmp_path):
    path = tmp_path / 'test.txt'
    path.write_text('test content', encoding='utf-8')

    client = LocalClient()
    content = client.get_file_contents(str(path))

    assert content == 'test content'


def test_put_file_contents_writes_correctly(tmp_path):
    path = tmp_path / 'test.txt'

    client = LocalClient()
    client.put_file_contents(str(path), 'test content')

    content = path.read_text(encoding='utf-8')
    assert content == 'test content'
