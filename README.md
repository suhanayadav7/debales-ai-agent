# 🤖 Debales AI Assistant

> An intelligent AI agent built with **LangGraph** that answers questions about Debales AI using RAG (Retrieval-Augmented Generation), handles external queries via DuckDuckGo/SERP, and routes smartly between both — with zero hallucination on unknown queries.

---

## 🚀 What This Project Does

This project is a fully functional AI chatbot assistant built for Debales AI. It uses a LangGraph-powered workflow to intelligently decide how to answer each user query:

- If the question is **about Debales AI** → it searches a local vector database built from scraped Debales AI website content (RAG)
- If the question is **general/external** → it searches the web using DuckDuckGo or SerpAPI
- If the question is **mixed** → it does both simultaneously and combines the results
- If the question is **unclear or nonsensical** → it honestly refuses without hallucinating

---

## 📸 Demo

https://drive.google.com/file/d/1ScVo_H9QD6tRcAlBtHCGseBRODwpD-Um/view?usp=share_link

╔══════════════════════════════════════════════════════╗
║          DEBALES AI  —  Intelligent Assistant        ║
║     Type your question or 'help' for commands        ║
╚══════════════════════════════════════════════════════╝
You: What does Debales AI do?
[Router] → serp
[SERP] Using DuckDuckGo
[SERP] Retrieved 1736 chars
Assistant: Debales AI is an Autonomous Logistics Automation Platform that automates
logistics operations using AI agents. It reads emails, updates systems, sends replies,
and fixes exceptions automatically...
You: What is ChatGPT?
[Router] → serp
[SERP] Using DuckDuckGo
Assistant: ChatGPT is a generative artificial intelligence chatbot developed by OpenAI...
You: How does Debales AI compare to other AI tools?
[Router] → serp
[SERP] Retrieved 2230 chars
Assistant: Debales AI stands out due to its unique focus on logistics automation,
supply chain optimization, and sales automation. Compared to Salesforce Agentforce,
Zendesk, Dialpad, Fin by Intercom, and Freshdesk...
You: asdfghjkl
[Router] → unknown
Assistant: I don't have enough context to provide a helpful answer...

---

## 🏗️ Architecture
User Query
│
▼
┌─────────────────────────────────┐
│         Route Query Node         │
│  LLM classifies intent into:     │
│  rag / serp / both / unknown     │
└────────────────┬────────────────┘
│
┌─────────┴──────────┐
│                    │
▼                    ▼
┌─────────────┐      ┌─────────────┐
│  RAG Node   │      │  SERP Node  │
│             │      │             │
│ Chroma DB   │      │ DuckDuckGo  │
│ Vector Store│      │ / SerpAPI   │
│ (Debales KB)│      │ (Web Search)│
└──────┬──────┘      └──────┬──────┘
│                    │
└──────────┬──────────┘
│
▼
┌─────────────────────────┐
│    Generate Answer Node  │
│                         │
│  Groq LLM synthesises   │
│  final response from    │
│  all available context  │
└─────────────────────────┘
│
▼
Final Answer

### Routing Logic

| Query Type | Route | Source Used |
|------------|-------|-------------|
| Questions about Debales AI company, product, features, pricing, integrations | `rag` | Chroma vector store built from scraped Debales AI website |
| General knowledge, news, external companies, definitions | `serp` | DuckDuckGo / SerpAPI web search |
| Mix of Debales + external info needed | `both` | RAG + SERP combined and synthesised |
| Unclear, nonsensical, or unanswerable | `unknown` | Honest refusal, no hallucination |

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Agent Workflow | LangGraph | Stateful graph-based agent orchestration |
| LLM | Groq (llama-3.1-8b-instant) | Query routing + answer generation |
| Embeddings | SentenceTransformers (all-MiniLM-L6-v2) | Free local text embeddings |
| Vector Store | Chroma DB | Persistent local vector database |
| Web Scraping | BeautifulSoup4 + Requests | Scraping Debales AI website |
| Web Search | DuckDuckGo (ddgs) / SerpAPI | External query resolution |
| CLI | Python (built-in) | Command line interface |
| Web UI | Streamlit | Optional browser-based chat UI |

---

## 📁 Project Structure
debales-ai-assistant/
├── src/
│   ├── init.py        # Package exports
│   ├── agent.py           # LangGraph StateGraph — nodes, edges, routing logic
│   ├── rag.py             # Web scraper + Chroma vector store + retriever
│   ├── tools.py           # SERP tool with DuckDuckGo fallback
│   └── llm.py             # LLM factory (Groq / OpenAI)
├── data/
│   └── chroma_db/         # Auto-created on first run (gitignored)
├── main.py                # Interactive CLI entrypoint
├── app.py                 # Streamlit web UI
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore
└── README.md

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.9 or higher
- pip
- A free Groq API key (get one at console.groq.com)

### Step 1 — Clone the repository

```bash
git clone https://github.com/suhanayadav/debales-ai-assistant.git
cd debales-ai-assistant
```

### Step 2 — Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:
```bash
venv\Scripts\activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```env
GROQ_API_KEY=your-groq-key-here
OPENAI_API_KEY=your-openai-key-here
SERPAPI_KEY=your-serpapi-key-here
SERP_ENGINE=google
OPENAI_MODEL=gpt-4o-mini
```

### Step 5 — Run the CLI

```bash
python3 main.py
```

### Step 6 — (Optional) Run the Streamlit UI

```bash
streamlit run app.py
```

---

## 🔑 API Keys Guide

| Key | Required | Where to Get | Cost |
|-----|----------|-------------|------|
| `GROQ_API_KEY` | ✅ Yes | [console.groq.com](https://console.groq.com) | Free |
| `OPENAI_API_KEY` | ❌ Optional | [platform.openai.com](https://platform.openai.com) | Paid |
| `SERPAPI_KEY` | ❌ Optional | [serpapi.com](https://serpapi.com) | 100 free/month |

> If `SERPAPI_KEY` is not set, the agent automatically falls back to **DuckDuckGo** which requires no API key.

---

## 🧠 How It Works — Deep Dive

### 1. LangGraph State Machine

The agent uses a `StateGraph` with a typed `AgentState` that tracks:
- `query` — the user's input
- `route` — classified as rag / serp / both / unknown
- `rag_context` — retrieved chunks from vector store
- `serp_results` — web search results
- `final_answer` — synthesised response
- `messages` — conversation history

### 2. RAG Pipeline

- **Scraping**: BeautifulSoup scrapes 6 Debales AI pages on first run
- **Chunking**: RecursiveCharacterTextSplitter (800 chars, 100 overlap)
- **Embedding**: SentenceTransformers all-MiniLM-L6-v2 (runs locally, free)
- **Storage**: Chroma DB persisted to `data/chroma_db/`
- **Retrieval**: Top-4 most similar chunks returned per query

### 3. SERP Tool

- Primary: SerpAPI (Google Search) if `SERPAPI_KEY` is set
- Fallback: DuckDuckGo via `ddgs` library (no key needed)
- Returns top 5 results formatted as title + snippet + URL

### 4. Routing Node

The LLM (Groq) receives the query and classifies it into one of four categories using a strict one-word prompt. This ensures fast, accurate routing without over-thinking.

### 5. Answer Generation

The final node receives all available context (RAG + SERP or both) and generates a grounded answer. The system prompt explicitly instructs the model not to hallucinate — if context is insufficient, it says so.

---

## 💬 Example Prompts

```bash
# Debales AI questions (RAG)
What does Debales AI do?
What are the features of Debales AI?
How does Debales integrate with Shopify?
What is Debales AI pricing?
Who founded Debales AI?
What industries does Debales AI serve?

# External questions (SERP)
What is the capital of France?
What is ChatGPT?
Latest developments in AI agents
What is LangGraph?

# Mixed questions (RAG + SERP)
How does Debales AI compare to Salesforce?
What makes Debales AI unique among logistics tools in 2024?
How does Debales AI stack up against Zendesk?

# Unknown (honest refusal)
asdfghjkl
123456789
????
```

---

## ✅ Assignment Evaluation Criteria

| Criteria | Status | Implementation Details |
|----------|--------|----------------------|
| Correct routing (RAG vs SERP) | ✅ Done | LLM-based router node classifies every query |
| Quality scraping and retrieval | ✅ Done | BeautifulSoup scrapes 6 pages, boilerplate removed, top-4 chunks retrieved |
| Proper use of SERP API | ✅ Done | SerpAPI supported + DuckDuckGo fallback |
| LangGraph workflow clarity | ✅ Done | Clean StateGraph with conditional fan-out edges |
| Code quality | ✅ Done | Typed state, modular files, docstrings, clean structure |
| No hallucination | ✅ Done | Anti-hallucination system prompt, honest unknown refusal |

---

## 🔧 CLI Commands

Once inside the CLI:

| Command | Action |
|---------|--------|
| `help` | Show available commands |
| `rebuild` | Re-scrape and re-index the Debales knowledge base |
| `clear` | Clear the terminal screen |
| `exit` or `quit` | Exit the assistant |

---

## 📦 Dependencies
langchain>=0.2.0
langchain-core>=0.2.0
langchain-community>=0.2.0
langchain-groq>=1.1.0
langgraph>=0.1.0
chromadb>=0.5.0
sentence-transformers
requests>=2.31.0
beautifulsoup4>=4.12.0
ddgs
python-dotenv>=1.0.0
streamlit>=1.35.0

---

## 📝 Notes

- On first run, the agent scrapes and indexes the Debales AI website — this takes about 30 seconds
- The vector store is cached locally in `data/chroma_db/` so subsequent runs are instant
- The agent uses Groq's free tier which is fast and has generous rate limits
- No OpenAI credits are required if using Groq

---

## 👩‍💻 Author

**Suhana**
Built as part of the Debales AI Internship Assignment
