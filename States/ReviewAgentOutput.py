from typing import List, Literal
from pydantic import BaseModel, Field


class PhaseReview(BaseModel):
    score: float = Field(ge=0, le=100)

    strengths: List[str] = Field(default_factory=list)

    weaknesses: List[str] = Field(default_factory=list)

    issues: List[str] = Field(default_factory=list)

    recommendations: List[str] = Field(default_factory=list)


class OverallReview(BaseModel):
    overall_score: float = Field(ge=0, le=100)

    approval_status: Literal[
        "Approved",
        "Approved with Minor Changes",
        "Needs Revision",
        "Rejected",
    ]

    executive_summary: str

    top_strengths: List[str] = Field(default_factory=list)

    top_weaknesses: List[str] = Field(default_factory=list)

    highest_priority_recommendations: List[str] = Field(default_factory=list)


class ReviewState(BaseModel):
    task_id: str | None = None

    analysis: PhaseReview

    design: PhaseReview

    coding: PhaseReview

    testing: PhaseReview

    overall: OverallReview