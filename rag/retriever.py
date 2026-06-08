import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

def get_top_k_docs(query: str, k=4, collection_name="book"):
    client = chromadb.PersistentClient(path="./backend/output/chroma_db")
    
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    collection = client.get_or_create_collection(name=collection_name, embedding_function=ef)
    
    results = collection.query(query_texts=[query], n_results=k)
    docs = results["documents"][0]
    metadata = results["metadatas"][0]
    
    return list(zip(docs, metadata))