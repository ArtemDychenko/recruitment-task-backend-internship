import datetime
from profil_logger.logger import LogEntry


def test_logentry_to_dict_and_from_dict():
    now = datetime.datetime.now()
    entry = LogEntry(date=now, level="INFO", msg="Test")
    data = entry.to_dict()
    assert data["date"] == now.isoformat()
    assert data["level"] == "INFO"
    assert data["msg"] == "Test"

    recreated = LogEntry.from_dict(data)
    assert recreated.date == now
    assert recreated.level == "INFO"
    assert recreated.message == "Test"
