from typing import Any, Dict, List, Optional, TypedDict


class WorkflowState(TypedDict, total=False):
    user_query: str
    task_id: str

    current_phase: str
    status: str

    iterations: int
    max_iterations: int

    review_outcome: str
    review_target: str
    revision_reason: str

    error: Optional[str]

    analysis: Optional[Dict[str, Any]]
    design: Optional[Dict[str, Any]]
    coding: Optional[Dict[str, Any]]
    testing: Optional[Dict[str, Any]]
    review: Optional[Dict[str, Any]]

    logs: List[str]
