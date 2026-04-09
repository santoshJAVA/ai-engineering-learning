# From Traditional SWE to AI Engineering 🚀

This repository contains the code from my weekend deep-dive into AI Engineering.

I’ve been a full-stack developer (Ruby on Rails, JS, React) for 10 years. For a long time, the AI space felt overwhelming. I assumed building with AI meant needing a PhD in machine learning or writing massive, complex prompts.

I was wrong. If you know how to build web apps, manage state, and call APIs, you already have 90% of the skills needed to build AI agents. This repo documents my "Aha!" moments—going from a basic API call to a multi-agent state machine.

## 📖 Read the full story here:
https://medium.com/@santoshsharma8150/my-aha-moment-with-ai-as-a-10-year-traditional-swe-9669460437a2

## 🛠 Tech Stack Used
- Python (The undisputed king of the AI ecosystem right now)
- OpenAI API (gpt-4o-mini is cheap and incredibly fast for testing)
- Pydantic (For strict type-checking and structured JSON outputs)
- ChromaDB (Local, open-source Vector Database for RAG)
- LangGraph (For managing Agent state machines)

## ⚙️ How to Run This Locally
1. Clone the repo
```bash
git clone https://github.com/santoshJAVA/ai-engineering-learning.git
cd ai-engineering-learning
```
2. Install dependencies
```bash
pip install -r requirements.txt
```
3. Set up your API Key
Create a file named `.env` in the root folder and add your OpenAI key:
```plaintext
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## 🗺 The Learning Path (The Scripts)
I broke this down into 4 core concepts. Run the scripts in this order:
### 1. Structured Outputs (`extractor.py` & `robust_extractor.py`)
**The Epiphany:** AI isn't just a chatbot. It's a "fuzzy function".
By using Pydantic, I learned how to force the LLM to return strict, perfectly formatted JSON. The `robust_extractor.py` script also adds tenacity for exponential backoff (retry logic) because APIs are inherently flaky.
```bash
python robust_extractor.py
```
### 2. RAG / Vector Databases (`rag_basics.py` & `full_rag_pipeline.py`)
**The Epiphany:** Hallucinations happen because of missing context. Memory is just a database lookup.
These scripts spin up a local ChromaDB instance, turn dummy pricing rules into mathematical vectors (embeddings), and perform a semantic search to inject private context into the LLM's prompt.
```bash
python full_rag_pipeline.py
```
### 3. Tool Calling (`agent.py`)
**The Epiphany:** LLMs can actually do things.
This script gives the OpenAI model the JSON schema for a local Python function (`create_linear_ticket`). The AI realizes it needs to use the tool, pauses text generation, passes the JSON arguments to Python, and waits for the execution result.
```bash
python agent.py
```
### 4. Multi-Agent State Machines (`multi_agent.py`)
**The Epiphany:** Complex AI isn't a giant prompt. It's a state machine.
Using LangGraph, I built a Researcher node and a Writer node. They pass a shared State dictionary back and forth. If you know Redux or finite state machines, this will immediately make sense to you.
```bash
python multi_agent.py
```
## What's Next?
I'm using my protected morning hours to combine these concepts into a functional Micro-SaaS. Follow my Twitter to watch the build-in-public journey!
