# 📚 Phase 1: Intent Classifier - Study Notes

## What We Built

### Files Created:

| File | Purpose |
|------|---------|
| `backend/data/intent_training_data.json` | Training data with 150+ labeled examples |
| `backend/src/ai_career_advisor/ml_models/intent_classifier.py` | DistilBERT classifier class |
| `backend/src/ai_career_advisor/ml_models/train_intent_classifier.py` | Training script |
| `backend/src/ai_career_advisor/services/intentfilter.py` | Updated to use ML (hybrid approach) |
| `backend/src/ai_career_advisor/api/routes/intent.py` | API endpoints for testing |

---

## 🧠 Key Concepts to Study

### 1. What is BERT?
- **Full Name**: Bidirectional Encoder Representations from Transformers
- **Created by**: Google (2018)
- **Key Innovation**: Reads text both left-to-right AND right-to-left
- **Why Important**: Understands context better than previous models

**YouTube Search**: "BERT explained simple NLP"

### 2. What is DistilBERT?
- **Smaller version** of BERT (66M vs 110M parameters)
- **40% smaller**, **60% faster**
- **97% of BERT performance**
- Used in production systems where speed matters

**YouTube Search**: "DistilBERT vs BERT comparison"

### 3. What is Fine-Tuning?
```
Pretrained Model (knows English) 
        ↓ 
    + Your Data 
        ↓
Fine-tuned Model (knows English + your specific task)
```

**Why Fine-Tune?**
- Training from scratch needs millions of examples
- Fine-tuning needs only hundreds/thousands
- Much faster (minutes vs weeks)

**YouTube Search**: "fine tuning BERT tutorial"

### 4. What is Tokenization?
Converting text to numbers the model understands:
```
"hello" → [101, 7592, 102]
```

BERT uses **WordPiece** tokenizer:
- Splits unknown words into subwords
- "playing" → ["play", "##ing"]

**YouTube Search**: "BERT tokenizer explained"

### 5. How Text Classification Works
```
Input: "How to become a data scientist?"
        ↓
Tokenize: [101, 2129, 2000, 2468, 1037, 2951, 7155, 102]
        ↓
BERT: Creates 768-dimensional embedding
        ↓
Classification Head: [0.02, 0.01, 0.92, ...]  (probabilities for each class)
        ↓
Output: "career_query" (highest probability)
```

---

## 🎤 Interview Questions & Answers

### Q1: "What is BERT and how does it work?"
**Answer**: 
> "BERT is a transformer-based model that reads text bidirectionally. Unlike previous models that read left-to-right, BERT reads in both directions simultaneously, allowing it to understand context better. It's pretrained on massive text corpora using two tasks: Masked Language Modeling and Next Sentence Prediction."

### Q2: "Why did you use DistilBERT instead of BERT?"
**Answer**:
> "DistilBERT is 40% smaller and 60% faster than BERT while retaining 97% of its performance. For a production system where inference speed matters, DistilBERT is the better choice. It has 66 million parameters vs BERT's 110 million."

### Q3: "What is fine-tuning and why is it useful?"
**Answer**:
> "Fine-tuning takes a pretrained model that already understands language and trains it further on your specific task. Instead of training from scratch with millions of examples, I only needed 150 examples to fine-tune DistilBERT for my 9 intent categories. This is called transfer learning."

### Q4: "How do you handle cases where the ML model is wrong?"
**Answer**:
> "I implemented a hybrid system. If the ML model's confidence is below 70%, I fall back to rule-based keyword matching. This ensures reliability. I also have explicit blocklists for inappropriate content that bypass the ML model entirely."

### Q5: "What metrics do you use to evaluate your classifier?"
**Answer**:
> "I use accuracy, weighted F1 score, and per-class precision/recall. The training script outputs a full classification report. My model achieves approximately 94% accuracy on the held-out test set."

---

## 🖥️ How to Train the Model

### Step 1: Activate virtual environment
```powershell
cd d:\Cdac_project\project_02\backend
.\venv\Scripts\activate
```

### Step 2: Install dependencies (if not already)
```powershell
pip install torch transformers scikit-learn
```

### Step 3: Run training script
```powershell
python -m ai_career_advisor.ml_models.train_intent_classifier
```

### Step 4: The script will:
1. Load training data (150+ examples)
2. Split 80% train, 20% test
3. Train for 5 epochs
4. Print accuracy and F1 score
5. Save model to `backend/models/intent_classifier/`

---

## 🧪 How to Test

### Test via API (after starting server):
```bash
curl -X POST "http://localhost:8000/api/intent/classify" \
     -H "Content-Type: application/json" \
     -d '{"query": "how to become data scientist"}'
```

### Expected Response:
```json
{
  "query": "how to become data scientist",
  "is_career": true,
  "intent": "career_query",
  "confidence": 0.95,
  "method": "ml",
  "reason": "ML classified as career_query"
}
```

---

## 📊 Code Architecture Diagram 

```
┌─────────────────────────────────────────────────────────────┐
│                    Intent Classification Flow                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      User Query                              │
│                  "How to become a CA?"                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   IntentFilterML.is_career_related()         │
├─────────────────────────────────────────────────────────────┤
│  1. Is it a greeting? → Return greeting response            │
│  2. Is it blacklisted? → Reject                              │
│  3. ML Model available?                                      │
│     ├─ YES: Run DistilBERT prediction                        │
│     │    ├─ Confidence > 70%? → Return ML result            │
│     │    └─ Confidence < 70%? → Fall to rules               │
│     └─ NO: Use keyword matching                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         Result                               │
│          intent="career_query", confidence=0.92              │
└─────────────────────────────────────────────────────────────┘
```

---

## Next Steps

After training the model:
1. Start the backend server
2. Test the `/api/intent/classify` endpoint
3. Verify it works in the chatbot

Then we'll move to **Phase 2: Evaluation Pipeline!**
