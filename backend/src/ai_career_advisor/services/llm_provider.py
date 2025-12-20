from ai_career_advisor.core.config import settings

def get_llm_provider():
    if settings.PERPLEXITY_API_KEY:
        return "perplexity"
    return "gemini"
