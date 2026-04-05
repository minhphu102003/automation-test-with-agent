from langchain_openai import ChatOpenAI
from config.pricing import DEFAULT_MODEL
from src.prompts.analyzer_prompts import VISION_CLASSIFIER_PROMPT
import os

class LLMTaskAnalyzer:
    def __init__(self, model_name: str = DEFAULT_MODEL):
        # We always use a cheap model for analysis for cost-efficiency
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.prompt = VISION_CLASSIFIER_PROMPT

    async def requires_vision(self, task: str) -> bool:
        """Determines if the task requires vision-based processing."""
        try:
            chain = self.prompt | self.llm
            response = await chain.ainvoke({"task": task})
            decision = response.content.strip().upper()
            
            print(f"--- Smart Analyzer Decision for task '{task[:50]}...': {decision} ---")
            return decision == "YES"
        except Exception as e:
            print(f"--- Warning: Smart Analyzer Failed: {e}. Defaulting to YES ---")
            return True # Safe default
