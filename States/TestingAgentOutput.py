from typing import Literal, Optional
from pydantic import BaseModel


class GeneratedTestFile(BaseModel):
    path: str
    language: str
    description: str


class TestingState(BaseModel):
    task_id: Optional[str] = None

    status: Literal[
        "success",
        "partial_success",
        "failed"
    ]

    testing_summary: str

    generated_test_files: list[GeneratedTestFile]

    created_files: list[str]

    modified_files: list[str]

    deleted_files: list[str]

    testing_framework: str

    estimated_test_count: int

    tested_components: list[str]

    assumptions: list[str]

    implementation_notes: list[str]

    blocking_issues: list[str]