from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class Risk(BaseModel):
    title: str
    severity: str  # Low | Medium | High
    mitigation: str


class AnalysisState(BaseModel):
    # Metadata
    task_id: Optional[str] = None
    user_query: str

    # Summary
    problem_summary: str
    objectives: List[str] = Field(default_factory=list)

    # Requirements
    functional_requirements: List[str] = Field(default_factory=list)
    non_functional_requirements: List[str] = Field(default_factory=list)

    # Data
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)

    # Constraints
    constraints: List[str] = Field(default_factory=list)

    # Assumptions
    assumptions: List[str] = Field(default_factory=list)

    # Dependencies
    dependencies: List[str] = Field(default_factory=list)

    # Risks
    risks: List[Risk] = Field(default_factory=list)

    # Edge Cases
    edge_cases: List[str] = Field(default_factory=list)

    # Research
    knowledge_sources: List[str] = Field(default_factory=list)
    web_references: List[str] = Field(default_factory=list)

    # Success Criteria
    success_criteria: List[str] = Field(default_factory=list)

    # Handoff
    design_handoff: str

    # Confidence
    confidence_score: float = 0.0

    # Missing Information
    open_questions: List[str] = Field(default_factory=list)

    # Status
    status: str = "completed"