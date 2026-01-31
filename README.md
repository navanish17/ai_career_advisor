# 🚀 AI Career Pilot

**AI Career Pilot** is an intelligent career guidance platform designed to help students make informed decisions about their academic and professional future. The platform leverages advanced AI technologies including RAG (Retrieval-Augmented Generation), natural language processing, and machine learning to provide personalized career recommendations, roadmaps, and college suggestions.

---

## ✨ Key Features

### 🤖 AI-Powered Chatbot
- **Intelligent Conversations**: Get answers to all your career-related queries in real-time
- **Bilingual Support**: Responds in English by default, with automatic Hindi/Hinglish detection
- **RAG-First Architecture**: Retrieves accurate, contextual information from curated knowledge base
- **Source Citations**: Every response includes credible sources for reference
- **Feature Recommendations**: Smart detection suggests relevant platform features based on your queries

### 🗺️ Career Roadmap Generator
- **Forward Planning**: Start from your current education level and explore possible career paths
- **Backward Planning**: Define your dream career goal and get a step-by-step path from your current position
- **Personalized Timelines**: Visual roadmaps with milestones, exams, and key deadlines
- **Save & Track Progress**: Save multiple roadmaps to revisit and track your journey

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
git clone https://github.com/navanish17/ai_career_advisor.git
cd ai_career_advisor
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
| **RAG System** | Retrieval-Augmented Generation for accurate responses |
| **ChromaDB** | Vector database for semantic search |
| **Sentence Transformers** | Text embeddings for similarity search |
| **Google Gemini** | LLM for content generation and analysis |
| **Perplexity Sonar** | Web search-augmented AI for real-time information |
| **NLTK** | Natural language processing utilities |
| **Scikit-learn** | Machine learning for intent classification |

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
│           ├── api/
│           │   └── routes/         # API endpoints
│           ├── core/               # Configuration and logging
│           ├── models/             # Database models
│           ├── RAG/                # Retrieval-Augmented Generation
│           │   ├── embeddings.py   # Text embedding generation
│           │   ├── retriever.py    # Knowledge retrieval
│           │   └── vector_store.py # Vector database operations
│           ├── schemas/            # Pydantic schemas
│           └── services/           # Business logic
│               ├── chatbot_service.py
│               ├── roadmap_service.py
│               ├── college_service.py
│               └── ... (other services)
│
├── frontend/
│   └── src/
│       ├── components/             # Reusable UI components
│       │   ├── chat/              # Chatbot components
│       │   ├── college/           # College finder components
│       │   └── ui/                # Shadcn/UI components
│       ├── contexts/              # React context providers
│       ├── hooks/                 # Custom React hooks
│       ├── pages/                 # Page components
│       │   ├── auth/              # Login/Signup
│       │   ├── career/            # Career exploration
│       │   ├── college/           # College search
│       │   ├── onboarding/        # User onboarding
│       │   └── roadmap/           # Roadmap features
│       ├── types/                 # TypeScript type definitions
│       └── lib/                   # Utility functions
│
├── data/                          # Static data files
├── configs/                       # Configuration files
├── docs/                          # Documentation
└── docker-compose.yml             # Docker orchestration
```

---

## 🔑 Key Technical Implementations

### RAG (Retrieval-Augmented Generation) System
- **Document Ingestion**: Career-related documents are chunked and embedded
- **Vector Storage**: ChromaDB stores embeddings for fast similarity search
- **Semantic Retrieval**: User queries are matched against the knowledge base
- **Context Augmentation**: Retrieved chunks enhance LLM responses with accurate information

### Intent Classification
- **Multi-layer Detection**: Greeting, career-related, and rejection filters
- **Feature Mapping**: Automatic detection of user intent to suggest platform features
- **Language Detection**: Automatic Hindi/English/Hinglish identification

### Backward Planning Algorithm
- **Goal Decomposition**: Breaks down career goals into achievable milestones
- **Timeline Generation**: Creates realistic timelines based on user's current status
- **Prerequisite Mapping**: Identifies required exams, degrees, and skills

### Authentication System
- **JWT-based Auth**: Secure token-based authentication
- **Password Hashing**: bcrypt encryption for passwords
- **Protected Routes**: Frontend route guards for authenticated pages

---

## 🚀 Deployment

### Docker Deployment

```bash
docker-compose up --build
```

### Production Considerations
- Use PostgreSQL instead of SQLite for scalability
- Configure proper CORS origins
- Set up HTTPS with SSL certificates
- Use production-grade ASGI server (Gunicorn with Uvicorn workers)

---

## 📄 License

This project is developed for educational purposes as part of CDAC coursework.

---

## 👨‍💻 Author

**Navanish**

---

## 🙏 Acknowledgments

- CDAC for project guidance
- OpenAI, Google, and Perplexity for AI capabilities
- Shadcn/UI for beautiful component library
- All open-source contributors whose libraries made this possible
