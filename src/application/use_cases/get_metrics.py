from typing import List

from src.domain.interfaces.metrics import IMetricsReader
from src.domain.models.metrics import MetricsSummary, TestRunHistory

class GetHistoryUseCase:
    def __init__(self, reader: IMetricsReader):
        self.reader = reader

    def execute(self, limit: int = 50) -> List[TestRunHistory]:
        return self.reader.get_history(limit=limit)

class GetMetricsSummaryUseCase:
    def __init__(self, reader: IMetricsReader):
        self.reader = reader

    def execute(self) -> MetricsSummary:
        return self.reader.get_summary()
