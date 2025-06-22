import datetime
import logging
import re
from collections import defaultdict
from typing import Any, Dict, List, Literal, Optional

logger = logging.getLogger(__name__)

LogLevelLiteral = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

LOG_LEVEL_VALUES = {
    "DEBUG": 0,
    "INFO": 1,
    "WARNING": 2,
    "ERROR": 3,
    "CRITICAL": 4,
}

DEFAULT_LOG_LEVEL: LogLevelLiteral = "DEBUG"


class LogEntry:
    def __init__(
        self, date: datetime.datetime, level: LogLevelLiteral, message: str
    ):
        """
        Initialize a log entry.

        Args:
            date (datetime.datetime): The timestamp of the log.
            level (LogLevelLiteral): The log level (e.g. "INFO", "ERROR").
            message (str): The log message.
        """
        self.date = date
        self.level = level
        self.message = message

    def __repr__(self):
        """
        Return a developer-friendly string representation of the log entry.

        Returns:
             str: String representation of the log entry.
        """
        return (
            f"LogEntry(date={self.date.isoformat()}, "
            f"level='{self.level}', message='{self.message}')"
        )

    def to_dict(self) -> dict:
        """
        Convert the LogEntry to a dictionary format.

        Returns:
            dict: Dictionary with keys "date", "level", "message".
        """
        return {
            "date": self.date.isoformat(),
            "level": self.level,
            "message": self.message,
        }

    @staticmethod
    def from_dict(data: Dict[str, LogLevelLiteral]) -> Optional["LogEntry"]:
        """
        Create a LogEntry instance from a dictionary.

        Args:
            data (dict): A dictionary with keys "date", "level" and "message".

        Returns:
            Optional[LogEntry]: The created LogEntry or None if parsing failed.
        """
        required_keys = {"date", "level", "message"}
        if not required_keys.issubset(data):
            logger.warning(
                "Missing keys in log data: expected %s, got %s",
                required_keys,
                data.keys(),
            )
            return None

        try:
            date = datetime.datetime.fromisoformat(data["date"])
            level = data["level"]
            message = data["message"]

            if level not in LOG_LEVEL_VALUES:
                logger.warning("Invalid log level: %s", level)
                return None

            return LogEntry(date=date, level=level, message=message)
        except (ValueError, TypeError) as e:
            logger.error("Invalid log entry format: %s", e)
            return None


class ProfilLogger:
    def __init__(self, handlers: List[Any]):
        """
        Initialize the logger with a list of handlers.

        Args:
            handlers (List[Any]): List of handler objects to write logs to.
        """
        self.handlers = handlers
        self.current_log_level_val = LOG_LEVEL_VALUES[DEFAULT_LOG_LEVEL]

    def _log(self, level: LogLevelLiteral, message: str):
        """
        Create a log entry and send it to all applicable handlers.

        Args:
            level (LogLevelLiteral): Log level of the message.
            message (str): The log message.
        """
        if LOG_LEVEL_VALUES[level] < self.current_log_level_val:
            return
        entry = LogEntry(
            date=datetime.datetime.now(), level=level, message=message
        )
        for handler_item in self.handlers:
            self._write_to_handler(handler_item, entry)

    @staticmethod
    def _write_to_handler(handler: Any, entry: LogEntry):
        """
        Attempt to write a log entry using available persist
        methods on a handler.

        Args:
            handler (Any): The handler to use.
            entry (LogEntry): The log entry to persist.
        """
        persist_methods = [
            "persist_log_sql",
            "persist_log_json",
            "persist_log_csv",
            "persist_log_file",
        ]

        last_exception = None

        for method_name in persist_methods:
            method = getattr(handler, method_name, None)
            if callable(method):
                try:
                    method(entry)
                    return
                except Exception as e:
                    last_exception = e
                    continue

        logger.error(
            "All handlers failed. Final error on %s: %s",
            type(handler).__name__,
            last_exception,
        )

    def info(self, message: str):
        self._log("INFO", message)

    def warning(self, message: str):
        self._log("WARNING", message)

    def critical(self, message: str):
        self._log("CRITICAL", message)

    def error(self, message: str):
        self._log("ERROR", message)

    def debug(self, message: str):
        self._log("DEBUG", message)

    def set_log_level(self, level: LogLevelLiteral):
        """
        Set the minimum log level.

        Args:
            level (LogLevelLiteral): New minimum level (e.g. "WARNING").
        """
        self.current_log_level_val = LOG_LEVEL_VALUES.get(
            level.upper(), self.current_log_level_val
        )


class ProfilLoggerReader:
    def __init__(self, handler: Any):
        """
        Initialize the reader with a specific log handler.

        Args:
            handler (Any): Handler to read logs from.
        """
        self.handler = handler

    def _get_all_logs_from_handler(self) -> List[LogEntry]:
        """
        Attempt to retrieve all logs using available read methods.

        Returns:
            List[LogEntry]: List of retrieved log entries (empty if failed).
        """
        retrieve_methods = [
            "retrieve_all_logs_sql",
            "retrieve_all_logs_json",
            "retrieve_all_logs_csv",
            "retrieve_all_logs_file",
        ]

        for method_name in retrieve_methods:
            method = getattr(self.handler, method_name, None)
            if callable(method):
                try:
                    return method()
                except AttributeError:
                    continue

        logger.error(
            "Handler %s has no recognized retrieval method.",
            type(self.handler).__name__,
        )
        return []

    @staticmethod
    def _filter_by_date(
        logs: List[LogEntry],
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None,
    ) -> List[LogEntry]:
        """
        Filter logs by an optional date range.

        Args:
            logs (List[LogEntry]): Logs to filter.
            start_date (datetime.datetime, optional): Start of date range.
            end_date (datetime.datetime, optional): End of date range.

        Returns:
            List[LogEntry]: Filtered list of log entries.
        """
        return [
            log
            for log in logs
            if (not start_date or log.date >= start_date)
            and (not end_date or log.date < end_date)
        ]

    def find_by_text(
        self,
        text: str,
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None,
    ) -> List[LogEntry]:
        """
        Search logs for entries that contain a given text.

        Args:
            text (str): Text to search for.
            start_date (datetime.datetime, optional): Start of date range.
            end_date (datetime.datetime, optional): End of date range.

        Returns:
            List[LogEntry]: List of matching log entries.
        """
        all_logs = self._get_all_logs_from_handler()
        result_logs = [log for log in all_logs if text in log.message]
        return self._filter_by_date(result_logs, start_date, end_date)

    def find_by_regex(
        self,
        regex: str,
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None,
    ) -> List[LogEntry]:
        """
        Search logs using a regular expression.

        Args:
            regex (str): Regex pattern to match in log messages.
            start_date (datetime.datetime, optional): Start of date range.
            end_date (datetime.datetime, optional): End of date range.

        Returns:
            List[LogEntry]: List of matching log entries.
        """
        all_logs = self._get_all_logs_from_handler()
        try:
            pattern = re.compile(regex)
            matching_logs = [
                log for log in all_logs if pattern.search(log.message)
            ]
            return self._filter_by_date(matching_logs, start_date, end_date)
        except re.error:
            return []

    def group_by_level(
        self,
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None,
    ) -> Dict[str, List[LogEntry]]:
        """
        Group logs by their log level.

        Args:
            start_date (datetime.datetime, optional): Start of date range.
            end_date (datetime.datetime, optional): End of date range.

        Returns:
            Dict[str, List[LogEntry]]: Dictionary with log levels as keys.
        """
        all_logs = self._get_all_logs_from_handler()
        logs_to_group = self._filter_by_date(all_logs, start_date, end_date)

        grouped = defaultdict(list)
        for log in logs_to_group:
            grouped[log.level].append(log)
        return dict(grouped)

    def group_by_month(
        self,
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None,
    ) -> Dict[str, List[LogEntry]]:
        """
        Group logs by month of their date.

        Args:
            start_date (datetime.datetime, optional): Start of date range.
            end_date (datetime.datetime, optional): End of date range.

        Returns:
            Dict[str, List[LogEntry]]: Dictionary with YYYY-MM as keys.
        """
        all_logs = self._get_all_logs_from_handler()
        logs_to_group = self._filter_by_date(all_logs, start_date, end_date)

        grouped = defaultdict(list)
        for log in logs_to_group:
            key = log.date.strftime("%Y-%m")
            grouped[key].append(log)
        return dict(grouped)
