import statistics
from typing import List, Deque
from collections import deque
from ai_career_advisor.core.logger import logger
import mlflow

class ModelMonitor:
    """
    MLOps Monitoring Service
    Tracks model performance in production (Confidence Drift)
    """
    
    # Singleton instance
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelMonitor, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        # Sliding window of last 100 predictions
        self.confidence_window: Deque[float] = deque(maxlen=100)
        self.intent_window: Deque[str] = deque(maxlen=100)
        
        # Drift Thresholds
        self.CONFIDENCE_THRESHOLD = 0.75
        self.UNKNOWN_RATIO_THRESHOLD = 0.15
        
        logger.info("🛡️ Model Monitor Service Initialized")

    def log_prediction(self, intent: str, confidence: float, query_length: int):
        """
        Log a single prediction for monitoring
        """
        self.confidence_window.append(confidence)
        self.intent_window.append(intent)
        
        # Check for drift every 10 samples
        if len(self.confidence_window) % 10 == 0:
            self._check_for_drift()
            
    def _check_for_drift(self):
        """
        Analyze windows for performance degradation
        """
        if not self.confidence_window:
            return

        # 1. Check Confidence Drift
        avg_conf = statistics.mean(self.confidence_window)
        
        # Log to MLflow (if active run exists, or just system log)
        # In a real system, this would push to a dashboard
        
        if avg_conf < self.CONFIDENCE_THRESHOLD:
            logger.warning(f"📉 MLOps ALERT: Confidence Drift Detected! Avg: {avg_conf:.2f} (Threshold: {self.CONFIDENCE_THRESHOLD})")
            logger.warning("   -> Recommendation: Retrain intent classifier with new data")
        else:
            logger.debug(f"✅ Model Health: Confidence {avg_conf:.2f} (Healthy)")
            
        # 2. Check "Unknown" Spike
        unknown_count = self.intent_window.count("unknown") + self.intent_window.count("rejected")
        unknown_ratio = unknown_count / len(self.intent_window)
        
        if unknown_ratio > self.UNKNOWN_RATIO_THRESHOLD:
            logger.warning(f"⚠️ MLOps ALERT: Unknown Intent Spike! Ratio: {unknown_ratio:.2%} (Threshold: {self.UNKNOWN_RATIO_THRESHOLD})")
            logger.warning("   -> Action: Analyze rejected queries for new features")
            
    def get_metrics(self):
        """Get current metrics for admin dashboard"""
        if not self.confidence_window:
            return {"status": "waiting_for_data"}
            
        return {
            "avg_confidence": statistics.mean(self.confidence_window),
            "sample_size": len(self.confidence_window),
            "unknown_ratio": (self.intent_window.count("unknown") / len(self.intent_window)) if self.intent_window else 0
        }

# Global instance
monitor = ModelMonitor()
