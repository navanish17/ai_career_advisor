"""
ML Models Package

This package contains machine learning models for:
- Intent Classification (BERT-based)
- Recommendation System
- Custom NER (future)
"""

from ai_career_advisor.ml_models.intent_classifier import (
    IntentClassifier,
    get_intent_classifier
)

__all__ = [
    'IntentClassifier',
    'get_intent_classifier'
]
