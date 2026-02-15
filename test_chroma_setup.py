import chromadb
try:
    client = chromadb.PersistentClient(path="./test_chroma")
    collection = client.get_or_create_collection(name="test")
    collection.add(
        documents=["This is a test document"],
        ids=["id1"]
    )
    result = collection.query(
        query_texts=["test"],
        n_results=1
    )
    print(f"ChromaDB Query Result: {result}")
    print("✅ ChromaDB is working correctly.")
except Exception as e:
    print(f"❌ ChromaDB Error: {e}")
