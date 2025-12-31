from dataclasses import dataclass
from typing import Any, Dict, List

from .decision_trace import TraceStep

@dataclass
class PlanResult:
    workflow_draft: Dict[str, Any]
    confidence: float
    need_more_knowledge: bool
    knowledge_queries: List[Dict[str, Any]]
    decision_trace_step: TraceStep
    assumptions: List[str]
