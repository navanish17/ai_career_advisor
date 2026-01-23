import chromadb
from chromadb.config import Settings
from ai_career_advisor.core.logger import logger
from typing import List, Dict, Any
import os

class VectorStore:
    """
    ChromaDB vector database manager
    Stores and retrieves document embeddings
    """
    
    def __init__(self):
        """Initialize ChromaDB client"""
        
        self.persist_directory = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "chroma_db"
        )
        
        
        os.makedirs(self.persist_directory, exist_ok=True)
        
        
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        logger.info(f"ChromaDB initialized at: {self.persist_directory}")
    
    def get_or_create_collection(self, collection_name: str = "career_knowledge"):
        """
        Get existing collection or create new one
        
        Args:
            collection_name: Name of the collection
        
        Returns:
            ChromaDB collection object
        """
        try:
            
            collection = self.client.get_collection(name=collection_name)
            count = collection.count()
            logger.info(f"Collection '{collection_name}' loaded ({count} documents)")
            return collection
        
        except Exception:
            
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "AI Career Advisor knowledge base"}
            )
            logger.success(f"Collection '{collection_name}' created")
            return collection
    
    def add_documents(
        self,
        collection,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ):
        """
        Add documents to collection
        
        Args:
            collection: ChromaDB collection
            documents: List of text documents
            embeddings: List of embedding vectors
            metadatas: List of metadata dicts
            ids: List of unique IDs
        """
        try:
            
            valid_items = [
                (doc, emb, meta, id_)
                for doc, emb, meta, id_ in zip(documents, embeddings, metadatas, ids)
                if emb is not None
            ]
            
            if not valid_items:
                logger.error("No valid embeddings to add")
                return
            
            docs, embs, metas, ids_ = zip(*valid_items)
            
            collection.add(
                documents=list(docs),
                embeddings=list(embs),
                metadatas=list(metas),
                ids=list(ids_)
            )
            
            logger.success(f"Added {len(docs)} documents to collection")
        
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def search(
        self,
        collection,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Search for similar documents
        
        Args:
            collection: ChromaDB collection
            query_embedding: Query vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
        
        Returns:
            Search results with documents, metadatas, distances
        """
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_metadata 
            )
            
            logger.debug(f"Search returned {len(results['ids'][0])} results")
            return results
        
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            raise
    
    def delete_collection(self, collection_name: str = "career_knowledge"):
        """Delete entire collection (use with caution!)"""
        try:
            self.client.delete_collection(name=collection_name)
            logger.warning(f"Collection '{collection_name}' deleted")
        except Exception as e:
            logger.error(f"Delete error: {str(e)}")
    
    def reset_database(self):
        """Reset entire database (use with caution!)"""
        self.client.reset()
        logger.warning("ChromaDB reset - all data deleted!")



vector_store = VectorStore()
