import google.generativeai as genai
from ai_career_advisor.core.config import settings
from ai_career_advisor.core.logger import logger
from typing import List
import asyncio
from functools import partial


genai.configure(api_key=settings.GEMINI_API_KEY)

class EmbeddingService:
    """
    Google Gemini embeddings service
    Converts text to 768-dimensional vectors
    """
    
    MODEL_NAME = "models/text-embedding-004"
    
    @staticmethod
    async def generate_embedding(text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text (max 2048 tokens)
        
        Returns:
            768-dimensional vector
        """
        try:
            
            text = text.strip()
            if not text:
                raise ValueError("Empty text provided")
            
            
            if len(text) > 5000:
                text = text[:5000]
                logger.warning(f"Text truncated to 5000 chars")
            
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                partial(
                    genai.embed_content,
                    model=EmbeddingService.MODEL_NAME,
                    content=text,
                    task_type="retrieval_document"
                )
            )
            
            embedding = result["embedding"]
            logger.debug(f"Generated embedding (dim: {len(embedding)})")
            
            return embedding
        
        except Exception as e:
            logger.error(f"Embedding generation error: {str(e)}")
            raise
    
    @staticmethod
    async def generate_query_embedding(query: str) -> List[float]:
        """
        Generate embedding for search query
        Uses task_type="retrieval_query" for better search accuracy
        """
        try:
            query = query.strip()
            if not query:
                raise ValueError("Empty query provided")
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                partial(
                    genai.embed_content,
                    model=EmbeddingService.MODEL_NAME,
                    content=query,
                    task_type="retrieval_query"  
                )
            )
            
            embedding = result["embedding"]
            logger.debug(f"Generated query embedding (dim: {len(embedding)})")
            
            return embedding
        
        except Exception as e:
            logger.error(f"Query embedding error: {str(e)}")
            raise
    
    @staticmethod
    async def generate_batch_embeddings(texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        Processes in batches to avoid rate limits
        """
        embeddings = []
        
        for i, text in enumerate(texts):
            try:
                embedding = await EmbeddingService.generate_embedding(text)
                embeddings.append(embedding)
                
            
                if (i + 1) % 10 == 0:
                    logger.info(f"Generated {i + 1}/{len(texts)} embeddings")
                
            
                if i < len(texts) - 1:
                    await asyncio.sleep(0.5)  
            
            except Exception as e:
                logger.error(f"Batch embedding error at index {i}: {str(e)}")
                embeddings.append(None)
        
        logger.success(f"Generated {len([e for e in embeddings if e])} embeddings successfully")
        return embeddings
