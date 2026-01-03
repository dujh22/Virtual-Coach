from dataclasses import dataclass
from typing import Any, Dict, List

from decision_trace import TraceStep
from logger import JsonlLogger

@dataclass
class PlanResult:
    workflow_draft: Dict[str, Any]
    confidence: float
    need_more_knowledge: bool
    knowledge_queries: List[Dict[str, Any]]
    decision_trace_step: TraceStep
    assumptions: List[str]


class BasePlanner:
    def plan(self, requirement: str, retrieved_docs: List[Dict[str, Any]], iteration: int) -> PlanResult:
        raise NotImplementedError

class LLMPlanner(BasePlanner):
    def __init__(self, logger: JsonlLogger):
        self.logger = logger

    def plan(self, requirement: str, retrieved_docs: List[Dict[str, Any]], iteration: int) -> PlanResult:
        raise NotImplementedError