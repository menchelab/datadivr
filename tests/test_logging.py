from datadivr.utils.logging import get_logger, setup_logging


def test_setup_logging():
    setup_logging()
    logger = get_logger("test")
    assert logger is not None


def test_get_logger():
    logger1 = get_logger("test1")
    logger2 = get_logger("test2")
    assert logger1 != logger2
    assert logger1.name == "test1"
    assert logger2.name == "test2"
