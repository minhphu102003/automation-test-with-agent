import mlflow
from typing import List, Dict, Any
from datetime import datetime
from src.presentation.schemas.automation import TestRunHistory, TokenUsage

class MLflowReader:
    def __init__(self, experiment_name: str = "Browser Automation Tests"):
        self.experiment_name = experiment_name
        self._experiment_id = self._get_experiment_id()

    def _get_experiment_id(self):
        exp = mlflow.get_experiment_by_name(self.experiment_name)
        return exp.experiment_id if exp else "0"

    def get_history(self, limit: int = 50) -> List[TestRunHistory]:
        runs = mlflow.search_runs(
            experiment_ids=[self._experiment_id],
            max_results=limit,
            order_by=["start_time DESC"]
        )
        
        history = []
        for _, run in runs.iterrows():
            # MLflow returns data as a pandas DataFrame row
            usage = TokenUsage(
                prompt_tokens=int(run.get("metrics.prompt_tokens", 0)),
                completion_tokens=int(run.get("metrics.completion_tokens", 0)),
                total_tokens=int(run.get("metrics.total_tokens", 0)),
                estimated_cost_usd=float(run.get("metrics.estimated_cost_usd", 0.0))
            )
            
            history.append(TestRunHistory(
                run_id=run["run_id"],
                task=run.get("params.task", "N/A"),
                model=run.get("params.model_name", "N/A"),
                status=run["status"],
                start_time=datetime.fromtimestamp(run["start_time"] / 1000.0),
                duration_seconds=float(run.get("metrics.duration_seconds", 0.0)),
                usage=usage,
                success=bool(run.get("metrics.success", 0))
            ))
            
        return history

    def get_summary(self) -> Dict[str, Any]:
        runs = mlflow.search_runs(experiment_ids=[self._experiment_id])
        if runs.empty:
            return {
                "total_runs": 0,
                "success_rate": 0,
                "total_cost_usd": 0,
                "total_tokens": 0,
                "avg_duration": 0
            }
            
        total_runs = len(runs)
        successes = runs[runs["metrics.success"] == 1]
        success_rate = (len(successes) / total_runs) * 100 if total_runs > 0 else 0
        
        return {
            "total_runs": total_runs,
            "success_rate": success_rate,
            "total_cost_usd": float(runs["metrics.estimated_cost_usd"].sum()),
            "total_tokens": int(runs["metrics.total_tokens"].sum()),
            "avg_duration": float(runs["metrics.duration_seconds"].mean())
        }
