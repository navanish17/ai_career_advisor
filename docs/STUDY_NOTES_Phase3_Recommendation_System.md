# Study Notes: Recommendation Systems

## Core Concepts

### 1. Content-Based Filtering
> "Recommend items similar to what the user liked before"

**How it works:**
- Extract features from items (careers → skills, salary, education)
- Extract features from user (quiz answers → interests, skills)
- Calculate similarity between user profile and each career
- Rank by similarity score

**Similarity Metrics:**
- **Jaccard Similarity**: Great for sets (skills)
  ```
  J(A,B) = |A ∩ B| / |A ∪ B|
  ```
- **Cosine Similarity**: Great for vectors (embeddings)
  ```
  cos(θ) = (A · B) / (||A|| × ||B||)
  ```

---

### 2. Collaborative Filtering
> "Users like you also liked these careers"

**Types:**
- **User-User**: Find users similar to you → recommend what they liked
- **Item-Item**: Find careers similar to ones you liked

**Matrix Factorization:**
```
User-Item Matrix (ratings/interactions)
    | Career1 | Career2 | Career3 |
U1  |    5    |    ?    |    3    |
U2  |    ?    |    4    |    5    |
U3  |    4    |    4    |    ?    |

→ Decompose into User and Item latent factors
→ Predict missing values
```

---

### 3. Hybrid Approach
> "Combine content + collaborative for best results"

**Why hybrid is better:**
| Problem | Solution |
|---------|----------|
| Cold start (new users) | Fallback to content-based |
| Cold start (new items) | Fallback to content features |
| Sparse data | Combine signals |

---

## Cold Start Problem

**The Challenge:** How to recommend when you have no data?

**Solutions implemented:**
1. **New User** → Ask quiz questions → Content-based
2. **New Career** → Use career attributes → Content-based
3. **Popularity-based** → Show top careers overall

---

## Evaluation Metrics (For Interviews)

| Metric | Formula | Meaning |
|--------|---------|---------|
| **Precision@K** | Relevant in top-K / K | Are recommendations relevant? |
| **Recall@K** | Relevant in top-K / Total relevant | Did we find all relevant? |
| **MAP** | Mean Average Precision | Overall ranking quality |
| **NDCG** | Normalized DCG | Position-aware quality |

---

## YouTube Resources

### Beginner (Start Here)
1. **"Recommendation Systems Explained"** - StatQuest
   - Search: "StatQuest recommendation systems"
   - ~15 mins, great visual explanation

2. **"Building a Recommendation System with Python"** - Krish Naik
   - Search: "Krish Naik recommendation system"
   - Hands-on coding tutorial

### Intermediate
3. **"Collaborative Filtering from Scratch"** - Sentdex
   - Search: "Sentdex collaborative filtering"
   - Implementation focused

4. **"Matrix Factorization for Recommendations"** - ritvikmath
   - Search: "ritvikmath matrix factorization"
   - Math explained simply

### Advanced
5. **"Real-World Recommendation Systems"** - Netflix/Spotify talks
   - Search: "Netflix recommendation system architecture"
   - Production-scale insights

---

## Interview Questions

### Basic Level

**Q1: What is the difference between content-based and collaborative filtering?**
> Content-based uses item features and user preferences to find similar items. Collaborative filtering uses user behavior patterns to find similar users/items. Content-based doesn't need other users' data; collaborative filtering needs a user-item interaction matrix.

**Q2: What is the cold start problem?**
> When a new user or new item joins the system, we have no historical data to base recommendations on. Solutions: collect explicit preferences (quiz), use demographic data, or fallback to popularity-based recommendations.

**Q3: How do you evaluate a recommendation system?**
> Offline: Precision@K, Recall, NDCG, MAP. Online: A/B testing, click-through rate, conversion rate, user engagement time.

### Intermediate Level

**Q4: How does matrix factorization work?**
> We decompose a sparse user-item matrix into two lower-dimensional matrices (user factors and item factors). The dot product of these factors approximates the original matrix, including missing values which become predictions.

**Q5: How do you handle implicit feedback vs explicit feedback?**
> Explicit = ratings (1-5 stars). Implicit = clicks, views, time spent. For implicit: treat interactions as binary (interacted/not), use confidence weighting (more views = higher confidence), or treat view duration as signal strength.

**Q6: What is the popularity bias problem?**
> Popular items get recommended more → get more clicks → become more popular. Solutions: diversity injection, explore-exploit strategies, personalization weighting.

### Advanced Level

**Q7: How would you design a recommendation system for millions of users?**
> - Approximate Nearest Neighbors (ANN) for similarity search (FAISS, Annoy)
> - Pre-compute recommendations offline, serve from cache
> - Two-stage: candidate generation (fast, rough) → ranking (slow, precise)
> - Feature store for real-time features

**Q8: How do you ensure diversity in recommendations?**
> - MMR (Maximal Marginal Relevance): penalize similarity to already-selected items
> - Coverage constraints: ensure all categories represented
> - Exploration slots: reserve some positions for discovery

---

## Your Implementation Talking Points

When asked "Tell me about your recommendation system":

1. **Architecture**: "I built a hybrid system combining content-based and collaborative filtering"
2. **Content-Based**: "Used Jaccard similarity for skill matching between user profiles and career requirements"
3. **Cold Start**: "New users take a quiz, which feeds into content-based recommendations until we have interaction data"
4. **Fallback Strategy**: "Content-based → Collaborative → Popularity-based, depending on data availability"
5. **Real Use Case**: "For Indian students choosing careers after 10th/12th with varying interests and constraints"
