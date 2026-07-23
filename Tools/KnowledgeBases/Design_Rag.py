import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain.tools import tool
loader = PyPDFDirectoryLoader("/Users/mac/Desktop/design_dataset")
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=100)
chunks = splitter.split_documents(documents)  

os.environ["NVIDIA_API_KEY"] = ""


embeddings = NVIDIAEmbeddings(
    model="nvidia/nv-embed-v1", 
)

vectorStore = InMemoryVectorStore.from_documents(documents=chunks, embedding=embeddings)

retriever = vectorStore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5},
)

@tool(description="Retrieve relevant documents from the internal knowledge base.")
def get_relevant_documents(query: str) -> str:
   
    docs = retriever.invoke(query)

    return "\n\n".join(
        [
            f"Source: {doc.metadata.get('source', 'unknown')}\n"
            f"{doc.page_content}"
            for doc in docs
        ]
    )