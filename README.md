
# 🤖 DevFlow-MultiAgent

### An End-to-End Autonomous Coding Engine

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Powered-orange?style=for-the-badge)](https://github.com/langchain-ai/langgraph)
[![Groq](https://img.shields.io/badge/Groq-qwen%2Fqwen3--32b-f55036?style=for-the-badge)](https://groq.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

> **DevFlow** is a state-driven multi-agent framework that takes a natural language requirement and autonomously produces analyzed specs, architecture design, production-grade code, unit/integration tests, and a code review — in one single run.

</div>

---

## ✨ What It Does

Give DevFlow a plain-English prompt like:

```
"Build a FastAPI REST API for a to-do list with SQLite persistence, CRUD endpoints, and input validation."
```

And watch five specialized AI agents collaborate to deliver:

| Stage | Agent | Output |
|---|---|---|
| 🔍 **Analysis** | Requirements Analyst | Structured requirements, constraints, edge cases |
| 🏗️ **Design** | Solution Architect | Design patterns, component diagram, tech choices |
| 💻 **Coding** | Senior Developer | Production-ready, documented source code |
| 🧪 **Testing** | QA Engineer | Unit & integration tests with full coverage |
| 🔎 **Review** | Code Reviewer | Quality report, approval status, revision notes |

If the reviewer requests changes, the pipeline **loops back automatically** and iterates until the code meets quality standards — up to a configurable maximum.

---

## 🏛️ Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Workflow                        │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Analysis │→ │  Design  │→ │  Coding  │→ │ Testing  │   │
│  │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                  │          │
│                        ┌─────────────────────────┘         │
│                        ▼                                    │
│                  ┌──────────┐                               │
│                  │  Review  │──── APPROVED ──→ Done ✅      │
│                  │  Agent   │                               │
│                  └──────────┘                               │
│                        │                                    │
│                    REVISE ──────────────────→ Coding ↩      │
└─────────────────────────────────────────────────────────────┘
```

**Key design decisions:**
- **State-driven routing** via LangGraph — each agent reads from and writes to a shared typed state object
- **Conditional edges** drive the review loop: `approved → done`, `revise → coding`
- **Prompt engineering** is externalized to the `/Prompts` directory, making agents easy to tune without touching logic
- **Mock mode** lets you run the full graph offline without any API keys (great for testing the wiring)

---

## 📁 Project Structure

```
DevFlow-MultiAgent/
├── Agents/             # Individual agent implementations (Analyst, Architect, Dev, QA, Reviewer)
├── Prompts/            # System & user prompt templates for each agent
├── States/             # Typed state schema for the LangGraph workflow
├── Tools/              # Shared tools available to agents (e.g., Tavily web search)
├── UI/                 # Optional web interface (port 8000 by default)
├── Workflow/
│   └── WorkflowGraph.py  # Graph definition — nodes, edges, routing logic
├── architecture/       # Architecture diagrams and design docs
├── config.py           # Central configuration (API keys, timeouts, paths)
├── invoke_example.py   # CLI entry point with full usage example
└── LICENSE
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/moonmido/DevFlow-MultiAgent.git
cd DevFlow-MultiAgent
pip install -r requirements.txt
```

### 2. Set API Keys

```bash
export GROQ_API_KEY=gsk_...         # Required for live LLM inference
export TAVILY_API_KEY=tvly-...      # Required for web search tool
export NVIDIA_API_KEY=nvapi-...     # Optional — used only for RAG embeddings
```

Or create a `.env` file at the project root:

```env
GROQ_API_KEY=gsk_...
TAVILY_API_KEY=tvly-...
NVIDIA_API_KEY=nvapi-...   # Optional — used only for RAG embeddings
```

### 3. Run

```bash
# Live mode — real agents, real LLM calls
python invoke_example.py "Build a FastAPI REST API for a to-do list with SQLite"

# Offline / structural test — no API keys needed
MOCK_MODE=1 python invoke_example.py "Build a to-do list API"
```

---

## ⚙️ Configuration

All settings live in `config.py` and can be overridden via environment variables:

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | — | Groq API key (LLM inference) |
| `NVIDIA_API_KEY` | — | NVIDIA NIM API key (RAG embeddings only) |
| `TAVILY_API_KEY` | — | Tavily search API key |
| `MOCK_MODE` | `0` | Set to `1` to run offline without API calls |
| `DEVFLOW_MAX_REVIEW_ITERATIONS` | `2` | Max times the review loop can cycle |
| `DEVFLOW_UI_PORT` | `8000` | Port for the optional web UI |
| `DEVFLOW_WORKFLOW_TIMEOUT_SECONDS` | `900` | Global workflow timeout |
| `DEVFLOW_MODEL_TIMEOUT_SECONDS` | `300` | Per-model call timeout |
| `DEVFLOW_OUTPUT_ROOT` | *(local path)* | Where generated files are saved |

---

## 🧩 Tech Stack

- **[LangGraph](https://github.com/langchain-ai/langgraph)** — stateful, cyclical multi-agent orchestration
- **[Groq](https://groq.com)** — fast LLM inference for agent reasoning (`qwen/qwen3-32b`)
- **[Tavily](https://tavily.com)** — real-time web search for the research tool
- **Python 3.10+** — async-friendly, type-annotated codebase

---

## 🛠️ Extending DevFlow

**Add a new agent:**
1. Create a new file in `/Agents/` with your agent class
2. Add its prompt templates to `/Prompts/`
3. Register it as a node in `Workflow/WorkflowGraph.py`
4. Wire the edges in the graph builder

**Swap the LLM:**
Update the model name in `config.py` — the agent layer is model-agnostic as long as the provider is LangChain-compatible.

**Add tools:**
Drop new tool definitions into `/Tools/` and bind them to the relevant agent in its constructor.

---

## 📋 Example Output

```
============================================================
FINAL STATUS:       completed
REVIEW:             APPROVED
REVISION REASON:    None
ITERATIONS:         1
============================================================

--- ANALYSIS ---
{ "requirements": [...], "constraints": [...], "edge_cases": [...] }

--- DESIGN ---
{ "patterns": ["Repository", "Dependency Injection"], "stack": [...] }

--- CODING ---
{ "files": { "main.py": "...", "models.py": "...", "tests/": "..." } }

--- REVIEW ---
{ "overall": { "approval_status": "APPROVED", "score": 92 } }
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue to discuss ideas or submit a pull request for bug fixes, new agents, or tool integrations.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---


Built by [Boutmedjet Abd elmoudjib](https://github.com/moonmido) · 2026

*"The best code review is the one that happens before you write the code."*

