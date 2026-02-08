"""
Test script for Model Preference in Agent
Run: python -m ai_career_advisor.agents.test_preference
"""
import asyncio
from ai_career_advisor.agents.career_agent import CareerAgent
from ai_career_advisor.core.logger import logger

async def test_preference():
    agent = CareerAgent(db=None)
    
    test_cases = [
        {"model": "auto", "desc": "Auto Mode"},
        {"model": "gemini-2.5-flash", "desc": "Explicit Gemini Flash"},
        {"model": "gemini-2.5-flash-lite", "desc": "Explicit Flash Lite"},
        {"model": "sonar-pro", "desc": "Explicit Perplexity (Should fail if no key, but logic runs)"}
    ]
    
    print("\n" + "="*60)
    print("TESTING MODEL PREFERENCE")
    print("="*60 + "\n")
    
    for test in test_cases:
        print(f"Testing: {test['desc']} ({test['model']})")
        try:
            result = await agent.run(
                query="Hello, who are you?",
                user_email="test@example.com",
                session_id="test-pref",
                language="en",
                model_preference=test['model']
            )
            
            if result["success"]:
                print(f"SUCCESS! Response: {result['response'][:50]}...")
            else:
                print(f"FAILED (Expected if no key): {result.get('error')}")
                
        except Exception as e:
            print(f"EXCEPTION: {e}")
        print("-" * 60)

if __name__ == "__main__":
    asyncio.run(test_preference())
