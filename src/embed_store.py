from sentence_transformers import SentenceTransformer
import chromadb
import os

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="chroma_db")

COLLECTION_NAME = "code_chunks"


def build_embedding_text(chunk):
    """Combine code with structural metadata to improve retrieval quality."""
    relative_path = chunk["file_path"]
    return f"File: {relative_path}\nType: {chunk['type']}\nLanguage: {chunk['language']}\n\n{chunk['code']}"


def store_chunks(chunks, repo_name):
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    
    texts_to_embed = [build_embedding_text(c) for c in chunks]
    embeddings = model.encode(texts_to_embed).tolist()
    
    ids = [f"{repo_name}_chunk_{i}" for i in range(len(chunks))]
    
    metadatas = [
        {
            "repo": repo_name,
            "file_path": c["file_path"],
            "type": c["type"],
            "language": c["language"],
            "start_line": c["start_line"],
        }
        for c in chunks
    ]
    
    # ChromaDB documents should be the raw code (what gets shown/used later),
    # while the embedding itself was computed from the enriched text above
    documents = [c["code"] for c in chunks]
    
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )
    
    print(f"Stored {len(chunks)} chunks for repo '{repo_name}' in collection '{COLLECTION_NAME}'")
    return collection


if __name__ == "__main__":
    from clone import clone_repo
    from parse import parse_repo
    
    repo_url = input("Enter a GitHub repo URL: ")
    repo_path = clone_repo(repo_url)
    repo_name = os.path.basename(repo_path)
    
    chunks = parse_repo(repo_path)
    store_chunks(chunks, repo_name)