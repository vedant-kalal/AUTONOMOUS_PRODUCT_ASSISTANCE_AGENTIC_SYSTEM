
# 🤖 Autonomous Product Assistance Agentic System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)
![Groq](https://img.shields.io/badge/LLM-Llama3.3-purple)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue)

A powerful, autonomous AI agent designed to act as an intelligent shopping assistant. It leverages a **multi-agent architecture** to understand user intent, search for products (via Database or Web), refine queries, and provide detailed, context-aware recommendations.

## 🌟 Key Features

*   **🧠 Multi-Agent Orchestration**: Built with **LangGraph**, coordinating specialized agents (Decider, Supervisor, Info Collector, etc.).
*   **💾 Persistent Memory**: Uses **PostgreSQL** to store Short-Term Memory (STM) and Long-Term Memory (LTM). It "remembers" your preferences and past searches (e.g., "What was the previous shoe I looked at?").
*   **⚡ High-Speed Inference**: Powered by **Groq API** running **Llama-3.3-70b** for near-instant responses.
*   **🌐 Real-Time Web Search**: Integrated with **Google Serper** to fetch live product data, pricing, and availability when the internal database falls short.
*   **🛡️ Robust Safety & Stability**: Includes advanced error handling, "Safety Fallback" for explicit content, and JSON validation to prevent crashes.
*   **🎨 Modern UI**: A sleek, dark-themed **Streamlit** interface with real-time token streaming, formatted Q&A tables, and interaction history.

---

## 📂 Project Structure

```bash
Autonomous-Product-Assistance-Agentic-System/
├── app/
│   ├── agents/
│   │   ├── nodes/              # Agent logic (Decider, Conversational, etc.)
│   │   └── workflow/           # LangGraph workflow definition
│   ├── core/
│   │   ├── config/             # Configuration (LLM, Settings)
│   │   ├── logging/            # Centralized logging system
│   │   └── prompt/             # Prompts for all agents
│   ├── memory/                 # Memory store logic (PostgreSQL)
│   ├── schemas/                # Pydantic models for structured output
│   └── tools/                  # Search & filtering tools
├── app_backend/                # Backend utilities (Thread Management)
├── logs/                       # Structured logs (App, Memory, Workflow)
├── streamlit_app.py            # Main Streamlit UI application
├── docker-compose.yml          # PostgreSQL setup
├── requirements.txt            # Python dependencies
└── .env                        # Environment variables
```

---

## 🚀 Getting Started

### Prerequisites

*   Python 3.10+
*   PostgreSQL (Local or Docker)
*   API Keys: Groq, Serper (optional for Google Search)

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/vedant-kalal/Autonomous-Product-Assistance-Agentic-System.git
    cd Autonomous-Product-Assistance-Agentic-System
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup Environment Variables**
    Create a `.env` file in the root directory:
    ```env
    GROQ_API_KEY=gsk_...
    SERPER_API_KEY=...    # Optional: For Google Search
    DATABASE_URL=postgresql://user:password@localhost:5432/chatbot_memory
    ```

4.  **Run PostgreSQL**
    You can use the included `docker-compose.yml` to start a local DB:
    ```bash
    docker-compose up -d
    ```

### Running the App

```bash
streamlit run streamlit_app.py
```
The application will open in your browser at `http://localhost:8501`.

---

## 🛠️ Architecture

The system follows a cyclic graph workflow:

1.  **Decider**: Routes inputs to "Conversational" (chit-chat) or "Agentic" (product search) modes.
2.  **Intent Analyzer**: Extracts product type and constraints from the query.
3.  **Supervisor**: Orchestrates the flow - determining if more info is needed or if validation is required.
4.  **Info Collector**: Asks clarifying questions if the query is vague.
5.  **Query Refinement**: Optimizes the search query for search engines.
6.  **Data Retrieval**: Fetches data from the Web or Internal DB.
7.  **Response Generator**: Synthesizes the final answer and recommendations.
8.  **Memory Store**: Persists the interaction for future context.

---

## 👨‍💻 Author

**Vedant Kalal**  
*Full Stack GenAI Engineer*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/vedantkalal)

---

*Built with ❤️ using LangGraph & Streamlit.*
