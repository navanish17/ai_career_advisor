"""
Training Script for Intent Classifier

HOW TO RUN THIS SCRIPT:
==========================
cd backend
python -m ai_career_advisor.ml_models.train_intent_classifier

WHAT THIS SCRIPT DOES:
=========================
1. Loads training data from JSON file
2. Splits into train/test sets (80/20)
3. Fine-tunes DistilBERT model
4. Evaluates on test set
5. Saves the trained model

INTERVIEW KEY POINTS:
========================
- Fine-tuning = Taking pretrained model + training on your specific data
- Only 5 epochs needed because BERT already knows language
- 80/20 split = 80% training, 20% for testing
- Stratified split = Each class is equally represented in train/test
"""

import json
import os
import sys
import io
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import time
import mlflow
import dagshub


# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from ai_career_advisor.ml_models.intent_classifier import IntentClassifier


def load_training_data(data_path: str):
    """Load training data from JSON file"""
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    texts = [item['text'] for item in data['training_data']]
    labels = [item['label'] for item in data['training_data']]
    
    return texts, labels


def main():
    print("=" * 60)
    print("[START] Intent Classifier Training Script")
    print("=" * 60)
    
    # Paths
    base_path = Path(__file__).parent.parent.parent.parent
    data_path = base_path / "data" / "intent_training_data.json"
    model_save_path = base_path / "models" / "intent_classifier"
    
    # MLOps: Initialize Dagshub (if configured) or use local MLflow
    # Using a try-block to ensure it works even if Dagshub isn't set up yet
    try:
        dagshub.init(repo_name="ai_career_advisor", repo_owner="navanish17", mlflow=True)
        print("\n[MLOPS] Dagshub integration initialized")
    except Exception as e:
        print(f"\n[MLOPS] Dagshub warning (continuing with local MLflow): {e}")

    # Create models directory
    
    # Create models directory
    model_save_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print("\n[LOAD] Loading training data...")
    texts, labels = load_training_data(str(data_path))
    print(f"   Total examples: {len(texts)}")
    
    # Show class distribution
    from collections import Counter
    label_counts = Counter(labels)
    print("\n[INFO] Class distribution:")
    for label, count in sorted(label_counts.items()):
        print(f"   {label}: {count}")
    
    # Split data
    print("\n[SPLIT] Splitting data (80% train, 20% test)...")
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        texts, labels, 
        test_size=0.2, 
        random_state=42,
        stratify=labels  # Ensures balanced split
    )
    print(f"   Training examples: {len(train_texts)}")
    print(f"   Test examples: {len(test_texts)}")
    
    # Initialize classifier
    print("\n[INIT] Initializing DistilBERT classifier...")
    classifier = IntentClassifier()
    
    # Train
    # Train with MLflow tracking
    print("\n[TRAIN] Starting training with MLflow tracking...")
    print("-" * 40)
    start_time = time.time()
    
    # MLflow Experiment
    mlflow.set_experiment("Intent Classifier Training")
    
    with mlflow.start_run():
        # Log Hyperparameters
        params = {
            "epochs": 10,
            "batch_size": 16,
            "learning_rate": 2e-5,
            "base_model": "distilbert-base-uncased"
        }
        mlflow.log_params(params)
        
        history = classifier.train(
            train_texts=train_texts,
            train_labels=train_labels,
            epochs=params["epochs"],
            batch_size=params["batch_size"],
            learning_rate=params["learning_rate"],
            save_path=str(model_save_path)
        )
        
        training_time = time.time() - start_time
        
        # Log Metrics (Final)
        mlflow.log_metric("final_val_accuracy", history['val_accuracy'][-1])
        mlflow.log_metric("final_val_f1", history['val_f1'][-1])
        mlflow.log_metric("training_time_seconds", training_time)
        
        # Log Metrics (Per Epoch)
        for i, acc in enumerate(history['val_accuracy']):
            mlflow.log_metric("val_accuracy_epoch", acc, step=i+1)
            
        # Log Model Artifacts
        mlflow.log_artifacts(str(model_save_path), artifact_path="model")
        print("   ✅ Model artifacts logged to MLflow")

    print("-" * 40)
    print(f"\n[TIME] Training completed in {training_time:.1f} seconds")
    
    # Evaluate on test set
    print("\n[EVAL] Evaluating on test set...")
    predictions = []
    for text in test_texts:
        intent, conf = classifier.predict(text)
        predictions.append(intent)
    
    # Print classification report
    print("\n" + "=" * 60)
    print("[REPORT] Classification Report:")
    print("=" * 60)
    print(classification_report(test_labels, predictions))
    
    # Test with some examples
    print("\n" + "=" * 60)
    print("[TEST] Testing with sample queries:")
    print("=" * 60)
    
    test_queries = [
        "hello how are you",
        "how to become a data scientist",
        "best iit colleges in india",
        "create a roadmap for software engineer",
        "what is JEE exam pattern",
        "what is btech degree",
        "suggest me a career",
        "what is the weather today",
        "thanks bye"
    ]
    
    for query in test_queries:
        intent, confidence = classifier.predict(query)
        print(f"\n   Query: \"{query}\"")
        print(f"   Intent: {intent} (confidence: {confidence:.2%})")
    
    print("\n" + "=" * 60)
    print(f"[DONE] Model saved to: {model_save_path}")
    print("=" * 60)
    
    # Print metrics summary for interview
    print("\n[METRICS] FOR INTERVIEW:")
    print("-" * 40)
    print(f"   Final Validation Accuracy: {history['val_accuracy'][-1]:.2%}")
    print(f"   Final Validation F1 Score: {history['val_f1'][-1]:.2%}")
    print(f"   Training Time: {training_time:.1f} seconds")
    print(f"   Model Size: DistilBERT (66M parameters)")
    print(f"   Number of Classes: 9 intents")


if __name__ == "__main__":
    main()
