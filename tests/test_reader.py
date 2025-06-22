import datetime
from profil_logger.logger import LogEntry
from profil_logger.logger import ProfilLoggerReader


class DummyHandler:
    def retrieve_all_logs_file(self):
        return [
            LogEntry(datetime.datetime(2024, 1, 1), "INFO", "hello"),
            LogEntry(datetime.datetime(2024, 1, 2), "ERROR", "crash"),
            LogEntry(datetime.datetime(2024, 2, 1), "INFO", "ok"),
        ]


def test_group_by_month():
    reader = ProfilLoggerReader(DummyHandler())
    result = reader.group_by_month()
    assert "2024-01" in result
    assert len(result["2024-01"]) == 2


def test_group_by_level():
    reader = ProfilLoggerReader(DummyHandler())
    result = reader.group_by_level()

    assert "INFO" in result
    assert "ERROR" in result
    assert len(result["INFO"]) == 2


def test_find_by_text():
    reader = ProfilLoggerReader(DummyHandler())
    result = reader.find_by_text("hello")

    assert len(result) == 1
    assert result[0].message == "hello"


def test_find_by_regex():
    reader = ProfilLoggerReader(DummyHandler())
    result = reader.find_by_regex(r"cr.*")

    assert len(result) == 1
    assert result[0].level == "ERROR"
