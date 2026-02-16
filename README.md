---
title: AI Career Pilot
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 7860
---

# 🚀 AI Career Pilot
#testing

**AI Career Pilot** is an intelligent career guidance platform designed to help students make informed decisions about their academic and professional future. The platform leverages advanced AI technologies including RAG (Retrieval-Augmented Generation), natural language processing, and machine learning to provide personalized career recommendations, roadmaps, and college suggestions.

---

## ✨ Key Features

### 🤖 AI-Powered Chatbot
- **Intelligent Conversations**: Get answers to all your career-related queries in real-time
- **Bilingual Support**: Responds in English by default, with automatic Hindi/Hinglish detection
- **RAG-First Architecture**: Retrieves accurate, contextual information from curated knowledge base
- **Smart Model Fallback**: Automatic switching between Gemini 2.5 Flash → Flash-Lite → Perplexity Sonar-Pro when rate-limited
- **Source Citations**: AI responses include credible source links (powered by Perplexity)
- **Intent Classification**: ML-powered query understanding using fine-tuned DistilBERT (92% accuracy)
- **Feature Recommendations**: Smart detection suggests relevant platform features based on your queries

### 🗺️ Career Roadmap Generator
- **Forward Planning**: Start from your current education level and explore possible career paths
- **Backward Planning**: Define your dream career goal and get a step-by-step path from your current position
- **Personalized Timelines**: Visual roadmaps with milestones, exams, and key deadlines
- **Save & Track Progress**: Save multiple roadmaps to revisit and track your journey
- **Share Roadmaps**: Generate public shareable links for your career roadmaps

### 📋 Career Assessment Quiz
- **Interest-Based Analysis**: Discover your ideal stream (Science, Commerce, Arts) through interactive quizzes
- **Personality Mapping**: Understand your strengths and inclinations
- **Personalized Recommendations**: Get career suggestions aligned with your interests

### 🎓 Degree & Branch Explorer
- **Comprehensive Database**: Browse detailed information about degrees across all streams
- **Branch Comparisons**: Explore specializations within each degree program
- **Career Pathways**: Understand the career opportunities each degree unlocks

### 🏫 College Finder
- **Smart Search**: Find colleges based on course, location, and ranking
- **NIRF Rankings**: Access official National Institutional Ranking Framework data
- **College Details**: View comprehensive information including programs, fees, and admission criteria
- **Admission Alerts**: Subscribe to receive email notifications about admission deadlines

### 📧 Email Alert System
- **Automated Notifications**: Get timely alerts about admissions, entrance exams, and deadlines
- **Personalized Subscriptions**: Subscribe to specific colleges or programs
- **Scheduled Reminders**: Never miss important dates with automated scheduling

### 🌗 Theme Support
- **Light & Dark Modes**: Choose your preferred visual theme
- **System Theme Detection**: Automatically adapts to your system preferences

---

## 🛠️ Getting Started

### Prerequisites

Ensure you have the following installed on your system:
- **Node.js** (v18 or higher)
- **Python** (v3.10 or higher)
- **Git**

### Step 1: Clone the Repository

```bash
git clone https://github.com/navanish17/ai_career_pilot.git
cd ai_career_pilot
```

### Step 2: Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **Linux/Mac:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables:**
   
   Create a `.env` file in the `backend` directory:
   ```env
   # AI API Keys
   PERPLEXITY_API_KEY=your_perplexity_api_key
   GOOGLE_API_KEY=your_google_gemini_api_key
   
   # Email Service (Brevo)
   BREVO_API_KEY=your_brevo_api_key
   SENDER_EMAIL=your_sender_email
   
   # JWT Authentication
   JWT_SECRET_KEY=your_secret_key
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # Database
   DATABASE_URL=sqlite+aiosqlite:///./dev.db
   ```

6. **Initialize the database:**
   ```bash
   python -m alembic upgrade head
   ```

7. **Start the backend server:**
   ```bash
   uvicorn ai_career_advisor.main:app --reload --port 8000
   ```

### Step 3: Frontend Setup

1. **Navigate to the frontend directory (in a new terminal):**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   
   Create a `.env` file in the `frontend` directory:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   ```

5. **Access the application:**
   
   Open your browser and navigate to `http://localhost:5173`

---

## 📖 How to Use AI Career Pilot

### 1️⃣ Create an Account
- Click on **Sign Up** to create a new account
- Complete the **onboarding process** to set your class level, stream, and preferences

### 2️⃣ Explore the Dashboard
After logging in, you'll see your personalized dashboard with:
- **Your Profile**: View and update your learning preferences
- **Quick Actions**: Access all main features with one click

### 3️⃣ Use the AI Chatbot
- Click the **floating chat icon** in the bottom-right corner
- Ask any career-related question like:
  - "What are the best engineering colleges in India?"
  - "How can I become a Data Scientist?"
  - "What exams should I prepare for after 12th Science?"

### 4️⃣ Take the Career Quiz
- Navigate to **Career Quiz**
- Answer interest-based questions
- Get personalized stream recommendations

### 5️⃣ Generate Career Roadmaps
- Go to **Roadmap Generator**
- Choose **Forward Planning** (explore from current position) or **Backward Planning** (define end goal)
- Enter your career goal (e.g., "Software Engineer at Google")
- View the generated visual roadmap with milestones
- **Save** the roadmap for future reference

### 6️⃣ Find Colleges
- Navigate to **College Finder**
- Search by course, location, or college name
- View college details including ranking, programs, and fees
- **Subscribe** to colleges for admission alerts

### 7️⃣ Explore Degrees
- Go to **Explore Degrees**
- Browse available degrees and their specializations
- Understand career pathways for each degree

---

## 🔧 Technical Architecture

### Frontend Stack

| Technology | Purpose |
|------------|---------|
| **React 18** | UI library for building interactive interfaces |
| **TypeScript** | Type-safe JavaScript for better code quality |
| **Vite** | Fast build tool and development server |
| **Tailwind CSS** | Utility-first CSS framework for styling |
| **Shadcn/UI** | Radix-based component library |
| **React Router v6** | Client-side routing and navigation |
| **TanStack Query** | Async state management and data fetching |
| **React Hook Form** | Form handling with Zod validation |
| **Recharts** | Data visualization for roadmap timelines |
| **Lucide React** | Modern icon library |

### Backend Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance asynchronous Python web framework |
| **Python 3.10+** | Core backend language |
| **SQLAlchemy** | Async ORM for database operations |
| **Alembic** | Database migration management |
| **SQLite** | Lightweight database (dev), supports PostgreSQL |
| **Pydantic** | Data validation and serialization |
| **JWT (python-jose)** | Secure authentication tokens |
| **Passlib (bcrypt)** | Password hashing |
| **APScheduler** | Background job scheduling for email alerts |

### AI/ML Technologies

| Technology | Purpose |
|------------|---------|
| **LangGraph** | Multi-agent orchestration with stateful conversation graphs |
| **DistilBERT** | Fine-tuned intent classifier (92% F1-score on career queries) |
| **RAG System** | Retrieval-Augmented Generation with ChromaDB vector store |
| **ChromaDB** | Vector database for semantic document retrieval |
| **Gemini 2.5 Flash** | Primary LLM with automatic fallback to Flash-Lite |
| **Perplexity Sonar-Pro** | Fallback LLM with real-time web search and citations |
| **Sentence Transformers** | Text embeddings for similarity search |
| **NLTK** | Natural language processing utilities |
| **Scikit-learn** | Machine learning utilities and evaluation metrics |

### External Services

| Service | Purpose |
|---------|---------|
| **Brevo (Sendinblue)** | Transactional email service for alerts |
| **Perplexity API** | Real-time web search and AI responses |
| **Google Generative AI** | Advanced language model capabilities |

---

## 📁 Project Structure

```
ai_career_advisor/
├── backend/
│   └── src/
│       └── ai_career_advisor/
│           ├── agents/              # LangGraph agent system
│           │   ├── career_agent.py  # Main agent with state graph
│           │   └── tools.py         # Agent tools and utilities
│           ├── api/
│           │   └── routes/          # API endpoints
│           ├── core/                # Configuration and logging
│           │   ├── config.py        # Settings management
│           │   ├── model_manager.py # Smart model fallback system
│           │   └── logger.py        # Logging utilities
│           ├── ml_models/           # Machine learning models
│           │   ├── intent_classifier.py      # DistilBERT classifier
│           │   └── train_intent_classifier.py # Training script
│           ├── models/              # Database models
│           ├── RAG/                 # Retrieval-Augmented Generation
│           │   ├── embeddings.py    # Text embedding generation
│           │   ├── retriever.py     # Knowledge retrieval
│           │   ├── vector_store.py  # ChromaDB operations
│           │   └── knowledge_loader.py # Document ingestion
│           ├── schemas/             # Pydantic schemas
│           └── services/            # Business logic
│               ├── chatbot_service.py
│               ├── roadmap_service.py
│               ├── college_service.py
│               ├── backward_roadmap_service.py
│               └── ... (other services)
│
├── frontend/
│   └── src/
│       ├── components/              # Reusable UI components
│       │   ├── chat/               # Chatbot components
│       │   ├── college/            # College finder components
│       │   └── ui/                 # Shadcn/UI components
│       ├── contexts/               # React context providers
│       ├── hooks/                  # Custom React hooks
│       ├── pages/                  # Page components
│       │   ├── auth/               # Login/Signup
│       │   ├── career/             # Career exploration
│       │   ├── college/            # College search
│       │   ├── onboarding/         # User onboarding
│       │   └── roadmap/            # Roadmap features
│       ├── types/                  # TypeScript type definitions
│       └── lib/                    # Utility functions
│
├── .github/
│   └── workflows/                  # CI/CD pipelines
│       ├── ci-cd.yml              # Main deployment workflow
│       └── sync_to_hf_space.yml   # Hugging Face Spaces sync
├── data/                           # Static data files
├── configs/                        # Configuration files
├── docs/                           # Documentation
├── Dockerfile                      # Multi-stage production build
└── docker-compose.yml              # Docker orchestration
```

---

## 🔑 Key Technical Implementations

### Intelligent Agent Architecture (LangGraph)

The chatbot uses a sophisticated **multi-agent system** built with LangGraph, providing stateful, context-aware conversations:

```mermaid
graph TD
    A[User Query] --> B[Intent Detection Node]
    B --> C{Intent Router}
    C -->|Greeting| D[Greeting Node]
    C -->|Non-Career| E[Rejection Node]
    C -->|Career Query| F[Tool Selection Node]
    C -->|Roadmap Request| F
    F --> G[RAG Retrieval]
    F --> H[Database Query]
    G --> I[Synthesis Node]
    H --> I
    I --> J[Model Fallback Chain]
    J -->|Primary| K[Gemini 2.5 Flash]
    J -->|Fallback 1| L[Gemini 2.5 Flash-Lite]
    J -->|Fallback 2| M[Perplexity Sonar-Pro]
    K --> N[Response with Citations]
    L --> N
    M --> N
    D --> O[End]
    E --> O
    N --> O
```

**Agent Nodes:**
1. **Intent Detection**: Uses fine-tuned DistilBERT to classify queries (greeting, career-related, rejected)
2. **Greeting Node**: Handles welcome messages in English/Hindi
3. **Rejection Node**: Politely redirects non-career queries
4. **Tool Selection**: Executes RAG retrieval, database lookups, or roadmap generation
5. **Synthesis Node**: Generates final response using LLM with context augmentation

### DistilBERT Intent Classification

**Why DistilBERT?**
- 40% smaller and 60% faster than BERT
- Retains 97% of BERT's language understanding
- Perfect for real-time intent detection

**Performance Metrics:**
- **Accuracy**: 92%
- **F1-Score**: 92%
- **Training Data**: 500+ labeled career-related queries
- **Model**: `distilbert-base-uncased` fine-tuned on domain-specific data

**Classification Pipeline:**
```
User Query → Tokenizer → DistilBERT Encoder → Classification Head → Intent Label
```

**Intent Categories:**
- `greeting`: Welcome messages
- `career_query`: General career questions
- `roadmap_request`: Career path planning queries
- `rejected`: Non-career topics

### Smart Model Fallback System

**3-Tier Fallback Chain:**

```python
# Automatic fallback with rate limit handling
1. Gemini 2.5 Flash (Primary)
   ├─ Fast, cost-effective
   └─ If rate-limited → Try next

2. Gemini 2.5 Flash-Lite (Secondary)
   ├─ Lighter, faster variant
   └─ If rate-limited → Try next

3. Perplexity Sonar-Pro (Tertiary)
   ├─ Web-search augmented
   ├─ Returns citations
   └─ Final fallback
```

**Features:**
- Automatic API key rotation (supports multiple Gemini keys)
- Rate limit detection and model switching
- Citation extraction from Perplexity responses
- Zero downtime during model transitions

### RAG (Retrieval-Augmented Generation) System
- **Document Ingestion**: Career-related documents are chunked and embedded
- **Vector Storage**: ChromaDB stores embeddings for fast similarity search
- **Semantic Retrieval**: User queries are matched against the knowledge base
- **Context Augmentation**: Retrieved chunks enhance LLM responses with accurate information

### Backward Planning Algorithm
- **Goal Decomposition**: Breaks down career goals into achievable milestones
- **Timeline Generation**: Creates realistic timelines based on user's current status
- **Prerequisite Mapping**: Identifies required exams, degrees, and skills

### Authentication System
- **JWT-based Auth**: Secure token-based authentication
- **Password Hashing**: bcrypt encryption for passwords
- **Protected Routes**: Frontend route guards for authenticated pages

---

## 🚀 DevOps & MLOps

### CI/CD Pipeline

**GitHub Actions Workflow:**
```yaml
1. Test Stage
   ├─ Python 3.10 setup
   ├─ Install dependencies
   └─ Run pytest (if tests exist)

2. Build & Push Stage
   ├─ Docker Hub login
   ├─ Multi-stage Docker build
   └─ Push image: ai-career-advisor-backend:latest

3. Deploy Stage
   └─ Trigger Render deploy hook
```

**Workflow File:** `.github/workflows/ci-cd.yml`

### Containerization

**Multi-Stage Dockerfile:**
- **Stage 1 (Builder)**: Compiles Python wheels with dependencies
- **Stage 2 (Runtime)**: Minimal production image with non-root user
- **Server**: Gunicorn + Uvicorn workers (2 workers for 2 vCPU)
- **Port**: 7860 (Hugging Face Spaces compatible)

### MLOps Integration

| Tool | Purpose |
|------|---------|
| **MLflow** | Experiment tracking and model registry |
| **DVC** | Data version control for datasets and models |
| **DagHub** | Collaborative MLOps platform integration |

**Model Versioning:**
- DistilBERT intent classifier tracked in MLflow
- Training metrics logged (accuracy, F1-score, loss)
- Model artifacts stored with DVC

### Deployment Platforms

| Platform | Component | URL |
|----------|-----------|-----|
| **Render** | Backend API | Production backend hosting |
| **Vercel** | Frontend | React app deployment |
| **Hugging Face Spaces** | Full Stack | Docker-based deployment (optional) |

**Environment Variables (Production):**
```env
# AI APIs
PERPLEXITY_API_KEY=<your_key>
GOOGLE_API_KEY=<your_key>

# Email Service
BREVO_API_KEY=<your_key>
SENDER_EMAIL=<your_email>

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host/db

# JWT
JWT_SECRET_KEY=<strong_secret>
```

---

## � Deployment

### Local Development (Docker Compose)

```bash
# Clone the repository
git clone https://github.com/navanish17/ai_career_pilot.git
cd ai_career_pilot

# Start all services
docker-compose up --build
```

Access the application at `http://localhost:5173`

### Production Deployment

#### Backend (Render)

1. **Create a new Web Service** on [Render](https://render.com)
2. **Connect your GitHub repository**
3. **Configure build settings:**
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && gunicorn src.ai_career_advisor.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
4. **Add environment variables** (see Production Environment Variables below)
5. **Deploy** - Render will automatically deploy on push to main

#### Frontend (Vercel)

1. **Import project** on [Vercel](https://vercel.com)
2. **Configure:**
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
3. **Add environment variable:**
   - `VITE_API_URL`: Your Render backend URL
4. **Deploy** - Vercel will auto-deploy on push

#### Hugging Face Spaces (Optional)

The project includes a sync workflow (`.github/workflows/sync_to_hf_space.yml`) for automatic deployment to Hugging Face Spaces.

**Setup:**
1. Create a new Docker Space on [Hugging Face](https://huggingface.co/spaces)
2. Add GitHub secrets:
   - `HF_USERNAME`: Your Hugging Face username
   - `HF_TOKEN`: Your Hugging Face access token
3. Push to main - GitHub Actions will sync automatically

### Production Environment Variables

**Backend (.env):**
```env
# AI APIs
PERPLEXITY_API_KEY=your_perplexity_api_key
GOOGLE_API_KEY=your_google_gemini_api_key
GEMINI_API_KEY_2=optional_second_key  # For rate limit handling
GEMINI_API_KEY_3=optional_third_key

# Email Service (Brevo)
BREVO_API_KEY=your_brevo_api_key
SENDER_EMAIL=noreply@yourdomain.com

# JWT Authentication
JWT_SECRET_KEY=generate_strong_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database (Production - PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# CORS (Update with your frontend URL)
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

**Frontend (.env.production):**
```env
VITE_API_URL=https://your-backend.onrender.com
```

### Database Migration (Production)

```bash
# SSH into your Render instance or run locally
cd backend
alembic upgrade head
```

### Production Checklist

- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure proper CORS origins
- [ ] Set up HTTPS with SSL certificates (handled by Render/Vercel)
- [ ] Enable rate limiting on API endpoints
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy for database
- [ ] Test all API endpoints in production
- [ ] Verify email service is working
- [ ] Test model fallback chain with rate limits

---

## 📄 License

This project is developed for educational purposes as part of CDAC coursework.

---

## 👨‍💻 Author

**Navanish**

---

## 🙏 Acknowledgments

- CDAC for project guidance
- Google (Gemini), Perplexity, and OpenAI for AI capabilities
- Shadcn/UI for beautiful component library
- All open-source contributors whose libraries made this possible
