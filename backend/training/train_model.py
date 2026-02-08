import mlflow
import os
import random

# --- CONFIGURATION (Load from Env) ---
# Ensure you set these environment variables!
DAGSHUB_TOKEN = os.getenv("DAGSHUB_TOKEN")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
MLFLOW_TRACKING_USERNAME = os.getenv("MLFLOW_TRACKING_USERNAME")
MLFLOW_TRACKING_PASSWORD = os.getenv("MLFLOW_TRACKING_PASSWORD")

if not MLFLOW_TRACKING_URI:
    print("❌ Error: MLFLOW_TRACKING_URI not set. Please check your .env or secrets.")
    exit(1)

# --- SETUP MLFLOW ---
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
experiment_name = "AI-Career-Advisor-Embeddings"
mlflow.set_experiment(experiment_name)

print(f"✅ Logging to Dagshub: {MLFLOW_TRACKING_URI}")

# --- DUMMY TRAINING FUNCTION ---
# Simulate training a small model or tuning embeddings
def train_model(learning_rate, epochs):
    with mlflow.start_run():
        print(f"🚀 Starting run with lr={learning_rate}, epochs={epochs}...")
        
        # Log Parameters
        mlflow.log_param("learning_rate", learning_rate)
        mlflow.log_param("epochs", epochs)
        mlflow.log_param("model_type", "sentence-transformer-finetune")

        # Simulate Training Loop
        for epoch in range(epochs):
            # Simulate metrics
            accuracy = 0.5 + (0.4 * (epoch / epochs)) + (random.random() * 0.05)
            loss = 1.0 - (0.8 * (epoch / epochs)) + (random.random() * 0.05)
            
            # Log Metrics
            mlflow.log_metric("accuracy", accuracy, step=epoch)
            mlflow.log_metric("loss", loss, step=epoch)
            print(f"   Epoch {epoch+1}: Acc={accuracy:.4f}, Loss={loss:.4f}")

        # Log Artifact (Dummy model file)
        with open("model.txt", "w") as f:
            f.write(f"Model trained with lr={learning_rate}")
        mlflow.log_artifact("model.txt")
        os.remove("model.txt")
        
        print("✅ Training complete. Metrics logged to Dagshub.")

if __name__ == "__main__":
    # Simulate a training run
    train_model(learning_rate=0.01, epochs=5)
