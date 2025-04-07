from unittest.mock import patch

import pytest

from wg_assistant.config.env import get_bot_token, get_bot_admins


def test_missing_token():
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(RuntimeError) as exc_info:
            get_bot_token()
        assert str(exc_info.value) == 'Missing required environment variable: TOKEN'


def test_missing_admin_id():
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(RuntimeError) as exc_info:
            get_bot_admins()
        assert str(exc_info.value) == 'Missing required environment variable: ADMIN_ID'


def test_invalid_admin_id_format():
    invalid_values = ['1,b', '1,,2', '1,2,3,', '1, 2 3', 'a,b,c']

    for value in invalid_values:
        with patch.dict('os.environ', {'ADMIN_ID': value}, clear=True):
            with pytest.raises(RuntimeError) as exc_info:
                get_bot_admins()
            assert str(exc_info.value) == 'ADMIN_ID must contain comma-separated integers'


def test_valid_token_and_admins():
    with patch.dict('os.environ', {'TOKEN': 'valid_token', 'ADMIN_ID': '1,2, 3'}, clear=True):
        token = get_bot_token()
        admins = get_bot_admins()

        assert token == 'valid_token'
        assert admins == [1, 2, 3]
