from datetime import datetime


class ApiHistoryRecord:

    def __init__(self, api_name: str, success: bool, duration_ms: int, message: str) -> None:
        self.api_name = api_name
        self.success = success
        self.duration_ms = duration_ms
        self.message = message
        self.called_at = datetime.now()


class ApiHistoryManager:

    def __init__(self) -> None:
        self._records: list[ApiHistoryRecord] = []

    def add(self, api_name: str, success: bool, duration_ms: int = 0, message: str = '') -> None:
        self._records.append(ApiHistoryRecord(api_name, success, duration_ms, message))

    def flush(self) -> list[ApiHistoryRecord]:
        records = self._records[:]
        self._records.clear()
        return records
