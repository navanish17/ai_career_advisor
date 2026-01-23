import asyncio
from ai_career_advisor.RAG.embeddings import EmbeddingService
from ai_career_advisor.RAG.vector_store import VectorStore

async def test_embeddings():
    """Test embedding generation"""
    print("=" * 50)
    print("TEST 1: Embedding Generation")
    print("=" * 50)
    
    # Test single embedding
    text = "IIT Bombay Computer Science fees ₹2.5 lakh per year"
    embedding = await EmbeddingService.generate_embedding(text)
    
    print(f"Text: {text}")
    print(f"Embedding dimensions: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    print(f"✅ Embedding generation working!\n")
    
    # Test query embedding
    query = "IIT Bombay CSE fees kya hai?"
    query_emb = await EmbeddingService.generate_query_embedding(query)
    
    print(f"Query: {query}")
    print(f"Query embedding dimensions: {len(query_emb)}")
    print(f"✅ Query embedding working!\n")

async def test_vector_store():
    """Test ChromaDB storage and search"""
    print("=" * 50)
    print("TEST 2: Vector Store")
    print("=" * 50)
    
    # Initialize VectorStore instance (was missing!)
    vs = VectorStore()
    
    # Get collection
    collection = vs.get_or_create_collection("test_collection")
    print(f"✅ Collection created/loaded\n")
    
    # Sample documents
    documents = [
        "IIT Bombay Computer Science fees ₹2.5 lakh per year",
        "IIT Delhi fees ₹2.08 lakh, NIRF Rank 1",
        "Software Engineer career requires BTech CSE degree"
    ]
    
    # Generate embeddings
    print("Generating embeddings for 3 test documents...")
    embeddings = await EmbeddingService.generate_batch_embeddings(documents)
    
    # Store in ChromaDB
    metadatas = [
        {"source": "college", "type": "fees"},
        {"source": "college", "type": "fees"},
        {"source": "career", "type": "roadmap"}
    ]
    ids = ["doc1", "doc2", "doc3"]
    
    vs.add_documents(collection, documents, embeddings, metadatas, ids)
    print(f"✅ {len(documents)} documents stored\n")
    
    # Test search
    print("=" * 50)
    print("TEST 3: Semantic Search")
    print("=" * 50)
    
    query = "IIT Bombay CSE fees kitne hai?"
    print(f"Query: {query}")
    
    query_embedding = await EmbeddingService.generate_query_embedding(query)
    results = vs.search(collection, query_embedding, top_k=2)
    
    print(f"\nTop 2 Results:")
    for i, (doc, distance) in enumerate(zip(results['documents'][0], results['distances'][0])):
        print(f"\n{i+1}. {doc}")
        print(f"   Similarity score: {1 - distance:.3f}")
    
    print("\n✅ Semantic search working!")
    
    # Cleanup
    vs.delete_collection("test_collection")
    print("\n🧹 Test collection deleted")


async def main():
    await test_embeddings()
    await test_vector_store()
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
