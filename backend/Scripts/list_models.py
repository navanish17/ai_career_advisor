import google.generativeai as genai
import os

# Hardcoding key for testing
api_key = "AIzaSyCEH6VNW8ngDdAQeRlFpUr7vQnTLMjolKg"
genai.configure(api_key=api_key)

print("Listing models...")
try:
    for m in genai.list_models():
        print(f"Model: {m.name}")
        print(f"Methods: {m.supported_generation_methods}")
        print("-" * 20)
except Exception as e:
    print(f"Error: {e}")
