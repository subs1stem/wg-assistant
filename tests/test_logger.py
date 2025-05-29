import logging
import sys

from wg_assistant.logger import setup_logging


def test_setup_logging(monkeypatch):
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    class DummyStream:
        def __init__(self):
            self.messages = []

        def write(self, msg):
            self.messages.append(msg)

        def flush(self):
            pass

    dummy_stdout = DummyStream()
    monkeypatch.setattr(sys, 'stdout', dummy_stdout)

    setup_logging('DEBUG')

    root_logger = logging.getLogger()
    aiogram_logger = logging.getLogger('aiogram.event')

    assert root_logger.level == logging.DEBUG
    assert aiogram_logger.level == logging.WARNING

    logging.debug('test debug message')
    assert any('test debug message' in msg for msg in dummy_stdout.messages)
