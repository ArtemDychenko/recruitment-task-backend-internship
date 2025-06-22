import csv
import datetime
import json
import os
import sqlite3
from typing import List

from .logger import LogEntry


class JsonHandler:
    def __init__(self, filepath: str):
        """
        Initialize a JSON handler and create an empty
         JSON file if it doesn't exist.

        Args:
            filepath (str): Path to the JSON file.
        """
        self.filepath = filepath

        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as f:
                json.dump([], f)

    def persist_log_json(self, entry: LogEntry) -> None:
        """
        Append a log entry to the JSON file.

        Args:
            entry (LogEntry): The log entry to persist.
        """
        all_logs_data = []
        try:
            if (
                os.path.exists(self.filepath)
                and os.path.getsize(self.filepath) > 0
            ):
                with open(self.filepath, "r") as f_in:
                    all_logs_data = json.load(f_in)
        except (json.JSONDecodeError, FileNotFoundError):
            all_logs_data = []

        all_logs_data.append(entry.to_dict())

        with open(self.filepath, "w") as f_out:
            json.dump(all_logs_data, f_out, indent=4)

    def retrieve_all_logs_json(self) -> List[LogEntry]:
        """
        Retrieve all log entries from the JSON file.

        Returns:
            List[LogEntry]: List of log entries.
        """
        log_entries_list = []

        try:
            with open(self.filepath, "r") as f:
                data_dicts_list = json.load(f)
                for entry_dict_item in data_dicts_list:
                    log = LogEntry.from_dict(entry_dict_item)
                    if log:
                        log_entries_list.append(log)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

        return log_entries_list


class CSVHandler:
    HEADERS = ["date", "level", "message"]

    def __init__(self, filepath: str):
        """
        Initialize a CSV handler and create a file with
        headers if it doesn't exist.

        Args:
            filepath (str): Path to the CSV file.
        """
        self.filepath = filepath

        if (
            not os.path.exists(self.filepath)
            or os.path.getsize(self.filepath) == 0
        ):
            with open(self.filepath, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(self.HEADERS)

    def persist_log_csv(self, entry: LogEntry) -> None:
        """
        Append a log entry to the CSV file.

        Args:
            entry (LogEntry): The log entry to persist.
        """
        with open(self.filepath, "a", newline="") as f:
            writer = csv.writer(f)
            log_data_dict = entry.to_dict()
            writer.writerow(
                [
                    log_data_dict[self.HEADERS[0]],
                    log_data_dict[self.HEADERS[1]],
                    log_data_dict[self.HEADERS[2]],
                ]
            )

    def retrieve_all_logs_csv(self) -> List[LogEntry]:
        """
        Retrieve all log entries from the CSV file.

        Returns:
            List[LogEntry]: List of log entries.
        """
        log_entries_list = []

        try:
            with open(self.filepath, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row_as_dict in reader:
                    log = LogEntry.from_dict(row_as_dict)
                    if log:
                        log_entries_list.append(log)
        except FileNotFoundError:
            return []

        return log_entries_list


class FileHandler:
    def __init__(self, filepath: str):
        """
        Initialize a plain text file handler and create an
         empty file if it doesn't exist.

        Args:
            filepath (str): Path to the plain text log file.
        """
        self.filepath = filepath
        self.total_lines_written = 0
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as f:
                f.write("")

    def persist_log_file(self, entry: LogEntry) -> None:
        """
        Append a log entry as a single line to the plain text file.

        Args:
            entry (LogEntry): The log entry to persist.
        """
        log_line = f"{entry.date.isoformat()} {entry.level} {entry.message}\n"
        with open(self.filepath, "a") as f:
            f.write(log_line)
        self.total_lines_written += 1

    def retrieve_all_logs_file(self) -> List[LogEntry]:
        """
        Retrieve all log entries from the plain text file.

        Returns:
            List[LogEntry]: List of log entries.
        """
        log_entries_list = []

        try:
            with open(self.filepath, "r") as f:
                for line_content_str in f:
                    parts = line_content_str.strip().split(" ", 2)
                    if len(parts) == 3:
                        try:
                            log = LogEntry(
                                date=datetime.datetime.fromisoformat(parts[0]),
                                level=parts[1].upper(),
                                message=parts[2],
                            )
                            log_entries_list.append(log)
                        except ValueError:
                            continue
        except FileNotFoundError:
            return []
        return log_entries_list


class SQLLiteHandler:
    def __init__(self, db_path: str, table_name: str = "logs"):
        """
        Initialize an SQLite handler and ensure the logs table exists.

        Args:
            db_path (str): Path to the SQLite database file.
            table_name (str): Name of the logs table. Defaults to "logs".
        """
        self.db_path = db_path
        self.table_name = table_name
        self._create_table_if_not_exists()

    def _get_connection(self) -> sqlite3.Connection:
        """
        Establish a connection to the SQLite database.

        Returns:
            sqlite3.Connection: SQLite database connection.
        """
        return sqlite3.connect(self.db_path)

    def _create_table_if_not_exists(self) -> None:
        """
        Create the logs table in the database if it doesn't already exist.
        """
        with self._get_connection() as connect:
            cursor = connect.cursor()
            create_table_sql: str = f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL
                )
            """
            cursor.executescript(create_table_sql)

    def persist_log_sql(self, entry: LogEntry) -> None:
        """
        Insert a log entry into the SQLite database.

        Args:
            entry (LogEntry): The log entry to persist.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            sql_query: str = (
                f"INSERT INTO {self.table_name} (timestamp, level, message) "
                "VALUES (?, ?, ?)"
            )
            cursor.execute(
                sql_query, (entry.date.isoformat(), entry.level, entry.message)
            )

    def retrieve_all_logs_sql(self) -> List[LogEntry]:
        """
        Retrieve all log entries from the SQLite database.

        Returns:
            List[LogEntry]: List of log entries.
        """
        log_entries_list = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"SELECT timestamp, level, message FROM {self.table_name} "
                    "ORDER BY timestamp ASC"
                )
                for row in cursor.fetchall():
                    try:
                        log = LogEntry(
                            date=datetime.datetime.fromisoformat(row[0]),
                            level=row[1],
                            message=row[2],
                        )
                        if log:
                            log_entries_list.append(log)
                    except ValueError:
                        continue
        except (sqlite3.Error, ValueError):
            return []
        return log_entries_list
