import os
from functools import lru_cache

from langchain.tools import tool
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config

DATASET_DIR = config.ANALYSIS_DATASET_DIR
EMBEDDING_TIMEOUT = 20


@lru_cache(maxsize=1)
def _get_retriever():
    os.environ.setdefault("NVIDIA_API_KEY", config.NVIDIA_API_KEY)
    if not os.path.isdir(DATASET_DIR):
        return None
    try:
        loader = PyPDFDirectoryLoader(DATASET_DIR)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=100)
        chunks = splitter.split_documents(documents)

        embeddings = NVIDIAEmbeddings(
            model="nvidia/nv-embed-v1",
            timeout=EMBEDDING_TIMEOUT,
        )

        vector_store = InMemoryVectorStore.from_documents(documents=chunks, embedding=embeddings)

        return vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5},
        )
    except Exception:
        return None


@tool(description="Retrieve relevant documents from the internal knowledge base.")
def get_relevant_documents(query: str) -> str:
    retriever = _get_retriever()
    if retriever is None:
        return (
            f"Knowledge base unavailable (dataset not found at {DATASET_DIR} or embedding "
            "service failed). Proceed without internal documents."
        )

    try:
        docs = retriever.invoke(query)
    except Exception as exc:  # noqa: BLE001
        return (
            f"Knowledge base lookup failed ({exc}). "
            "Proceed without internal documents."
        )

    return "\n\n".join(
        [
            f"Source: {doc.metadata.get('source', 'unknown')}\n"
            f"{doc.page_content}"
            for doc in docs
        ]
    )
