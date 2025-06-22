# Profil Logger – Refactored Logging Library

This is a flexible and modular logging library designed for various output formats.

---

## Main Components

| Component             | Description                                      |
|-----------------------|--------------------------------------------------|
| `ProfilLogger`        | Core logger that emits log entries to handlers   |
| `ProfilLoggerReader`  | Log reader with powerful filtering/grouping      |
| `LogEntry`            | Structured representation of a single log line   |
| `JsonHandler`         | Reads/writes logs in JSON format                 |
| `CSVHandler`          | Handles CSV-based logging                        |
| `FileHandler`         | Writes logs to a plain text file                 |
| `SQLLiteHandler`      | Persists logs into an SQLite database            |

---

## Features

- Logging levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- Pluggable storage handlers (CSV, JSON, SQLite, text file)
- Query logs by:
  - Full-text search
  - Regex pattern
  - Date range
  - Grouping by **log level** or **month**

---

## Requirements

- Python **3.12+**

---


# Usage Examples

## Logging to CSV

```python
from profil_logger import ProfilLogger, CSVHandler

logger = ProfilLogger(handlers=[CSVHandler("logs.csv")])
logger.info("Application started")
logger.error("Something went wrong")
```

## Reading Logs by Regex from SQLite
```python
from profil_logger import ProfilLogger, SQLLiteHandler, ProfilLoggerReader

sqlite_handler = SQLLiteHandler("logs.db")
logger = ProfilLogger([sqlite_handler])

logger.info("Info message")
logger.error("Something went wrong")
logger.warning("Watch out!")
logger.debug("Debug start")
logger.critical("Critical failure")

reader = ProfilLoggerReader(sqlite_handler)
matches = reader.find_by_regex(r"error|fail")

for entry in matches:
    print(entry)
```

---


# Project Structure

    profil_logger/
    ├── handlers.py            # Storage backends (CSV, JSON, File, SQLite)
    ├── logger.py              # Main logger and reader logic
    ├── __init__.py            # Package exports
    tests/
    ├── test_handlers.py       # Unit tests for all handlers
    ├── test_logger.py         # Tests for ProfilLogger and reader
    pyproject.toml             # Ruff configuration