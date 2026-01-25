import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir / "src"))

from ai_career_advisor.RAG.knowledge_loader import KnowledgeLoader
from ai_career_advisor.RAG.embeddings import EmbeddingService
from ai_career_advisor.RAG.vector_store import VectorStore
from ai_career_advisor.core.logger import logger

async def index_knowledge_base():
    """Index all knowledge base into ChromaDB"""
    
    logger.info("=" * 60)
    logger.info("🚀 KNOWLEDGE BASE INDEXING STARTED")
    logger.info("=" * 60)
    
    logger.info("\n Step 1: Loading documents from database...")
    documents = await KnowledgeLoader.load_all()
    
    if not documents:
        logger.error(" No documents found to index!")
        return
    
    logger.success(f" Loaded {len(documents)} documents\n")
    
    
    logger.info(" Step 2: Generating embeddings...")
    logger.info(" This may take 5-15 minutes depending on data size...")
    logger.info(" Tip: Go grab a coffee! \n")
    
    texts = [doc["content"] for doc in documents]
    embeddings = await EmbeddingService.generate_batch_embeddings(texts)
    
    valid_count = len([e for e in embeddings if e is not None])
    logger.success(f" Generated {valid_count}/{len(texts)} embeddings\n")
    

    logger.info(" Step 3: Storing in ChromaDB...")
    
    vs = VectorStore()
    
    
    try:
        vs.delete_collection("career_knowledge")
        logger.info("  Deleted old index (if existed)")
    except:
        logger.info("  No old index found (first run)")
    
    # Create fresh collection
    collection = vs.get_or_create_collection("career_knowledge")
    
    # Prepare data
    ids = [doc["id"] for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]
    
    # Add to collection
    vs.add_documents(
        collection=collection,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    
    logger.success(f" Stored {valid_count} documents in ChromaDB\n")
    
    # Step 4: Test search
    logger.info(" Step 4: Testing semantic search...\n")
    
    test_queries = [
        "IIT Bombay CSE fees kya hai?",
        "Software engineer banne ke liye kya chahiye?",
        "JEE Main exam kab hai?",
        "12th ke baad kya kare Science PCM?"
    ]
    
    for query in test_queries:
        logger.info(f"Query: {query}")
        query_emb = await EmbeddingService.generate_query_embedding(query)
        results = vs.search(collection, query_emb, top_k=2)
        
        for i, doc in enumerate(results['documents'][0][:2]):
            logger.info(f"  {i+1}. {doc[:100]}...")
        logger.info("")
    
    logger.info("\n" + "=" * 60)
    logger.success(" KNOWLEDGE BASE INDEXING COMPLETE!")
    logger.info("=" * 60)
    logger.info(f"\n Summary:")
    logger.info(f"   Total documents loaded: {len(documents)}")
    logger.info(f"   Embeddings generated: {valid_count}")
    logger.info(f"   Storage location: {vs.persist_directory}")
    logger.info(f"   Collection name: career_knowledge")
    logger.info(f"\n Your chatbot knowledge base is ready!")
    logger.info("=" * 60)

if __name__ == "__main__":
    try:
        asyncio.run(index_knowledge_base())
    except KeyboardInterrupt:
        logger.warning("\n  Indexing interrupted by user")
    except Exception as e:
        logger.error(f"\n Indexing failed: {str(e)}")
        logger.exception(e)
