"""
Smart Model Manager with Fallback Support
Handles rate limiting and automatic model/API switching
"""

import google.generativeai as genai
import requests
from ai_career_advisor.core.config import settings
from ai_career_advisor.core.logger import logger
from google.api_core.exceptions import ResourceExhausted
from typing import Dict, Any, Optional, List
import asyncio
from functools import partial


class ModelManager:
    """Manages multiple AI models with automatic fallback"""
    
    # Available models in priority order
    GEMINI_MODELS = [
        "gemini-2.5-flash",           # Primary
        "gemini-2.5-flash-lite",      # Secondary
    ]
    
    # Available API keys (in priority order)
    GEMINI_API_KEYS = [
        getattr(settings, 'GEMINI_API_KEY', None),
        getattr(settings, 'GEMINI_API_KEY_2', None),
        getattr(settings, 'GEMINI_API_KEY_3', None),
    ]
    # Filter out None values
    GEMINI_API_KEYS = [k for k in GEMINI_API_KEYS if k]
    
    # Track model/key combination performance and rate limits
    model_status: Dict[str, Dict[str, Any]] = {
        model: {"available": True, "rate_limited_until": None, "failures": 0}
        for model in GEMINI_MODELS
    }
    
    current_model_index = 0
    current_key_index = 0
    
    @classmethod
    def get_next_gemini_key(cls) -> Optional[str]:
        """Get the next available Gemini API key and rotate"""
        if not cls.GEMINI_API_KEYS:
            return getattr(settings, 'GEMINI_API_KEY', None)
        
        key = cls.GEMINI_API_KEYS[cls.current_key_index % len(cls.GEMINI_API_KEYS)]
        cls.current_key_index += 1
        return key
    
    @classmethod
    def get_available_gemini_model(cls):
        """Get the next available Gemini model, or rotate if all are rate-limited"""
        for model in cls.GEMINI_MODELS:
            status = cls.model_status.get(model, {})
            if status.get("available", True):
                logger.info(f"✅ Using Gemini model: {model}")
                return model
        
        # If all are rate limited, reset and use first
        logger.warning(f"⚠️ All Gemini models rate-limited, resetting to first model")
        cls.current_model_index = 0
        return cls.GEMINI_MODELS[0]
    
    @classmethod
    def mark_model_rate_limited(cls, model: str, retry_after: int = 60):
        """Mark a model as rate-limited"""
        logger.warning(f"🔴 Marking {model} as rate-limited for {retry_after}s")
        if model in cls.model_status:
            cls.model_status[model]["available"] = False
            cls.model_status[model]["rate_limited_until"] = retry_after
    
    @classmethod
    def mark_model_available(cls, model: str):
        """Mark a model as available again"""
        if model in cls.model_status:
            cls.model_status[model]["available"] = True
            cls.model_status[model]["failures"] = 0
    
    @classmethod
    async def generate_with_gemini(cls, prompt: str, model: Optional[str] = None) -> str:
        """
        Generate content using Gemini with automatic fallback
        - Tries different API keys when one is rate-limited
        - Tries different models when a model is rate-limited
        """
        # Get the model to use
        selected_model = model or cls.get_available_gemini_model()
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Get next API key (rotate through multiple keys)
                api_key = cls.get_next_gemini_key()
                if not api_key:
                    raise ValueError("No Gemini API keys configured")
                
                logger.info(f"📤 Generating with {selected_model} (attempt {retry_count + 1})")
                
                # Configure and try the selected model
                genai.configure(api_key=api_key)
                genai_model = genai.GenerativeModel(selected_model)
                
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    partial(genai_model.generate_content, prompt)
                )
                
                # Success - mark model as available
                cls.mark_model_available(selected_model)
                logger.success(f"✅ Generated with {selected_model}")
                return response.text.strip()
                
            except ResourceExhausted as e:
                # Rate limited - try next model (if auto-swapping is enabled, but here we specific model)
                logger.warning(f"🔴 Rate limit hit on {selected_model}: {str(e)}")
                cls.mark_model_rate_limited(selected_model)
                
                # If specifically requested model failed, we stop here to let fallback logic handle it
                if model:
                     raise
                
                # Otherwise try next available from pool
                selected_model = cls.get_available_gemini_model()
                retry_count += 1
                await asyncio.sleep(2)
            
            except Exception as e:
                logger.error(f"❌ Error with {selected_model}: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(2)
                else:
                    raise
        
        raise Exception("Gemini generation failed after retries")
    
    @classmethod
    async def generate_with_perplexity(cls, prompt: str, return_full: bool = False) -> Any:
        """
        Fallback to Perplexity API
        If return_full is True, returns dict with content and citations
        """
        if not settings.PERPLEXITY_API_KEY:
            raise ValueError("PERPLEXITY_API_KEY not configured")
        
        logger.info("Switching to Perplexity API as fallback")
        
        headers = {
            "Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar-pro",  # Current Perplexity model
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(
                    requests.post,
                    "https://api.perplexity.ai/chat/completions",
                    json=payload,
                    headers=headers
                )
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.success("Generated with Perplexity API")
                choices = result.get("choices", [{}])[0]
                content = choices.get("message", {}).get("content", "")
                citations = result.get("citations", [])
                
                if return_full:
                    return {
                        "content": content,
                        "citations": citations,
                        "model": "sonar-pro"
                    }
                return content
            else:
                logger.error(f"Perplexity API error: {response.status_code} - {response.text}")
                raise Exception(f"Perplexity API error: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Perplexity API exception: {str(e)}")
            raise
    
    @classmethod
    async def generate_smart(cls, prompt: str, return_full: bool = False) -> Any:
        """
        Smart generation with explicit fallback chain:
        1. Gemini 2.5 Flash
        2. Gemini 2.5 Flash-Lite
        3. Perplexity Sonar-Pro (returns citations if return_full=True)
        """
        # 1. Try Gemini 2.5 Flash
        try:
            content = await cls.generate_with_gemini(prompt, model="gemini-2.5-flash")
            return {"content": content, "citations": [], "model": "gemini-2.5-flash"} if return_full else content
        except Exception as e1:
            logger.warning(f"Gemini 2.5 Flash failed: {e1}. Trying Flash-Lite...")
            
            # 2. Try Gemini 2.5 Flash-Lite
            try:
                content = await cls.generate_with_gemini(prompt, model="gemini-2.5-flash-lite")
                return {"content": content, "citations": [], "model": "gemini-2.5-flash-lite"} if return_full else content
            except Exception as e2:
                logger.warning(f"Gemini 2.5 Flash-Lite failed: {e2}. Switching to Perplexity...")
                
                # 3. Try Perplexity Sonar-Pro
                try:
                    return await cls.generate_with_perplexity(prompt, return_full=return_full)
                except Exception as e3:
                    logger.error(f"All providers failed. Final error: {e3}")
                    raise Exception(f"All models failed. Last error: {e3}")
    
    @classmethod
    async def generate(cls, prompt: str, preference: str = "auto") -> str:
        """
        Generate content based on user preference.
        Returns ONLY text (backward compatibility)
        """
        if not preference or preference.lower() == "auto":
            return await cls.generate_smart(prompt, return_full=False)
        
        elif preference.lower() == "sonar-pro":
            try:
                return await cls.generate_with_perplexity(prompt, return_full=False)
            except Exception as e:
                raise Exception(f"Perplexity Sonar-Pro failed: {str(e)}")
        
        elif "gemini" in preference.lower():
            try:
                model_name = preference if preference in cls.GEMINI_MODELS else "gemini-2.5-flash"
                return await cls.generate_with_gemini(prompt, model=model_name)
            except Exception as e:
                raise Exception(f"{model_name} failed: {str(e)}")
        
        else:
            return await cls.generate_smart(prompt, return_full=False)

    @classmethod
    async def generate_extended(cls, prompt: str, preference: str = "auto") -> Dict[str, Any]:
        """
        Generate content WITH metadata (citations, model used)
        Returns: {"content": str, "citations": List[str], "model": str}
        """
        if not preference or preference.lower() == "auto":
            return await cls.generate_smart(prompt, return_full=True)
        
        elif preference.lower() == "sonar-pro":
            try:
                return await cls.generate_with_perplexity(prompt, return_full=True)
            except Exception as e:
                raise Exception(f"Perplexity Sonar-Pro failed: {str(e)}")
        
        elif "gemini" in preference.lower():
            try:
                model_name = preference if preference in cls.GEMINI_MODELS else "gemini-2.5-flash"
                content = await cls.generate_with_gemini(prompt, model=model_name)
                return {
                    "content": content,
                    "citations": [],
                    "model": model_name
                }
            except Exception as e:
                raise Exception(f"{model_name} failed: {str(e)}")
        
        else:
            return await cls.generate_smart(prompt, return_full=True)
    
    @classmethod
    async def get_embedding(cls, text: str) -> List[float]:
        """
        Get text embedding using Gemini's embedding model
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                api_key = cls.get_next_gemini_key()
                if not api_key:
                    raise ValueError("No Gemini API keys configured")
                
                genai.configure(api_key=api_key)
                
                # Using text-embedding-004 (latest Gemini embedding model)
                # Note: Don't use "models/" prefix for embed_content
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    partial(
                        genai.embed_content,
                        model="models/gemini-embedding-001",
                        content=text,
                        task_type="retrieval_document"
                    )
                )
                
                return result['embedding']
                
            except Exception as e:
                logger.error(f"❌ Embedding error (attempt {retry_count + 1}): {str(e)}")
                retry_count += 1
                await asyncio.sleep(1)
        
        raise Exception("Failed to get embedding after retries")

    @classmethod
    def reset_all_models(cls):
        """Reset all model statuses"""
        for model in cls.GEMINI_MODELS:
            cls.mark_model_available(model)
        logger.info("🔄 All models reset to available")
