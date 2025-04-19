import psutil
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Milvus
# from pymilvus import connections
from langchain_community.vectorstores import Qdrant

class Vectorstore:

    def get_vectorstore(self, chunks, model_name = "nomic-embed-text:latest"):
        if not chunks:
            return None
        embeddings = OllamaEmbeddings(
            model=model_name,
            num_thread=max(1, int(psutil.cpu_count() * 0.9)),
        )

        vectorstore = Qdrant.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name="document_hub",
            location=":memory:", 
            # connection_args={"host": "localhost", "port": "19530"},
        )
        return vectorstore
