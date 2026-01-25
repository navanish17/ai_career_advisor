from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from ai_career_advisor.core.logger import logger
import asyncio
from datetime import datetime

class KnowledgeBaseScheduler:
    """
    Automated weekly knowledge base re-indexing
    Runs every Sunday at 2:00 AM IST
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
        self.is_running = False
    
    async def reindex_knowledge_base(self):
        """Re-index entire knowledge base with latest data"""
        try:
            logger.info("=" * 60)
            logger.info(" SCHEDULED RE-INDEXING STARTED")
            logger.info(f" Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
            logger.info("=" * 60)
            
            
            from ai_career_advisor.RAG.knowledge_loader import KnowledgeLoader
            from ai_career_advisor.RAG.embeddings import EmbeddingService
            from ai_career_advisor.RAG.vector_store import VectorStore
            
            logger.info("\n  Deleting old index...")
            vs = VectorStore()
            try:
                vs.delete_collection("career_knowledge")
                logger.success(" Old index deleted")
            except:
                logger.info(" No old index found")
            
            
            logger.info("\n Loading latest data from database...")
            documents = await KnowledgeLoader.load_all()
            
            if not documents:
                logger.error(" No documents found!")
                return
            
            logger.success(f" Loaded {len(documents)} documents")
            
            
            logger.info("\n Generating embeddings...")
            texts = [doc["content"] for doc in documents]
            embeddings = await EmbeddingService.generate_batch_embeddings(texts)
            
            valid_count = len([e for e in embeddings if e is not None])
            logger.success(f" Generated {valid_count}/{len(texts)} embeddings")
            
            
            logger.info("\n Storing in ChromaDB...")
            collection = vs.get_or_create_collection("career_knowledge")
            
            ids = [doc["id"] for doc in documents]
            metadatas = [doc["metadata"] for doc in documents]
            
            vs.add_documents(
                collection=collection,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.success(f" Stored {valid_count} documents")
            
            
            logger.info("\n Testing...")
            test_query = "IIT Bombay fees"
            query_emb = await EmbeddingService.generate_query_embedding(test_query)
            results = vs.search(collection, query_emb, top_k=1)
            
            if results['documents'][0]:
                logger.success(" Search test passed")
            
            logger.info("\n" + "=" * 60)
            logger.success(" SCHEDULED RE-INDEXING COMPLETE!")
            logger.info("=" * 60)
            logger.info(f" Documents indexed: {valid_count}")
            logger.info(f" Next re-index: Next Sunday 2:00 AM IST")
            logger.info("=" * 60)
        
        except Exception as e:
            logger.error(f" Re-indexing failed: {str(e)}")
            logger.exception(e)
    
    def start(self):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler already running!")
            return
        
        
        self.scheduler.add_job(
            self.reindex_knowledge_base,
            trigger=CronTrigger(
                day_of_week='sun',
                hour=2,
                minute=0,
                timezone='Asia/Kolkata'
            ),
            id='weekly_reindex',
            name='Weekly Knowledge Base Re-indexing',
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        
        logger.success(" Scheduler started!")
        logger.info("Schedule: Every Sunday 2:00 AM IST")
        
        
        job = self.scheduler.get_job('weekly_reindex')
        if job:
            next_run = job.next_run_time
            logger.info(f" Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler stopped")
    
    def trigger_manual_reindex(self):
        """Manual trigger (for admin)"""
        logger.info(" Manual re-index triggered")
        asyncio.create_task(self.reindex_knowledge_base())

scheduler = KnowledgeBaseScheduler()
