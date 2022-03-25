#!/usr/bin/env python


import pytest
import logging
from _pytest.logging import caplog as _caplog
from starter.loggerdef import logger
from starter import utils


collect_ignore = [
        # "test_init.py",
        # "test_utils.py",
        # "test_version.py",
        ]


# Making pytest caplog work with loguru
# https://loguru.readthedocs.io/en/stable/resources/migration.html?highlight=pytest#making-things-work-with-pytest-and-caplog
@pytest.fixture
def caplog(_caplog):
    class PropagateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)
    # handler_id = logger.add(PropagateHandler(), level="TRACE", format="{message} {extra}")
    handler_id = logger.add(PropagateHandler(), level="TRACE", format="{message}")
    yield _caplog
    logger.remove(handler_id)
