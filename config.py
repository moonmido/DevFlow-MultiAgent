import os

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

MOCK_MODE = os.getenv("MOCK_MODE", "0").lower() in ("1", "true", "yes")

DEFAULT_OUTPUT_ROOT = os.getenv(
    "DEVFLOW_OUTPUT_ROOT", "/Users/mac/Desktop/devFlowProjetsTestingPath"
)
ANALYSIS_DATASET_DIR = os.getenv("DEVFLOW_ANALYSIS_DATASET", "/Users/mac/Desktop/dataset")
DESIGN_DATASET_DIR = os.getenv("DEVFLOW_DESIGN_DATASET", "/Users/mac/Desktop/design_dataset")

MAX_REVIEW_ITERATIONS = int(os.getenv("DEVFLOW_MAX_REVIEW_ITERATIONS", "2"))

UI_PORT = int(os.getenv("DEVFLOW_UI_PORT", "8000"))

WORKFLOW_TIMEOUT_SECONDS = int(os.getenv("DEVFLOW_WORKFLOW_TIMEOUT_SECONDS", "900"))

MODEL_TIMEOUT_SECONDS = int(os.getenv("DEVFLOW_MODEL_TIMEOUT_SECONDS", "300"))

# Groq's on-demand tier counts the requested `max_tokens` towards the
# per-minute token limit, so large output budgets make requests fail with
# 413/429 even when the prompt itself is small. Keep these budgets modest.
MODEL_MAX_TOKENS = {
    "analysis": int(os.getenv("DEVFLOW_ANALYSIS_MAX_TOKENS", "2048")),
    "design": int(os.getenv("DEVFLOW_DESIGN_MAX_TOKENS", "3584")),
    "coding": int(os.getenv("DEVFLOW_CODING_MAX_TOKENS", "2560")),
    "testing": int(os.getenv("DEVFLOW_TESTING_MAX_TOKENS", "2048")),
    "review": int(os.getenv("DEVFLOW_REVIEW_MAX_TOKENS", "2560")),
}
