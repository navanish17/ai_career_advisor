import requests
from ai_career_advisor.core.config import settings

def test_perplexity_api():
    """Test if Perplexity API key is working"""
    
    api_key = settings.PERPLEXITY_API_KEY
    
    print(f"🔑 API Key: {api_key[:15]}..." if api_key else "❌ No API key found!")
    
    if not api_key:
        print("❌ PERPLEXITY_API_KEY not found in .env file")
        return
    
    url = "https://api.perplexity.ai/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "user",
                "content": "Say 'API is working' in one sentence."
            }
        ],
        "max_tokens": 50
    }
    
    print("\n🚀 Testing Perplexity API...")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            message = data['choices'][0]['message']['content']
            print(f"✅ API is working!")
            print(f"📝 Response: {message}")
            return True
        
        elif response.status_code == 401:
            print("❌ 401 Unauthorized - Invalid API key")
            print("🔍 Check:")
            print("   1. Key is correct in .env file")
            print("   2. Key starts with 'pplx-'")
            print("   3. Key is active (not expired)")
            print(f"\n📄 Response: {response.text}")
            return False
        
        elif response.status_code == 429:
            print("⚠️ 429 Rate Limited - Too many requests")
            return False
        
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️ Request timed out")
        return False
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_perplexity_api()
