from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="chroma_db")

COLLECTION_NAME = "code_chunks"


def retrieve_chunks(query, repo=None, n_results=5):
    collection = client.get_collection(name=COLLECTION_NAME)
    
    query_embedding = model.encode([query]).tolist()
    
    where_filter = {"repo": repo} if repo else None
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
        where=where_filter,
        include=["documents", "metadatas", "distances"]
    )
    
    # Combine code with its metadata so the caller knows exactly where each result came from
    combined = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        combined.append({
            "code": doc,
            "file_path": meta["file_path"],
            "start_line": meta["start_line"],
            "type": meta["type"],
        })
    
    return combined


if __name__ == "__main__":
    query = "how is chunking done"
    results = retrieve_chunks(query, repo="SEC-RAG")
    
    for i, r in enumerate(results):
        print(f"--- Result {i+1} ({r['file_path']}, line {r['start_line']}) ---")
        print(r["code"])
        print()