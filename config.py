import os

from dotenv import load_dotenv

load_dotenv()

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
