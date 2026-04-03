from typing import Any, Dict, List
import uuid
from browser_use import AgentHistoryList
from config.pricing import COST_PER_1M_TOKENS, DEFAULT_PRICING 
from langfuse import Langfuse

def calculate_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    pricing = COST_PER_1M_TOKENS.get(model_name, DEFAULT_PRICING)
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost

class LangfuseBrowserLogger:
    def __init__(self, experiment_name: str = "Browser Automation"):
        self.experiment_name = experiment_name
        self.langfuse = Langfuse()

    def log_run(self, task: str, model_name: str, history: AgentHistoryList, run_id: str = None) -> float:
        """Logs the agent execution results and costs to Langfuse."""
        
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
                    print(f"Langfuse Warning: Could not extract tokens from step: {e}")
                    continue

        total_cost = calculate_cost(model_name, total_prompt_tokens, total_completion_tokens)
        duration = history.total_duration_seconds() if hasattr(history, 'total_duration_seconds') else 0.0
        success = 1 if history.is_successful() else 0

        if not run_id:
             run_id = str(uuid.uuid4())
             
        try:
            trace = self.langfuse.trace(
                id=run_id,
                name=f"Task: {task[:30]}...",
                tags=[self.experiment_name],
                metadata={
                    "task": task,
                    "model_name": model_name,
                    "total_steps": len(history.history),
                    "success": success,
                    "duration_seconds": duration,
                    "prompt_tokens": total_prompt_tokens,
                    "completion_tokens": total_completion_tokens,
                    "total_tokens": total_prompt_tokens + total_completion_tokens
                }
            )

            # Ingest generation to track models and usage accurately
            generation = trace.generation(
                name="browser_agent_execution",
                model=model_name,
                usage_details={
                    "input": total_prompt_tokens,
                    "output": total_completion_tokens,
                    "total": total_prompt_tokens + total_completion_tokens
                },
                cost_details={
                    "total": total_cost
                }
            )
            
            self.langfuse.flush()
        except Exception as e:
            print(f"Langfuse Logging Error: {e}")

        print("-" * 30)
        print(f"DEBUG - Langfuse Logging Results:")
        print(f"Model: {model_name}")
        print(f"Total Cost: ${total_cost:.6f}")
        print("-" * 30)

        return total_cost
