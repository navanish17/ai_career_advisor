from ai_career_advisor.RAG.vector_store import VectorStore
from ai_career_advisor.RAG.embeddings import EmbeddingService
from ai_career_advisor.core.logger import logger
from typing import List, Dict, Any


class RAGRetriever:
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.collection = self.vector_store.get_or_create_collection("career_knowledge")
    
    async def search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        try:
            logger.info(f"RAG search for: {query}")
            
            query_embedding = await EmbeddingService.generate_query_embedding(query)
            
            results = self.vector_store.search(
                collection=self.collection,
                query_embedding=query_embedding,
                top_k=top_k
            )
            
            if not results['documents'][0]:
                logger.warning("No results found in RAG")
                return {
                    "found": False,
                    "documents": [],
                    "metadatas": [],
                    "scores": []
                }
            
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            distances = results['distances'][0]
            
            scores = [1 - dist for dist in distances]
            
            logger.success(f"Found {len(documents)} relevant documents")
            
            return {
                "found": True,
                "documents": documents,
                "metadatas": metadatas,
                "scores": scores
            }
        
        except Exception as e:
            logger.error(f"RAG search error: {str(e)}")
            return {
                "found": False,
                "documents": [],
                "metadatas": [],
                "scores": []
            }
    
    def build_context(self, search_results: Dict[str, Any], max_length: int = 2000) -> str:
        if not search_results["found"]:
            return ""
        
        context_parts = []
        current_length = 0
        
        for doc, metadata, score in zip(
            search_results["documents"],
            search_results["metadatas"],
            search_results["scores"]
        ):
            if score < 0.3:
                continue
            
            source_type = metadata.get("source", "unknown")
            doc_text = f"[Source: {source_type}] {doc}"
            
            if current_length + len(doc_text) > max_length:
                break
            
            context_parts.append(doc_text)
            current_length += len(doc_text)
        
        context = "\n\n".join(context_parts)
        
        logger.info(f"Built context with {len(context_parts)} documents ({current_length} chars)")
        
        return context
    
    async def search_and_build_context(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        search_results = await self.search(query, top_k)
        context = self.build_context(search_results)
        
        return {
            "context": context,
            "found": search_results["found"],
            "num_documents": len(search_results["documents"]),
            "sources": [m.get("source", "unknown") for m in search_results["metadatas"]],
            "scores": search_results["scores"]
        }
    
    async def add_to_knowledge_base(
        self, 
        query: str, 
        response: str, 
        metadata: Dict[str, Any] = None
        ) -> bool:
        """
        Save LLM-generated response to RAG for future use
        This allows chatbot to LEARN from new queries
        """
        try:
            logger.info(f"Saving to RAG: {query[:50]}...")
            
            
            response_embedding = await EmbeddingService.generate_query_embedding(response)
            
            
            if metadata is None:
                metadata = {}
            
            metadata.update({
                "source": "llm_generated",
                "original_query": query
            })
            
            import uuid
            doc_id = f"llm_{str(uuid.uuid4())}"
            
            self.collection.add(
                ids=[doc_id],
                embeddings=[response_embedding],
                documents=[response],
                metadatas=[metadata]
            )
            
            logger.success(f"Saved to RAG with ID: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save to RAG: {str(e)}")
            return False



retriever = RAGRetriever()
