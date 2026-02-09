# import google.generativeai as genai
import google.generativeai as genai
import os
import asyncio

# Hardcoding key for testing
api_key = "AIzaSyCEH6VNW8ngDdAQeRlFpUr7vQnTLMjolKg"

genai.configure(api_key=api_key)

async def test_embeddings():
    print("Listing available models first...")
    try:
        for m in genai.list_models():
            if 'embedContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

    models_to_test = [
        "models/gemini-embedding-001",
        "gemini-embedding-001"
    ]
    
    print(f"Testing with API Key: {api_key[:5]}...{api_key[-4:]}")
    
    for model in models_to_test:
        print(f"\n--- Testing model: {model} ---")
        try:
            result = genai.embed_content(
                model=model,
                content="Hello world",
                task_type="retrieval_document"
            )
            print(f"✅ SUCCESS! Embedding length: {len(result['embedding'])}")
            return  # Stop after first success
        except Exception as e:
            print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    # Print available models
    print("List of available models:")
    try:
        for m in genai.list_models():
            if 'embedContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

    # Test embeddings
    import asyncio
    asyncio.run(test_embeddings())
