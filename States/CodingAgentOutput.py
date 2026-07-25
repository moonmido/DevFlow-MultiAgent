from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field


class GeneratedFile(BaseModel):
    path: str
    language: str
    content: str
    description: Optional[str] = None


class BuildCommand(BaseModel):
    command: str
    purpose: str


class CodingState(BaseModel):
    task_id: Optional[str] = None

    status: Literal[
        "success",
        "partial",
        "failed",
        "needs_information",
    ]

    implementation_summary: str

    generated_files: List[GeneratedFile] = Field(default_factory=list)

    created_files: List[str] = Field(default_factory=list)

    modified_files: List[str] = Field(default_factory=list)

    build_commands: List[BuildCommand] = Field(default_factory=list)

    dependencies: List[str] = Field(default_factory=list)

    environment_variables: Dict[str, str] = Field(default_factory=dict)

    implementation_notes: List[str] = Field(default_factory=list)

    assumptions: List[str] = Field(default_factory=list)

    blocking_issues: List[str] = Field(default_factory=list)

    compile_success: Optional[bool] = None

    lint_passed: Optional[bool] = None