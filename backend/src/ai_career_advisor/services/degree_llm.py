import requests
from ai_career_advisor.core.config import settings

PROMPT_TEMPLATE = """
You are a Degree Description Generator.
Generate EXACTLY 1 simple line about the degree {degree_name}.
Line 1: What this degree is, written in simple academic language.

Rules:
- No careers, salary, colleges, exams.
- No bullets, no numbering.
- No extra lines.
- Use formal but simple tone.
- Similar depth and style as a university prospectus.
Return only plain text.
""".strip()

def generate_degree_description(degree_name: str) -> str:
    """
    Generates a 2-line academic description for a degree using Perplexity API.
    Returns plain text only.
    """
    
    if not degree_name:
        raise ValueError("Degree name is required")
    
    url = "https://api.perplexity.ai/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar-pro",  
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that generates concise degree descriptions."
            },
            {
                "role": "user",
                "content": PROMPT_TEMPLATE.format(degree_name=degree_name)
            }
        ],
        "temperature": 0.2,
        "max_tokens": 150
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if "choices" not in data or len(data["choices"]) == 0:
            raise RuntimeError("Empty response from Perplexity API")
        
        text = data["choices"][0]["message"]["content"].strip()
        
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines[:4])
        
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Perplexity API request failed: {str(e)}")
    except KeyError as e:
        raise RuntimeError(f"Invalid response format from Perplexity API: {str(e)}")
