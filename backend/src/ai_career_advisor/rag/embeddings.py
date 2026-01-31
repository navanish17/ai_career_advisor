from ai_career_advisor.core.logger import logger
from typing import List
import asyncio
from functools import lru_cache


class EmbeddingService:
    """
    Local Hugging Face embeddings service using sentence-transformers
    - Works offline (after first model download)
    - Free, no API limits
    - Fast embedding generation
    """
    
    # Using a lightweight, high-quality model
    MODEL_NAME = "all-MiniLM-L6-v2"  # 384 dimensions, fast, good quality
    _model = None
    _lock = asyncio.Lock()
    
    @classmethod
    def _get_model(cls):
        """Lazy load the model (only when first needed)"""
        if cls._model is None:
            logger.info(f"🔄 Loading embedding model: {cls.MODEL_NAME}")
            try:
                from sentence_transformers import SentenceTransformer
                cls._model = SentenceTransformer(cls.MODEL_NAME)
                logger.success(f"✅ Embedding model loaded successfully")
            except Exception as e:
                logger.error(f"❌ Failed to load model: {e}")
                raise
        return cls._model
    
    @staticmethod
    async def generate_embedding(text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text (will be truncated if too long)
        
        Returns:
            384-dimensional vector (for all-MiniLM-L6-v2)
        """
        try:
            text = text.strip()
            if not text:
                raise ValueError("Empty text provided")
            
            # Truncate if too long
            if len(text) > 5000:
                text = text[:5000]
                logger.warning(f"Text truncated to 5000 chars")
            
            # Run in executor to not block event loop
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                lambda: EmbeddingService._get_model().encode(text).tolist()
            )
            
            logger.debug(f"Generated embedding (dim: {len(embedding)})")
            return embedding
        
        except Exception as e:
            logger.error(f"❌ Embedding generation error: {str(e)}")
            raise
    
    @staticmethod
    async def generate_query_embedding(query: str) -> List[float]:
        """
        Generate embedding for search query
        Same as generate_embedding but with clear semantics
        """
        return await EmbeddingService.generate_embedding(query)
    
    @staticmethod
    async def generate_batch_embeddings(texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing)
        More efficient than calling generate_embedding multiple times
        """
        try:
            # Clean texts
            clean_texts = [t.strip()[:5000] for t in texts if t.strip()]
            
            if not clean_texts:
                return []
            
            # Batch encode
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: EmbeddingService._get_model().encode(clean_texts).tolist()
            )
            
            logger.success(f"✅ Generated {len(embeddings)} embeddings in batch")
            return embeddings
        
        except Exception as e:
            logger.error(f"❌ Batch embedding error: {str(e)}")
            return []
