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
                # Rate limited - try next model
                logger.warning(f"🔴 Rate limit hit on {selected_model}: {str(e)}")
                cls.mark_model_rate_limited(selected_model)
                
                # Get next available model
                selected_model = cls.get_available_gemini_model()
                retry_count += 1
                
                # Wait before retry
                await asyncio.sleep(2)
            
            except Exception as e:
                logger.error(f"❌ Error with {selected_model}: {str(e)}")
                retry_count += 1
                
                if retry_count < max_retries:
                    await asyncio.sleep(2)
                else:
                    raise
        
        raise Exception("All Gemini models exhausted")
    
    @classmethod
    async def generate_with_perplexity(cls, prompt: str) -> str:
        """
        Fallback to Perplexity API
        """
        if not settings.PERPLEXITY_API_KEY:
            raise ValueError("PERPLEXITY_API_KEY not configured")
        
        logger.info("🔄 Switching to Perplexity API as fallback")
        
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
                logger.success("✅ Generated with Perplexity API")
                return result.get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                logger.error(f"❌ Perplexity API error: {response.status_code} - {response.text}")
                raise Exception(f"Perplexity API error: {response.status_code}")
        
        except Exception as e:
            logger.error(f"❌ Perplexity API exception: {str(e)}")
            raise
    
    @classmethod
    async def generate_smart(cls, prompt: str) -> str:
        """
        Smart generation with full fallback chain:
        1. Try Gemini 2.5 Flash (primary)
        2. Try Gemini 2.5 Flash Lite (fallback)
        3. Try Perplexity Sonar Pro (final fallback)
        """
        try:
            return await cls.generate_with_gemini(prompt)
        except Exception as e:
            logger.error(f"⚠️ Gemini failed: {str(e)}")
            
            try:
                logger.info("🔄 Attempting Perplexity as fallback...")
                return await cls.generate_with_perplexity(prompt)
            except Exception as e2:
                logger.error(f"❌ Perplexity also failed: {str(e2)}")
                raise Exception(f"All AI providers failed. Gemini: {str(e)}, Perplexity: {str(e2)}")
    
    @classmethod
    def reset_all_models(cls):
        """Reset all model statuses"""
        for model in cls.GEMINI_MODELS:
            cls.mark_model_available(model)
        logger.info("🔄 All models reset to available")
