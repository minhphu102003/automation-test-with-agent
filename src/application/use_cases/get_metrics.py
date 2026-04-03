from typing import List
from src.infrastructure.monitoring.langfuse_reader import LangfuseReader
from src.presentation.schemas.automation import TestRunHistory, MetricsSummary

class GetHistoryUseCase:
    def __init__(self, reader: LangfuseReader):
        self.reader = reader

    def execute(self, limit: int = 50) -> List[TestRunHistory]:
        return self.reader.get_history(limit=limit)

class GetMetricsSummaryUseCase:
    def __init__(self, reader: LangfuseReader):
        self.reader = reader

    def execute(self) -> MetricsSummary:
        summary_data = self.reader.get_summary()
        return MetricsSummary(**summary_data)
