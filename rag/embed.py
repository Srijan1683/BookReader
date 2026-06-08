from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions
import os

MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500  # characters

def chunk_text(text, chunk_size=CHUNK_SIZE):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def load_model():
    return SentenceTransformer(MODEL_NAME)

def embed_book_content(slide_json, collection_name="book"):
    client = chromadb.PersistentClient(path="./backend/output/chroma_db")
    
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    collection = client.get_or_create_collection(name=collection_name, embedding_function=ef)

    for chapter, headings in slide_json.items():
        for heading, slides in headings.items():
            text = " ".join(slides)
            chunks = chunk_text(text)
            for i, chunk in enumerate(chunks):
                doc_id = f"{chapter}_{heading}_{i}"
                metadata = {"chapter": chapter, "heading": heading}
                collection.add(documents=[chunk], ids=[doc_id], metadatas=[metadata])
    
    print("Embedding completed and stored.")