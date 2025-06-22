import datetime

from profil_logger import CSVHandler, FileHandler, JsonHandler, SQLLiteHandler
from profil_logger.logger import LogEntry


def test_json_handler_can_persist_and_retrieve_log(tmp_path):
    path = tmp_path / "log.json"

    handler = JsonHandler(path)
    entry = LogEntry(
        datetime.datetime.now(), "ERROR", "JsonHandler test message"
    )
    handler.persist_log_json(entry)

    logs = handler.retrieve_all_logs_json()

    assert len(logs) == 1
    assert logs[0].message == "JsonHandler test message"
    assert logs[0].level == "ERROR"
    assert isinstance(logs[0].date, datetime.datetime)


def test_csv_handler_can_persist_and_retrieve_log(tmp_path):
    path = tmp_path / "log.csv"

    handler = CSVHandler(path)
    entry = LogEntry(
        datetime.datetime.now(), "WARNING", "CSVHandler test message"
    )
    handler.persist_log_csv(entry)

    logs = handler.retrieve_all_logs_csv()

    assert len(logs) == 1
    assert logs[0].message == "CSVHandler test message"
    assert logs[0].level == "WARNING"
    assert isinstance(logs[0].date, datetime.datetime)


def test_file_handler_can_persist_and_retrieve_log(tmp_path):
    path = tmp_path / "logfile.txt"
    handler = FileHandler(str(path))

    log_entry = LogEntry(
        datetime.datetime.now(), "INFO", "FileHandler test message"
    )
    handler.persist_log_file(log_entry)

    logs = handler.retrieve_all_logs_file()

    assert len(logs) == 1
    assert logs[0].message == "FileHandler test message"
    assert logs[0].level == "INFO"
    assert isinstance(logs[0].date, datetime.datetime)


def test_sqlite_handler_can_persist_and_retrieve_log(tmp_path):
    db_path = tmp_path / "logs.sqlite"
    handler = SQLLiteHandler(str(db_path))

    log_entry = LogEntry(
        datetime.datetime.now(), "ERROR", "SQLite test message"
    )
    handler.persist_log_sql(log_entry)

    logs = handler.retrieve_all_logs_sql()

    assert len(logs) == 1
    assert logs[0].message == "SQLite test message"
    assert logs[0].level == "ERROR"
    assert isinstance(logs[0].date, datetime.datetime)


def test_file_handler_ignores_invalid_lines(tmp_path):
    path = tmp_path / "logfile.txt"
    path.write_text("This is invalid log format\n")

    handler = FileHandler(str(path))
    logs = handler.retrieve_all_logs_file()

    assert logs == []


def test_sqlite_handler_missing_table(tmp_path):
    db_path = tmp_path / "logs.sqlite"
    handler = SQLLiteHandler(str(db_path))

    with handler._get_connection() as conn:
        conn.execute("DROP TABLE logs")

    logs = handler.retrieve_all_logs_sql()
    assert logs == []


def test_json_handler_empty_file(tmp_path):
    path = tmp_path / "empty.json"
    path.write_text("")

    handler = JsonHandler(path)
    logs = handler.retrieve_all_logs_json()
    assert logs == []


def test_csv_handler_empty_file(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("")

    handler = CSVHandler(path)
    logs = handler.retrieve_all_logs_csv()
    assert logs == []


def test_json_handler_overwrites_correctly(tmp_path):
    path = tmp_path / "log.json"
    handler = JsonHandler(path)

    first = LogEntry(datetime.datetime.now(), "DEBUG", "First")
    second = LogEntry(datetime.datetime.now(), "ERROR", "Second")

    handler.persist_log_json(first)
    handler.persist_log_json(second)

    logs = handler.retrieve_all_logs_json()
    assert len(logs) == 2


def test_csv_handler_ignores_invalid_rows(tmp_path):
    path = tmp_path / "log.csv"
    path.write_text("a,b,c,d,e\n")

    handler = CSVHandler(path)
    logs = handler.retrieve_all_logs_csv()

    assert logs == []


def test_sqlite_handler_invalid_data(tmp_path):
    db_path = tmp_path / "logs.sqlite"
    handler = SQLLiteHandler(str(db_path))

    with handler._get_connection() as conn:
        conn.execute(
            "INSERT INTO logs (timestamp, level, message) VALUES (?, ?, ?)",
            ("not-a-date", "INFO", "Bad entry"),
        )

    logs = handler.retrieve_all_logs_sql()
    assert logs == []
