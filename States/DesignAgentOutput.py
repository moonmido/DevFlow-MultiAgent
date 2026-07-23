from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class Component(BaseModel):
    name: str
    responsibility: str
    dependencies: List[str] = Field(default_factory=list)


class Module(BaseModel):
    name: str
    responsibility: str
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)


class APIDesign(BaseModel):
    required: bool
    endpoints: List[Dict] = Field(default_factory=list)


class DatabaseDesign(BaseModel):
    required: bool
    entities: List[Dict] = Field(default_factory=list)


class DesignState(BaseModel):
    task_id: Optional[str] = None

    architecture_style: str
    architecture_reasoning: str

    components: List[Component] = Field(default_factory=list)
    modules: List[Module] = Field(default_factory=list)

    data_flow: List[str] = Field(default_factory=list)

    api_design: APIDesign
    database_design: DatabaseDesign

    class_design: List[Dict] = Field(default_factory=list)
    design_patterns: List[str] = Field(default_factory=list)
    algorithms: List[str] = Field(default_factory=list)

    security: List[str] = Field(default_factory=list)
    performance: List[str] = Field(default_factory=list)
    scalability: List[str] = Field(default_factory=list)

    folder_structure: List[str] = Field(default_factory=list)

    testing_strategy: Dict = Field(default_factory=dict)

    development_phases: List[str] = Field(default_factory=list)

    coding_guidelines: List[str] = Field(default_factory=list)

    implementation_notes: List[str] = Field(default_factory=list)

    coding_handoff: str

    confidence_score: float = 0.0