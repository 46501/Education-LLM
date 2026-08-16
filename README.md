# Education LLM

A personalized AI-powered education platform designed to adapt to each student's unique learning journey. Education LLM combines the power of Large Language Models with proven educational methodologies like spaced repetition, memory engines, and dynamic study planning to create a tailored, effective learning experience.

## Features

- **AI Tutor:** An intelligent, context-aware conversational agent that understands a student's learning history and current struggles.
- **Retrieval-Augmented Generation (RAG):** Upload educational materials (PDFs, docs) to ground the AI's knowledge, ensuring factual, relevant instruction.
- **Personalized Learning:** Continuous monitoring of a student's progress and misconceptions to dynamically adapt the curriculum.
- **Quiz Generation:** Automatically generate targeted quizzes based on uploaded materials and topics the student needs to improve.
- **Answer Evaluation:** AI-driven grading of free-text and multiple-choice answers, providing constructive feedback.
- **Adaptive Difficulty:** Automatically scale question complexity up or down based on the student's mastery score.
- **Learning Memory:** Extract long-term insights (strengths, weaknesses, misconceptions) from student interactions and quizzes.
- **Spaced Repetition:** Scientifically backed scheduling algorithm for reviewing topics to maximize retention and prevent forgetting curves.
- **AI Study Planner:** Automatically construct time-boxed daily study plans based on the user's goals, available time, and priority areas.
- **Progress Analytics:** Comprehensive dashboards tracking streaks, mastery levels, and study session statistics.

## Architecture

```mermaid
graph TD
    A[Next.js Frontend] --> B[FastAPI Backend]
    B --> C[AI Orchestrator]
    C --> D[RAG / Learning Engine / Personalization]
    D --> E[(PostgreSQL + pgvector)]
    D --> F[LLM Provider (LiteLLM / OpenAI)]
```

## Tech Stack

### Frontend
- **Next.js 16** (App Router)
- **TypeScript**
- **Tailwind CSS**

### Backend
- **FastAPI**
- **Python 3**
- **SQLAlchemy (Async)**

### Database
- **PostgreSQL**
- **pgvector** (For semantic document search and retrieval)

### AI
- **LiteLLM** (Provider agnostic LLM routing)
- **OpenAI Embeddings**
- **Retrieval-Augmented Generation (RAG)**

## Project Structure

```
Education-LLM/
├── backend/          # FastAPI application, database models, AI orchestrator
│   ├── app/
│   │   ├── api/      # REST API Endpoints
│   │   ├── core/     # Configuration and Database setup
│   │   ├── models/   # SQLAlchemy Database Models
│   │   ├── schemas/  # Pydantic validation schemas
│   │   └── services/ # Business Logic (RAG, Scoring, Spaced Repetition)
│   ├── tests/        # Pytest test suite
│   └── alembic/      # Database migrations
└── frontend/         # Next.js application
    └── src/
        └── app/      # React components and pages
```

## Setup

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Node.js 18+

### 1. Database Setup
Ensure Docker is running, then spin up the PostgreSQL database with `pgvector`:
```bash
docker-compose up -d
```

### 2. Backend Setup
Navigate to the backend directory, create a virtual environment, and install dependencies:
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Unix:
source venv/bin/activate

pip install -r requirements.txt
```

Set up your environment variables:
```bash
cp .env.example .env
```
Edit `.env` to include your LLM provider keys and ensure `DATABASE_URL` matches your local setup.

Run the database migrations:
```bash
alembic upgrade head
```

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

### 3. Frontend Setup
Navigate to the frontend directory and install dependencies:
```bash
cd frontend
npm install
```

Start the Next.js development server:
```bash
npm run dev
```

## Usage

1. **Register/Login:** Create a new student account to isolate your learning data.
2. **Upload Materials:** Navigate to the documents section and upload course materials (PDF, TXT).
3. **Chat with AI Tutor:** Ask questions about the uploaded materials. The AI will retrieve relevant context using RAG.
4. **Take Quizzes:** Generate custom quizzes on specific topics. The platform will evaluate your answers.
5. **Review Analytics:** Check your mastery scores, current streaks, and identified learning misconceptions.
6. **Follow Study Plans:** Request a daily study plan, and the AI will prioritize topics based on your spaced repetition schedule and current weaknesses.

## Testing

### Backend Tests
Run the full pytest suite for the backend services:
```bash
cd backend
pytest
```

### End-to-End Tests
Execute the E2E verification script to test the complete user flow against the running server:
```bash
python e2e_test.py
```

### Frontend Checks
Run the TypeScript compiler and linter:
```bash
cd frontend
npm run build
```

## Future Roadmap

- **Phase 5 (Upcoming):** Gamification, advanced UI polish, and social learning features.
