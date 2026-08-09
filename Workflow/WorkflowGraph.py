import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

import config
from States.WorkflowState import WorkflowState
from Workflow.mock_agents import (
    mock_analysis,
    mock_coding,
    mock_design,
    mock_review,
    mock_testing,
)

_AGENT_CACHE: Dict[str, Any] = {}


def _ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def _log(state: Dict[str, Any], message: str) -> Dict[str, Any]:
    logs = list(state.get("logs", []))
    logs.append(f"[{_ts()}] {message}")
    return {"logs": logs}


def _get_agent(kind: str):
    if kind in _AGENT_CACHE:
        return _AGENT_CACHE[kind]

    from Agents.AnalysisAgent import create_analysis_agent
    from Agents.CodingAgent import create_coding_agent
    from Agents.DesignAgent import create_design_agent
    from Agents.ReviewAgent import create_review_agent
    from Agents.TestingAgent import create_testing_agent

    factory = {
        "analysis": create_analysis_agent,
        "design": create_design_agent,
        "coding": create_coding_agent,
        "testing": create_testing_agent,
        "review": create_review_agent,
    }[kind]

    _AGENT_CACHE[kind] = factory()
    return _AGENT_CACHE[kind]


def _to_dict(output: Any) -> Dict[str, Any]:
    if hasattr(output, "model_dump"):
        return output.model_dump()
    return output


def _extract_json(content: Any) -> Optional[Dict[str, Any]]:
    if isinstance(content, str):
        candidates = [content]
    elif isinstance(content, list):
        candidates = []
        for block in content:
            if isinstance(block, dict):
                text = block.get("text") or block.get("content")
                if isinstance(text, str):
                    candidates.append(text)
            elif isinstance(block, str):
                candidates.append(block)
    else:
        return None

    for candidate in candidates:
        stripped = candidate.strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            stripped = "\n".join(lines[1:])
            if stripped.rstrip().endswith("```"):
                stripped = stripped.rstrip()[:-3].rstrip()
        try:
            parsed = json.loads(stripped)
        except (TypeError, ValueError):
            continue
        return parsed if isinstance(parsed, dict) else {"raw": parsed}
    return None


def _files_from_tool_calls(result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    created = []
    for message in result.get("messages", []):
        for call in getattr(message, "tool_calls", None) or []:
            if call.get("name") == "create_file":
                path = (call.get("args") or {}).get("path")
                if path:
                    created.append(path)
    if created:
        return {
            "status": "success",
            "implementation_summary": f"Created {len(created)} file(s) via filesystem tools.",
            "generated_files": [
                {"path": p, "language": str(p).rsplit(".", 1)[-1], "description": "Created by Coding Agent"}
                for p in created
            ],
            "created_files": created,
            "modified_files": [],
            "build_commands": [],
            "dependencies": [],
            "environment_variables": {},
            "implementation_notes": [],
            "assumptions": [],
            "blocking_issues": [],
            "compile_success": True,
            "lint_passed": None,
        }
    return None


def _run_agent(kind: str, content: str, state: Dict[str, Any]) -> Dict[str, Any]:
    if config.MOCK_MODE:
        mock = {
            "analysis": mock_analysis,
            "design": mock_design,
            "coding": mock_coding,
            "testing": mock_testing,
            "review": mock_review,
        }[kind]
        return mock(state)

    agent = _get_agent(kind)
    for attempt in range(2):
        result = agent.invoke({"messages": [HumanMessage(content=content)]})

        structured = result.get("structured_response")
        if structured is not None:
            return _to_dict(structured)

        found = None
        for message in reversed(result.get("messages", [])):
            if getattr(message, "type", None) == "ai" and message.content:
                parsed = _extract_json(message.content)
                if parsed is not None:
                    found = parsed
                    break
        if found is not None:
            return found

        if kind in ("coding", "testing"):
            fallback_result = _files_from_tool_calls(result)
            if fallback_result is not None:
                return fallback_result

        if attempt == 0:
            print(f"[DevFlow] agent '{kind}' produced no structured output; retrying...", flush=True)

    print(f"[debug] Agent '{kind}' fallback failed. Result keys: {list(result.keys())}", flush=True)
    msgs = result.get("messages", [])
    print(f"[debug] Messages count: {len(msgs)}", flush=True)
    for i, message in enumerate(msgs):
        t = getattr(message, "type", "?")
        c = getattr(message, "content", "")
        print(f"[debug]   [{i}] {t} truthy={bool(c)} len={len(str(c))}", flush=True)
        if t == "ai" and c:
            print(f"[debug]   [{i}] content[:200]: {str(c)[:200]}", flush=True)

    raise ValueError(
        f"Agent '{kind}' produced no structured response and no parseable output."
    )


def router_node(state: Dict[str, Any]) -> Dict[str, Any]:
    query = state.get("user_query", "").strip()
    if not query:
        raise ValueError("router_node: user_query is empty")

    import uuid

    task_id = state.get("task_id") or f"task_{uuid.uuid4().hex[:12]}"
    update = {
        "task_id": task_id,
        "current_phase": "router",
        "status": "running",
    }
    update.update(_log(state, f"Task {task_id} started"))
    return update


def analysis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    if not config.MOCK_MODE:
        print(f"[DevFlow] running analysis_node...", flush=True)
    result = _run_agent("analysis", state["user_query"], state)
    update = {
        "analysis": result,
        "current_phase": "analysis",
    }
    update.update(_log(state, "Analysis completed"))
    return update


def design_node(state: Dict[str, Any]) -> Dict[str, Any]:
    if not config.MOCK_MODE:
        print(f"[DevFlow] running design_node...", flush=True)
    payload = json.dumps(
        {"user_query": state.get("user_query"), "analysis": state.get("analysis")},
        indent=2,
    )
    result = _run_agent("design", payload, state)
    update = {
        "design": result,
        "current_phase": "design",
    }
    update.update(_log(state, "Design completed"))
    return update


def coding_node(state: Dict[str, Any]) -> Dict[str, Any]:
    if not config.MOCK_MODE:
        print(f"[DevFlow] running coding_node...", flush=True)
    payload = json.dumps(
        {
            "user_query": state.get("user_query"),
            "analysis": _compact_analysis(state.get("analysis")),
            "design": state.get("design"),
        },
        indent=2,
    )
    result = _run_agent("coding", payload, state)
    update = {
        "coding": result,
        "current_phase": "coding",
    }
    update.update(_log(state, "Coding completed"))
    return update


def testing_node(state: Dict[str, Any]) -> Dict[str, Any]:
    if not config.MOCK_MODE:
        print(f"[DevFlow] running testing_node...", flush=True)
    payload = json.dumps(
        {
            "user_query": state.get("user_query"),
            "design": _compact_design(state.get("design")),
            "coding": _compact_coding(state.get("coding")),
        },
        indent=2,
    )
    result = _run_agent("testing", payload, state)
    update = {
        "testing": result,
        "current_phase": "testing",
    }
    update.update(_log(state, "Testing completed"))
    return update


def _compact_analysis(a: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not a:
        return None
    return {
        "problem_summary": a.get("problem_summary"),
        "objectives": a.get("objectives"),
        "functional_requirements": a.get("functional_requirements"),
        "non_functional_requirements": a.get("non_functional_requirements"),
        "constraints": a.get("constraints"),
        "risks": a.get("risks"),
        "edge_cases": a.get("edge_cases"),
        "success_criteria": a.get("success_criteria"),
        "design_handoff": a.get("design_handoff"),
        "confidence_score": a.get("confidence_score"),
    }


def _compact_design(d: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not d:
        return None
    return {
        "architecture_style": d.get("architecture_style"),
        "architecture_reasoning": d.get("architecture_reasoning"),
        "components": d.get("components"),
        "modules": d.get("modules"),
        "data_flow": d.get("data_flow"),
        "api_design": d.get("api_design"),
        "database_design": d.get("database_design"),
        "design_patterns": d.get("design_patterns"),
        "folder_structure": d.get("folder_structure"),
        "testing_strategy": d.get("testing_strategy"),
        "coding_handoff": d.get("coding_handoff"),
        "confidence_score": d.get("confidence_score"),
    }


def _compact_coding(c: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not c:
        return None
    return {
        "status": c.get("status"),
        "implementation_summary": c.get("implementation_summary"),
        "created_files": c.get("created_files"),
        "modified_files": c.get("modified_files"),
        "build_commands": c.get("build_commands"),
        "dependencies": c.get("dependencies"),
        "blocking_issues": c.get("blocking_issues"),
        "compile_success": c.get("compile_success"),
        "lint_passed": c.get("lint_passed"),
    }


def _compact_testing(t: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not t:
        return None
    return {
        "status": t.get("status"),
        "testing_summary": t.get("testing_summary"),
        "generated_test_files": t.get("generated_test_files"),
        "created_files": t.get("created_files"),
        "modified_files": t.get("modified_files"),
        "testing_framework": t.get("testing_framework"),
        "estimated_test_count": t.get("estimated_test_count"),
        "tested_components": t.get("tested_components"),
        "blocking_issues": t.get("blocking_issues"),
    }


def review_node(state: Dict[str, Any]) -> Dict[str, Any]:
    if not config.MOCK_MODE:
        print(f"[DevFlow] running review_node...", flush=True)
    payload = json.dumps(
        {
            "user_query": state.get("user_query"),
            "task_id": state.get("task_id"),
            "analysis": _compact_analysis(state.get("analysis")),
            "design": _compact_design(state.get("design")),
            "coding": _compact_coding(state.get("coding")),
            "testing": _compact_testing(state.get("testing")),
        },
        indent=2,
    )
    result = _run_agent("review", payload, state)

    iterations = state.get("iterations", 0) + 1
    max_iterations = state.get("max_iterations", config.MAX_REVIEW_ITERATIONS)

    overall = result.get("overall", {})
    approval_status = overall.get("approval_status", "Rejected")
    approved = approval_status in ("Approved", "Approved with Minor Changes")
    force_accept = not approved and iterations >= max_iterations

    if approved:
        outcome = "accepted"
        reason = f"Approved with status '{approval_status}' on pass #{iterations}"
        target = None
    elif force_accept:
        outcome = "force_accepted"
        reason = f"Max iterations ({max_iterations}) reached; accepting with '{approval_status}'"
        target = None
    else:
        scores = {
            phase: (result.get(phase) or {}).get("score", 0)
            for phase in ("analysis", "design", "coding", "testing")
        }
        target = min(scores, key=scores.get)
        reason = (
            f"Lowest-scoring phase is '{target}' ({scores[target]:.1f}/100); "
            f"status='{approval_status}' on pass #{iterations}"
        )
        outcome = "revise"

    update = {
        "review": result,
        "iterations": iterations,
        "review_outcome": outcome,
        "review_target": target,
        "revision_reason": reason,
        "current_phase": "review",
        "status": "approved" if outcome in ("accepted", "force_accepted") else "in_review",
    }
    update.update(_log(state, f"Review pass #{iterations}: '{approval_status}' -> {outcome}"))
    return update


def route_after_review(state: Dict[str, Any]) -> str:
    outcome = state.get("review_outcome", "revise")
    if outcome == "revise":
        target = state.get("review_target") or "coding"
        return f"revise_{target}"
    return "accept"


def finalize_node(state: Dict[str, Any]) -> Dict[str, Any]:
    overall = (state.get("review") or {}).get("overall", {})
    approval_status = overall.get("approval_status", "unknown")
    update = {
        "current_phase": "finalize",
        "status": state.get("status", "approved"),
    }
    update.update(
        _log(
            state,
            f"Final approval_status={approval_status} after {state.get('iterations', 0)} review pass(es)",
        )
    )
    return update


def build_workflow_graph(checkpointer: Optional[Any] = None):
    builder = StateGraph(WorkflowState)

    builder.add_node("router_node", router_node)
    builder.add_node("analysis_node", analysis_node)
    builder.add_node("design_node", design_node)
    builder.add_node("coding_node", coding_node)
    builder.add_node("testing_node", testing_node)
    builder.add_node("review_node", review_node)
    builder.add_node("finalize_node", finalize_node)

    builder.add_edge(START, "router_node")
    builder.add_edge("router_node", "analysis_node")
    builder.add_edge("analysis_node", "design_node")
    builder.add_edge("design_node", "coding_node")
    builder.add_edge("coding_node", "testing_node")
    builder.add_edge("testing_node", "review_node")

    builder.add_conditional_edges(
        "review_node",
        route_after_review,
        {
            "accept": "finalize_node",
            "revise_analysis": "analysis_node",
            "revise_design": "design_node",
            "revise_coding": "coding_node",
            "revise_testing": "testing_node",
        },
    )

    builder.add_edge("finalize_node", END)

    if checkpointer is None:
        checkpointer = InMemorySaver()

    return builder.compile(checkpointer=checkpointer)
