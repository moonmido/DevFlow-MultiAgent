"""DevFlow UI server.

Simple HTML/CSS/JS frontend backed by a zero-dependency stdlib HTTP server.
Runs the LangGraph workflow in a background thread and exposes a small JSON API.

Usage:
    python UI/server.py            # serves on http://127.0.0.1:8000
    MOCK_MODE=1 python UI/server.py   # offline demo (no API keys needed)
"""

import concurrent.futures
import json
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import config
from Workflow.WorkflowGraph import build_workflow_graph

STATIC_DIR = Path(__file__).resolve().parent / "static"
INDEX_FILE = STATIC_DIR / "index.html"

RUNS = {}
LOCK = threading.Lock()


def _run_workflow(run_id: str) -> None:
    run = RUNS.get(run_id)
    try:
        graph = build_workflow_graph()
        graph_config = {"configurable": {"thread_id": run_id}}
        inputs = {
            "user_query": run["query"],
            "max_iterations": config.MAX_REVIEW_ITERATIONS,
        }

        def consume():
            for update in graph.stream(inputs, config=graph_config, stream_mode="updates"):
                for node, value in (update or {}).items():
                    with LOCK:
                        if value.get("logs"):
                            run["logs"] = value["logs"]
                        if node not in run["completed_phases"]:
                            run["completed_phases"].append(node)
                        if value.get("current_phase"):
                            run["current_phase"] = value["current_phase"]
                        if value.get("iterations") is not None:
                            run["iterations"] = value["iterations"]
                        if value.get("status"):
                            run["run_status"] = value["status"]
            return graph.get_state(graph_config).values

        budget = config.WORKFLOW_TIMEOUT_SECONDS
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        future = executor.submit(consume)
        try:
            final = future.result(timeout=budget)
        except concurrent.futures.TimeoutError:
            with LOCK:
                run["status"] = "timeout"
                run["error"] = (
                    f"Workflow exceeded the {budget // 60}-minute budget "
                    f"while in phase {run['current_phase'] or 'starting'}."
                )
                run["finished_at"] = time.time()
            return
        finally:
            executor.shutdown(wait=False)

        with LOCK:
            run["result"] = final
            run["approval_status"] = (final.get("review") or {}).get(
                "overall", {}
            ).get("approval_status")
            run["revision_reason"] = final.get("revision_reason")
            run["status"] = "done"
            run["finished_at"] = time.time()
    except Exception as exc:  # noqa: BLE001
        with LOCK:
            run["status"] = "error"
            run["error"] = f"{type(exc).__name__}: {exc}"
            run["finished_at"] = time.time()


def _new_run(query: str) -> dict:
    run_id = uuid.uuid4().hex[:12]
    run = {
        "id": run_id,
        "query": query,
        "status": "running",
        "run_status": "running",
        "current_phase": None,
        "completed_phases": [],
        "iterations": 0,
        "approval_status": None,
        "revision_reason": None,
        "logs": [],
        "result": None,
        "error": None,
        "mock": config.MOCK_MODE,
        "started_at": time.time(),
        "finished_at": None,
    }
    with LOCK:
        RUNS[run_id] = run
    threading.Thread(target=_run_workflow, args=(run_id,), daemon=True).start()
    return run


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep console quiet
        pass

    # ---------- helpers ----------

    def _send_json(self, obj, code=200):
        body = json.dumps(obj, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_index(self):
        if not INDEX_FILE.exists():
            self._send_json({"error": "index.html missing"}, 500)
            return
        body = INDEX_FILE.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw or b"{}")
        except json.JSONDecodeError:
            return {}

    # ---------- routes ----------

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self._serve_index()
            return

        if path == "/api/status":
            run_id = (parse_qs(parsed.query).get("run_id") or [None])[0]
            with LOCK:
                run = RUNS.get(run_id)
            if not run:
                self._send_json({"error": "run not found"}, 404)
                return
            self._send_json(run)
            return

        if path == "/api/runs":
            with LOCK:
                summary = [
                    {
                        "id": r["id"],
                        "query": r["query"],
                        "status": r["status"],
                        "approval_status": r["approval_status"],
                    }
                    for r in list(RUNS.values())[-20:]
                ]
            self._send_json(summary)
            return

        self._send_json({"error": "not found"}, 404)

    def do_POST(self):
        if self.path == "/api/run":
            body = self._read_json_body()
            query = (body.get("query") or "").strip()
            if not query:
                self._send_json({"error": "query is required"}, 400)
                return
            run = _new_run(query)
            self._send_json({"run_id": run["id"]})
            return

        self._send_json({"error": "not found"}, 404)


def main():
    port = int(config.UI_PORT if hasattr(config, "UI_PORT") else 8000)
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    mode = "MOCK (offline)" if config.MOCK_MODE else "LIVE"
    print(f"[DevFlow] UI server ({mode}) -> http://127.0.0.1:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[DevFlow] shutting down", flush=True)


if __name__ == "__main__":
    main()
