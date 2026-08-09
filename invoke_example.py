"""
DevFlow multi-agent workflow - LangGraph invoke example.

Real agents:
    export NVIDIA_API_KEY=nvapi-...
    export TAVILY_API_KEY=tvly-...
    python invoke_example.py "Build a FastAPI REST API for a to-do list with SQLite"

Offline / structural test (no API keys needed):
    MOCK_MODE=1 python invoke_example.py "Build a to-do list API"
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config  # noqa: E402
from Workflow.WorkflowGraph import build_workflow_graph  # noqa: E402

DEFAULT_QUERY = (
    "Build a FastAPI REST API for a to-do list with SQLite persistence, "
    "CRUD endpoints, and input validation."
)


def _print_section(title: str, payload: dict) -> None:
    print(f"\n--- {title} ---")
    if not payload:
        print("  (none)")
        return
    print(json.dumps(payload, indent=2, default=str)[:4000])


def main() -> None:
    query = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_QUERY
    mode = "MOCK (offline)" if config.MOCK_MODE else "LIVE"
    print(f"[DevFlow] mode={mode}")
    print(f"[DevFlow] query: {query}\n")

    graph = build_workflow_graph()

    try:
        result = graph.invoke(
            {
                "user_query": query,
                "max_iterations": config.MAX_REVIEW_ITERATIONS,
            },
            config={"configurable": {"thread_id": "devflow-run"}},
        )
    except Exception as exc:  # noqa: BLE001
        print(f"[DevFlow] workflow failed: {type(exc).__name__}: {exc}")
        sys.exit(1)

    print("=" * 64)
    print(f"FINAL STATUS: {result.get('status')}")
    print(f"REVIEW: {((result.get('review') or {}).get('overall') or {}).get('approval_status')}")
    print(f"REVISION REASON: {result.get('revision_reason')}")
    print(f"ITERATIONS: {result.get('iterations')}")
    print("=" * 64)

    _print_section("ANALYSIS", result.get("analysis"))
    _print_section("DESIGN", result.get("design"))
    _print_section("CODING", result.get("coding"))
    _print_section("TESTING", result.get("testing"))
    _print_section("REVIEW", result.get("review"))

    print("\n[DevFlow] execution log:")
    for line in result.get("logs", []):
        print(f"  {line}")


if __name__ == "__main__":
    main()
