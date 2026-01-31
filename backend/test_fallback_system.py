#!/usr/bin/env python3
"""
Test Script: API Fallback System Verification

This script verifies that the API fallback system is working correctly.
Run from backend directory: python test_fallback_system.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_model_manager_imports():
    """Test that ModelManager imports correctly"""
    print("\n" + "="*60)
    print("TEST 1: ModelManager Imports")
    print("="*60)
    try:
        from ai_career_advisor.core.model_manager import ModelManager
        print("✅ ModelManager imported successfully")
        print(f"   - Available models: {ModelManager.GEMINI_MODELS}")
        print(f"   - API keys configured: {len(ModelManager.GEMINI_API_KEYS)} keys")
        return True
    except Exception as e:
        print(f"❌ Failed to import ModelManager: {str(e)}")
        return False


async def test_config_loading():
    """Test that config loads all API keys"""
    print("\n" + "="*60)
    print("TEST 2: Config Loading")
    print("="*60)
    try:
        from ai_career_advisor.core.config import settings
        
        has_key1 = bool(settings.GEMINI_API_KEY)
        has_key2 = bool(getattr(settings, 'GEMINI_API_KEY_2', None))
        has_key3 = bool(getattr(settings, 'GEMINI_API_KEY_3', None))
        has_pplx = bool(settings.PERPLEXITY_API_KEY)
        
        print(f"✅ Config loaded successfully")
        print(f"   - GEMINI_API_KEY: {'✅ Configured' if has_key1 else '❌ Missing'}")
        print(f"   - GEMINI_API_KEY_2: {'✅ Configured' if has_key2 else '⚠️ Optional'}")
        print(f"   - GEMINI_API_KEY_3: {'✅ Configured' if has_key3 else '⚠️ Optional'}")
        print(f"   - PERPLEXITY_API_KEY: {'✅ Configured' if has_pplx else '⚠️ Optional'}")
        
        if not has_key1:
            print("\n⚠️ WARNING: GEMINI_API_KEY is required!")
            print("   Add GEMINI_API_KEY to backend/.env")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Failed to load config: {str(e)}")
        return False


async def test_service_imports():
    """Test that all services with fallback import correctly"""
    print("\n" + "="*60)
    print("TEST 3: Service Imports")
    print("="*60)
    
    services = [
        ("college_details_extractor", "ai_career_advisor.services.college_details_extractor"),
        ("career_llm", "ai_career_advisor.services.career_llm"),
        ("career_insight_llm", "ai_career_advisor.services.career_insight_llm"),
        ("backward_planner_llm", "ai_career_advisor.services.backward_planner_llm"),
    ]
    
    all_ok = True
    for name, module_path in services:
        try:
            __import__(module_path)
            print(f"✅ {name:<30} imported successfully")
        except Exception as e:
            print(f"❌ {name:<30} import failed: {str(e)[:60]}")
            all_ok = False
    
    return all_ok


async def test_logger_setup():
    """Test that logger is configured"""
    print("\n" + "="*60)
    print("TEST 4: Logger Setup")
    print("="*60)
    try:
        from ai_career_advisor.core.logger import logger
        
        # Test logger methods
        logger.info("ℹ️ Test info message")
        logger.warning("⚠️ Test warning message")
        logger.error("❌ Test error message")
        logger.success("✅ Test success message")
        
        print("✅ Logger configured successfully")
        print("   - All logging methods working")
        print("   - Check logs/app.log for output")
        return True
    except Exception as e:
        print(f"❌ Logger setup failed: {str(e)}")
        return False


async def test_model_manager_methods():
    """Test ModelManager methods exist"""
    print("\n" + "="*60)
    print("TEST 5: ModelManager Methods")
    print("="*60)
    try:
        from ai_career_advisor.core.model_manager import ModelManager
        
        methods = [
            'get_available_gemini_model',
            'get_next_gemini_key',
            'mark_model_rate_limited',
            'mark_model_available',
            'generate_with_gemini',
            'generate_with_perplexity',
            'generate_smart',
            'reset_all_models',
        ]
        
        all_ok = True
        for method in methods:
            if hasattr(ModelManager, method):
                print(f"✅ {method:<35} exists")
            else:
                print(f"❌ {method:<35} MISSING")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print(f"❌ Method check failed: {str(e)}")
        return False


async def test_file_structure():
    """Test that all required files exist"""
    print("\n" + "="*60)
    print("TEST 6: File Structure")
    print("="*60)
    
    backend_dir = Path(__file__).parent
    files_to_check = [
        "src/ai_career_advisor/core/model_manager.py",
        "src/ai_career_advisor/core/config.py",
        "src/ai_career_advisor/services/college_details_extractor.py",
        "src/ai_career_advisor/services/career_llm.py",
        "src/ai_career_advisor/services/career_insight_llm.py",
        "src/ai_career_advisor/services/backward_planner_llm.py",
        "logs/",
        ".env",
    ]
    
    all_ok = True
    for file_path in files_to_check:
        full_path = backend_dir / file_path
        exists = full_path.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {file_path:<50} {'exists' if exists else 'MISSING'}")
        if not exists and file_path != ".env":
            all_ok = False
    
    return all_ok


async def run_all_tests():
    """Run all tests and report results"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  API FALLBACK SYSTEM - VERIFICATION TESTS".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("File Structure", test_file_structure),
        ("ModelManager Imports", test_model_manager_imports),
        ("Config Loading", test_config_loading),
        ("Logger Setup", test_logger_setup),
        ("Service Imports", test_service_imports),
        ("ModelManager Methods", test_model_manager_methods),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {str(e)}")
            results.append((name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<10} {name}")
    
    print("\n" + "-"*60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your fallback system is ready to go!")
        print("\nNext steps:")
        print("1. Verify .env has all required API keys")
        print("2. Restart backend: python -m uvicorn ai_career_advisor.app:app --reload")
        print("3. Test college finder to verify fallback works")
        print("4. Monitor logs: tail -f logs/app.log | grep '✅\\|🔴'")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Make sure all dependencies are installed: pip install -e .")
        print("2. Check that .env file exists with required keys")
        print("3. Verify Python version is 3.10+")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
