import datetime

from profil_logger.handlers import FileHandler
from profil_logger.logger import LogEntry, ProfilLogger


def test_logger_info_level_logged(tmp_path):
    path = tmp_path / "log.txt"

    handler = FileHandler(path)
    logger = ProfilLogger([handler])
    logger.info("Info message")

    with open(path, "r") as f:
        contents = f.read()

    assert "INFO Info message" in contents


def test_logger_debug_level_logged(tmp_path):
    path = tmp_path / "log.txt"

    handler = FileHandler(path)
    logger = ProfilLogger([handler])
    logger.debug("Debug message")

    with open(path, "r") as f:
        contents = f.read()

    assert "DEBUG Debug message" in contents


def test_logger_warning_level_logged(tmp_path):
    path = tmp_path / "log.txt"

    handler = FileHandler(path)
    logger = ProfilLogger([handler])
    logger.warning("Warning message")

    with open(path, "r") as f:
        contents = f.read()

    assert "WARNING Warning message" in contents


def test_logger_error_level_logged(tmp_path):
    path = tmp_path / "log.txt"

    handler = FileHandler(path)
    logger = ProfilLogger([handler])
    logger.error("Error message")

    with open(path, "r") as f:
        contents = f.read()

    assert "ERROR Error message" in contents


def test_logger_critical_level_logged(tmp_path):
    path = tmp_path / "log.txt"

    handler = FileHandler(path)
    logger = ProfilLogger([handler])
    logger.critical("Critical message")

    with open(path, "r") as f:
        contents = f.read()

    assert "CRITICAL Critical message" in contents


def test_logger_type_message_filtering(tmp_path):
    path = tmp_path / "log.txt"

    handler = FileHandler(path)
    logger = ProfilLogger([handler])
    logger.set_log_level("ERROR")
    logger.info("Info message")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    with open(path, "r") as f:
        contents = f.read()

    assert "INFO Info message" not in contents
    assert "DEBUG Debug message" not in contents
    assert "WARNING Warning message" not in contents

    assert "ERROR Error message" in contents
    assert "CRITICAL Critical message" in contents


def test_set_invalid_log_level(tmp_path):
    path = tmp_path / "log.txt"
    handler = FileHandler(str(path))

    logger = ProfilLogger([handler])
    logger.set_log_level("UNKNOWN")
    logger.debug("This should be logged")

    logs = handler.retrieve_all_logs_file()
    assert len(logs) == 1
    assert logs[0].message == "This should be logged"


def test_from_dict_missing_keys():
    bad_data = {"date": "2024-06-22T12:00:00", "message": "Hello"}
    result = LogEntry.from_dict(bad_data)
    assert result is None


def test_from_dict_invalid_date_format():
    bad_data = {"date": "22-06-2024", "level": "INFO", "message": "Bad date"}
    result = LogEntry.from_dict(bad_data)
    assert result is None


def test_from_dict_invalid_log_level():
    bad_data = {
        "date": "2024-06-22T12:00:00",
        "level": "TREX",
        "message": "Bad level",
    }
    result = LogEntry.from_dict(bad_data)
    assert result is None


def test_from_dict_invalid_types():
    bad_data = {"date": 12345, "level": "INFO", "message": "Wrong type"}
    result = LogEntry.from_dict(bad_data)
    assert result is None


def test_from_dict_valid_input():
    valid_data = {
        "date": "2024-06-22T12:00:00",
        "level": "INFO",
        "message": "All good",
    }
    result = LogEntry.from_dict(valid_data)
    assert isinstance(result, LogEntry)
    assert result.date == datetime.datetime.fromisoformat(
        "2024-06-22T12:00:00"
    )
    assert result.level == "INFO"
    assert result.message == "All good"
