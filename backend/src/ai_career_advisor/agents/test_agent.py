"""
Test script for LangGraph Agent
Run: python -m ai_career_advisor.agents.test_agent
"""
import asyncio
from ai_career_advisor.agents.career_agent import CareerAgent
from ai_career_advisor.core.logger import logger


async def test_agent():
    """Test the agent with various queries"""
    
    test_cases = [
        {
            "query": "Hello!",
            "expected_intent": "greeting",
            "description": "Greeting test"
        },
        {
            "query": "What is the capital of France?",
            "expected_intent": "rejected",
            "description": "Non-career query test"
        },
        {
            "query": "I want to become a software engineer",
            "expected_intent": "roadmap_request",
            "description": "Roadmap request test"
        },
        {
            "query": "Tell me about IIT admissions",
            "expected_intent": "career_query",
            "description": "General career query test"
        }
    ]
    
    agent = CareerAgent(db=None)  # No DB for basic tests
    
    print("\n" + "="*60)
    print("TESTING LANGGRAPH AGENT")
    print("="*60 + "\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Query: \"{test['query']}\"")
        print(f"Expected Intent: {test['expected_intent']}")
        print("-" * 60)
        
        try:
            result = await agent.run(
                query=test["query"],
                user_email="test@example.com",
                session_id=f"test-{i}",
                language="en"
            )
            
            if result["success"]:
                print(f"SUCCESS!")
                print(f"Intent Detected: {result['intent']}")
                print(f"Response Preview: {result['response'][:150]}...")
                
                if result['intent'] == test['expected_intent']:
                    print("Intent matches expected!")
                else:
                    print(f"WARNING: Intent mismatch! Got {result['intent']}, expected {test['expected_intent']}")
            else:
                print(f"FAILED: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"EXCEPTION: {str(e)}")
        
        print()
    
    print("="*60)
    print("TESTING COMPLETE")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_agent())
