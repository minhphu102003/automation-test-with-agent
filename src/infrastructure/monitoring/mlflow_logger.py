import mlflow
from typing import Any, Dict, List
from browser_use import AgentHistoryList
from config.pricing import COST_PER_1M_TOKENS, DEFAULT_PRICING # This is still correct relative to root

def calculate_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    pricing = COST_PER_1M_TOKENS.get(model_name, DEFAULT_PRICING)
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost

class MLflowBrowserLogger:
    def __init__(self, experiment_name: str = "Browser Automation"):
        mlflow.set_experiment(experiment_name)

    def log_run(self, task: str, model_name: str, history: AgentHistoryList):
        """Logs the agent execution results and costs to MLflow."""
        with mlflow.start_run(run_name=f"Task: {task[:30]}..."):
            mlflow.log_param("task", task)
            mlflow.log_param("model_name", model_name)
            
            total_prompt_tokens = 0
            total_completion_tokens = 0
            
            if hasattr(history, 'usage') and history.usage:
                total_prompt_tokens = getattr(history.usage, 'total_prompt_tokens', 0)
                total_completion_tokens = getattr(history.usage, 'total_completion_tokens', 0)
            
            if total_prompt_tokens == 0:
                for step in history.history:
                    try:
                        output = step.model_output
                        if not output: continue
                        
                        if hasattr(output, 'usage') and output.usage:
                            total_prompt_tokens += getattr(output.usage, 'prompt_tokens', 0)
                            total_completion_tokens += getattr(output.usage, 'completion_tokens', 0)
                        elif hasattr(output, 'response_metadata') and output.response_metadata:
                            usage = output.response_metadata.get('token_usage', {})
                            total_prompt_tokens += usage.get('prompt_tokens', 0)
                            total_completion_tokens += usage.get('completion_tokens', 0)
                        elif hasattr(output, 'usage_metadata') and output.usage_metadata:
                            total_prompt_tokens += output.usage_metadata.get('input_tokens', 0)
                            total_completion_tokens += output.usage_metadata.get('output_tokens', 0)
                    except Exception as e:
                        print(f"MLflow Warning: Could not extract tokens from step: {e}")
                        continue

            total_cost = calculate_cost(model_name, total_prompt_tokens, total_completion_tokens)
            
            metrics = {
                "total_steps": len(history.history),
                "duration_seconds": history.total_duration_seconds(),
                "success": 1 if history.is_successful() else 0,
                "prompt_tokens": total_prompt_tokens,
                "completion_tokens": total_completion_tokens,
                "total_tokens": total_prompt_tokens + total_completion_tokens,
                "estimated_cost_usd": total_cost,
            }
            mlflow.log_metrics(metrics)

            print("-" * 30)
            print(f"DEBUG - MLflow Logging Results (Refactored):")
            print(f"Model: {model_name}")
            print(f"Total Cost: ${total_cost:.6f}")
            print("-" * 30)

        return total_cost
