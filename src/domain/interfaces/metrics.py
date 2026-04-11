from abc import ABC, abstractmethod
from typing import List

from src.domain.models.metrics import MetricsSummary, TestRunHistory


class IMetricsReader(ABC):
    @abstractmethod
    def get_history(self, limit: int = 50) -> List[TestRunHistory]:
        """Return the latest execution history entries."""

    @abstractmethod
    def get_summary(self) -> MetricsSummary:
        """Return aggregate execution metrics."""
