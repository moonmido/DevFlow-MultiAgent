from typing import Any, Dict


def mock_analysis(state: Dict[str, Any]) -> Dict[str, Any]:
    query = state.get("user_query", "Build a project")
    return {
        "task_id": state.get("task_id"),
        "user_query": query,
        "problem_summary": f"[mock] Analyzed request: {query}",
        "objectives": ["Implement core features", "Ensure maintainability"],
        "functional_requirements": ["Feature A", "Feature B"],
        "non_functional_requirements": ["Performance", "Security"],
        "inputs": ["User input"],
        "outputs": ["Working application"],
        "constraints": ["Python 3.11"],
        "assumptions": ["No legacy system"],
        "dependencies": [],
        "risks": [
            {
                "title": "Scope creep",
                "severity": "Medium",
                "mitigation": "Freeze requirements after analysis",
            }
        ],
        "edge_cases": ["Empty input"],
        "knowledge_sources": [],
        "web_references": [],
        "success_criteria": ["All tests pass"],
        "design_handoff": "Design a modular system with clear interfaces.",
        "confidence_score": 0.9,
        "open_questions": [],
        "status": "completed",
    }


def mock_design(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "task_id": state.get("task_id"),
        "architecture_style": "Layered Architecture",
        "architecture_reasoning": "Simple, maintainable, and easy to test",
        "components": [
            {
                "name": "API",
                "responsibility": "Expose endpoints",
                "dependencies": [],
            }
        ],
        "modules": [
            {
                "name": "core",
                "responsibility": "Business logic",
                "inputs": [],
                "outputs": [],
                "dependencies": [],
            }
        ],
        "data_flow": ["Request -> API -> Service -> Storage"],
        "api_design": {
            "required": True,
            "endpoints": [{"method": "GET", "path": "/items"}],
        },
        "database_design": {
            "required": True,
            "entities": [{"name": "Item", "fields": ["id", "name"]}],
        },
        "class_design": [
            {
                "name": "ItemService",
                "purpose": "Business logic",
                "methods": ["create", "get"],
                "properties": [],
            }
        ],
        "design_patterns": ["Repository"],
        "algorithms": [],
        "security": ["Auth via tokens"],
        "performance": ["Indexed queries"],
        "scalability": ["Stateless services"],
        "folder_structure": ["app/main.py", "app/services/item_service.py"],
        "testing_strategy": {
            "unit_tests": ["tests/test_item_service.py"],
            "integration_tests": [],
            "e2e_tests": [],
        },
        "development_phases": ["Phase 1: API", "Phase 2: Persistence"],
        "coding_guidelines": ["Type hints", "Docstrings"],
        "implementation_notes": [],
        "coding_handoff": "Implement according to the folder_structure.",
        "confidence_score": 0.9,
    }


def mock_coding(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "task_id": state.get("task_id"),
        "status": "success",
        "implementation_summary": "[mock] Generated project skeleton.",
        "generated_files": [
            {
                "path": "app/main.py",
                "language": "python",
                "content": "print('hello')",
                "description": "Application entry point",
            }
        ],
        "created_files": ["app/main.py"],
        "modified_files": [],
        "build_commands": [
            {
                "command": "pip install -r requirements.txt",
                "purpose": "Install dependencies",
            }
        ],
        "dependencies": ["fastapi"],
        "environment_variables": {},
        "implementation_notes": [],
        "assumptions": [],
        "blocking_issues": [],
        "compile_success": True,
        "lint_passed": True,
    }


def mock_testing(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "task_id": state.get("task_id"),
        "status": "success",
        "testing_summary": "[mock] Added tests for core modules.",
        "generated_test_files": [
            {
                "path": "tests/test_app.py",
                "language": "python",
                "description": "API tests",
            }
        ],
        "created_files": ["tests/test_app.py"],
        "modified_files": [],
        "deleted_files": [],
        "testing_framework": "pytest",
        "estimated_test_count": 5,
        "tested_components": ["api", "service"],
        "assumptions": [],
        "implementation_notes": [],
        "blocking_issues": [],
    }


def mock_review(state: Dict[str, Any]) -> Dict[str, Any]:
    pass_number = state.get("iterations", 0) + 1
    first_pass = pass_number == 1

    def phase(score: float) -> Dict[str, Any]:
        return {
            "score": score,
            "strengths": [],
            "weaknesses": [],
            "issues": [],
            "recommendations": [],
        }

    if first_pass:
        overall = {
            "overall_score": 55.0,
            "approval_status": "Needs Revision",
            "executive_summary": "[mock] Coding quality requires revision.",
            "top_strengths": ["Structured pipeline"],
            "top_weaknesses": ["Coding quality below standard"],
            "highest_priority_recommendations": ["Improve implementation quality"],
        }
    else:
        overall = {
            "overall_score": 92.0,
            "approval_status": "Approved",
            "executive_summary": "[mock] All phases look good after revision.",
            "top_strengths": ["Structured pipeline", "Good test coverage"],
            "top_weaknesses": [],
            "highest_priority_recommendations": [],
        }

    return {
        "task_id": state.get("task_id"),
        "analysis": phase(90.0),
        "design": phase(88.0),
        "coding": phase(50.0 if first_pass else 91.0),
        "testing": phase(85.0),
        "overall": overall,
    }
