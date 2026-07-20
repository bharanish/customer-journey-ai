# Customer Journey AI Analyst — Interview Q&A

This document is designed for interview preparation. It covers common questions about the project, architecture, implementation choices, and troubleshooting.

## 1. What is this project?

**Answer:**
Customer Journey AI Analyst is a hybrid analytics agent that accepts natural language questions, converts them into SQL queries or knowledge lookup requests, executes those queries against a customer journey dataset, and returns results along with business insights and recommendations.

It also supports Retrieval-Augmented Generation (RAG) for glossary and business definition questions by searching a semantic vector store built from text documents.

## 2. What problems does this project solve?

**Answer:**
- Makes business analytics accessible through natural language.
- Avoids manual SQL writing for non-technical users.
- Provides business insights and recommendations automatically.
- Uses a safe prompt-based SQL generation flow to reduce hallucination or dangerous queries.
- Uses RAG for domain knowledge questions not covered by the dataset.

## 3. What is the high-level architecture?

**Answer:**
The flow is:

1. User submits a question through the Streamlit frontend.
2. Frontend sends the question to the FastAPI backend endpoint `/chat`.
3. Backend decides whether the question is a glossary/definition request (RAG), an analytics request, or a general chat request.
4. For RAG, the backend retrieves relevant documents from a FAISS vector store and prompts the LLM with that context.
5. For analytics, the backend uses a LangGraph workflow to generate SQL, validate it, execute it against PostgreSQL, and generate visualization, insight, and recommendations.
6. For general chat, the backend directly returns the LLM response.

## 4. What are the main components?

**Answer:**
- `frontend/app.py`: Streamlit UI and request handling.
- `backend/main.py`: FastAPI router and branching logic.
- `backend/config.py`: loads OpenAI API keys from `.env`.
- `backend/database.py`: SQLAlchemy database engine creation.
- `backend/load_data.py`: loads CSV data into PostgreSQL.
- `backend/agents/`: contains LLM agents for SQL generation, chat, insight, recommendations, RAG, validation, and visualization.
- `backend/workflows/customer_journey_graph.py`: defines the analytics workflow with LangGraph.
- `backend/rag/build_vector_store.py`: builds the FAISS vector store from text files.
- `vector_store/`: stores the local FAISS indexes.

## 5. How does the backend decide between RAG and analytics?

**Answer:**
The backend first calls `agents/rag_router.py` which has `is_business_definition(question)`. If it returns `YES`, the request goes to the RAG branch.

If it returns `NO`, the backend calls `agents/router_agent.py` to classify the question. If the classifier detects analytics keywords, it goes to the analytics workflow; otherwise it falls back to general chat.

## 6. How does RAG work in this project?

**Answer:**
- The RAG builder loads all `.txt` files from `data/`.
- It chunks the content and generates embeddings using `OpenAIEmbeddings`.
- These embeddings are stored in a FAISS vector store under `vector_store/customer_knowledge_base`.
- At query time, the backend performs `db.similarity_search(question, k=3)`.
- It concatenates the retrieved passages as context and prompts the LLM to answer using that context only.

## 7. What does the analytics workflow look like?

**Answer:**
The workflow uses `langgraph.graph.StateGraph` and includes the following nodes:

- `question_validation_agent`: validates question intent and checks dataset coverage.
- `sql_agent`: generates SQL from the question using a prompt with schema and examples.
- `sql_guard_agent`: validates SQL safety.
- `query_executor`: executes the query against PostgreSQL.
- `visualization_agent`: generates visualization metadata.
- `insight_agent`: produces business insight text.
- `recommendation_agent`: writes recommendations.

The workflow ends by returning all results to the frontend.

## 8. How is SQL generation implemented?

**Answer:**
SQL generation is implemented in `backend/agents/sql_agent.py`.

- It uses `langchain_openai.ChatOpenAI` with `gpt-4o`.
- The prompt includes a single schema, the allowed columns, business context, and strict SQL rules.
- It also includes examples and instructions to return only SQL.
- The result is cleaned to remove markdown fences and ensure only SQL remains.

## 9. How is SQL safety enforced?

**Answer:**
`backend/agents/sql_guard_agent.py` checks the generated SQL for safety. It ensures only read-only operations are allowed, flags unsafe requests, and prevents execution if the SQL is invalid or unsafe. This is a second checkpoint after the prompt-based restrictions.

## 10. How is the dataset loaded?

**Answer:**
`backend/load_data.py` reads `data/customer_journey.csv` using pandas and writes it into PostgreSQL as the `customer_journey` table. This must be executed before analytics queries can run.

## 11. How do you run the app?

**Answer:**
1. Activate the Python virtual environment:
   ```bash
   source env/bin/activate
   ```
2. Ensure `backend/.env` contains:
   ```env
   OPENAI_API_KEY="<your_openai_key>"
   API_KEY="<your_api_key>"
   DATABASE_URL="postgresql://admin:password@localhost:5432/customer_ai"
   ```
3. Start the backend with Docker Compose or directly:
   ```bash
   docker compose up -d
   ```
   or
   ```bash
   cd backend
   ../env/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
4. Load the data:
   ```bash
   docker compose exec api python /app/backend/load_data.py
   ```
5. Start frontend:
   ```bash
   cd frontend
   streamlit run app.py
   ```

## 12. What are the main endpoints and payloads?

**Answer:**
- `POST /chat`: main conversational endpoint.
- Request body:
  ```json
  {
    "question": "Show revenue by channel",
    "history": []
  }
  ```
- Response contains `type` with one of: `rag`, `analytics`, or `general`.

## 13. How are chat types handled in the frontend?

**Answer:**
The frontend inspects `data.type` and renders different UI blocks:
- `rag`: shows glossary/business knowledge answer.
- `analytics`: shows SQL, results, visualization, insight, and recommendations.
- `general`: shows a generic AI assistant response.

## 14. What was the biggest setup issue and how was it fixed?

**Answer:**
The main issue during setup was the missing `customer_journey` table in PostgreSQL. This was fixed by loading the CSV data into the DB with `backend/load_data.py` or `docker compose exec api python /app/backend/load_data.py`.

## 15. What are good interview talking points?

**Answer:**
- The app combines structured analytics and retrieval-based knowledge search.
- It separates concerns clearly between routing, workflow, SQL generation, database execution, and presentation.
- It demonstrates safe LLM usage with prompt constraints and SQL validation.
- It includes an end-to-end data loading and Docker orchestration flow.
- It has a fallback chat path for non-analytics requests.

## 16. What questions should I expect in an interview?

**Answer:**
- How does the system decide between analytics, RAG, and general chat?
- How do you prevent unsafe SQL generation?
- What is RAG and why is it used here?
- How does the LangGraph workflow work?
- How do you load and validate the dataset?
- How do you run the whole stack with Docker Compose?
- What would you improve next?
- What are the main limitations of this system?

## 17. What would you improve next?

**Answer:**
- Add a dedicated schema registry or metadata service for stronger SQL generation constraints.
- Improve the question classifier with a trained intent model instead of keyword matching.
- Add robust error handling and retry logic for database and OpenAI failures.
- Add logging and monitoring of query performance and model latency.
- Add auth and role-based access control for the API.

## 18. How do you troubleshoot common failures?

**Answer:**
- `401 Unauthorized`: check `x-api-key` and `API_KEY` in `.env`.
- `DATABASE_URL` missing: ensure `backend/.env` contains the database connection string.
- `relation "customer_journey" does not exist`: run data loader.
- Docker port conflicts: stop conflicting containers or change mapped host ports.
- `service "customer-api" is not running`: use `docker compose ps` and compose service names, not container names.

## 19. How can I summarize this project in one sentence?

**Answer:**
It is a full-stack AI analytics application that converts natural language business questions into SQL or contextual knowledge answers, executes them securely against a PostgreSQL dataset, and returns structured results with business insights and recommendations.

## 20. Common follow-up questions

## 21. 5-Minute Interview Talk

### Project Summary
- This project is a **Customer Journey Analytics platform** that makes business intelligence accessible through natural language.
- It combines **SQL generation, retrieval-augmented generation (RAG), and analytic workflows** to answer questions across marketing channels, campaigns, devices, and revenue.

### What the System Does
- Users ask questions like:
  - “Show revenue by channel”
  - “Which campaign generated the highest revenue?”
  - “What are the top performing devices?”
- The system converts business questions into **safe, schema-aware SQL**, executes them against PostgreSQL, and returns results with business insights.
- For glossary or business-definition questions, it uses **RAG** to search text documents and answer from domain knowledge.

### Architecture Highlights
- Modular backend agents in `backend/agents/`:
  - `sql_agent.py` for generating SQL
  - `rag_agent.py` / `rag_router.py` for document retrieval and knowledge answers
  - `chat_agent.py`, `insight_agent.py`, `recommendation_agent.py` for dialogue and recommendations
- `backend/workflows/customer_journey_graph.py` defines the analytics workflow.
- `backend/rag/build_vector_store.py` builds FAISS indexes from `data/` documents.

### Technical Strengths
- Uses **LangChain/OpenAI** for natural language understanding and SQL generation.
- Enforces SQL safety with:
  - strict prompt rules
  - only `SELECT` queries
  - known schema columns
  - a second SQL guard validation step
- Integrates **business context and examples** in the SQL prompt to improve accuracy.

### Why It Matters
- Turns raw customer journey data into **actionable insights**.
- Reduces the need for technical stakeholders to write SQL manually.
- Enables marketing and product teams to make decisions quickly using conversational analytics.

### Key Interview Talking Points
- The project demonstrates a **practical AI assistant** for analytics and knowledge search.
- It shows strong **separation of concerns** with routing, SQL generation, validation, execution, and presentation.
- It highlights **safe LLM usage** for query generation and real-world data reliability.
- It supports **end-to-end execution** from data loading to API and frontend.
- Next improvements could include metrics segmentation, dashboards, and enhanced intent classification.

**Q: Why use RAG instead of directly querying the database for definitions?**

**A:**
RAG is used for knowledge that lives in text documents rather than structured tables. It allows the system to answer glossary and metric definition questions from business documentation, while analytics questions use structured SQL execution.

**Q: Why is schema information included in the SQL prompt?**

**A:**
Including the schema helps the LLM generate valid SQL and prevents it from inventing columns or tables. It constrains the model to the actual dataset and reduces hallucinations.

**Q: How is this safer than a generic LLM-powered SQL generator?**

**A:**
This project uses multiple safeguards: strict prompt rules, schema-aware examples, a separate SQL guard agent, and a read-only execution path. The combination limits unsafe queries and unauthorized database modifications.

**Q: What happens if the question is ambiguous or unsupported?**

**A:**
The question validation agent marks the request as ambiguous or unsupported and returns a helpful message instead of generating SQL. This prevents incorrect queries and improves user guidance.

**Q: Why use Docker Compose for this project?**

**A:**
Docker Compose simplifies starting the full stack, including Postgres, API, Prometheus, and Grafana. It ensures consistent environment setup and avoids local dependency issues.

**Q: How does the frontend know which response type to render?**

**A:**
The backend returns `type` in the response: `rag`, `analytics`, or `general`. The frontend uses that field to render the appropriate UI and output format.

**Q: What is the role of the `history` field in the request?**

**A:**
`history` is used to preserve conversational context for analytics queries. It is included in the SQL generation prompt so the system can generate queries that respect the conversation flow.

**Q: What would you say is the main limitation of this implementation?**

**A:**
The current router is keyword-based, which can misclassify questions. A better solution would use a fine-tuned intent classification model or a more robust natural language understanding layer.

## 21. Why multi-agent instead of a single agent?

**A:**
A multi-agent design separates responsibilities and improves reliability. In this project, each agent handles a specific job—question validation, SQL generation, SQL safety, query execution, insight generation, recommendation generation, and RAG retrieval. This makes the system easier to debug, extend, and test, and it prevents a single model prompt from becoming too complex or prone to errors.

## 22. Why FAISS?

**A:**
FAISS is a high-performance library for vector similarity search. It is used here because it can efficiently search semantic embeddings at runtime, enabling fast retrieval of relevant text chunks for RAG. FAISS is a good fit for local vector stores and scales well as the knowledge base grows.

## 23. Why LangGraph instead of LangChain?

**A:**
LangGraph is used here for explicit workflow orchestration with a state graph. It makes it clear how each step connects and allows building a controlled sequence of agent nodes. While LangChain is focused on LLM chains and tools, LangGraph is a better fit when you want to define a deterministic workflow with branching, validation, and state transitions.

## 24. Why not ChromaDB or another vector database?

**A:**
FAISS was chosen because this project uses a local vector store and FAISS is a lightweight, high-performance option for local similarity search. It is easy to integrate, has good performance for small-to-medium datasets, and does not require a separate service. ChromaDB or other vector databases can also work and may be preferable in production for persistence, distributed storage, or hosted vector database features, but FAISS is suitable for a self-contained demo and local development.

## 25. Which embedding model is used and why?

**A:**
The project uses `OpenAIEmbeddings` from the OpenAI integration. This was chosen because it provides high-quality semantic embeddings that work well for retrieving business glossary and KPI-related text. Using OpenAI embeddings keeps the retrieval pipeline simple and consistent with the rest of the OpenAI-based stack.

## 26. Have you experimented with different embedding or LLM models?

**A:**
The current implementation uses OpenAI's embeddings and `gpt-4o` for LLM calls. In a production-ready design, it would be useful to experiment with different embedding models (for example OpenAI text-embedding-3 or newer embedding families) and different LLMs (`gpt-4o-mini`, `gpt-4o`, or other cost-performance variants). The project is structured so the model selection can be changed in `backend/rag/build_vector_store.py`, `backend/agents/rag_agent.py`, and `backend/agents/sql_agent.py`.

## 27. How do you evaluate your system?

**A:**
Evaluation should cover correctness, safety, and performance. For correctness, compare generated SQL and query results against a benchmark set of analytics questions and expected outputs. For safety, test unsupported or malicious queries and ensure the system either blocks them or returns a safe response. For performance, measure latency and success rate for analytics, RAG, and general chat requests. A strong evaluation also includes end-to-end testing from the frontend to the backend and monitoring API responses for expected types (`rag`, `analytics`, `general`).

## 28. How would you deploy this project in production?

**A:**
The safest production deployment would use container orchestration, such as Docker Compose for development and Kubernetes for production. The backend should run in a container with environment variables managed securely for `OPENAI_API_KEY`, `API_KEY`, and `DATABASE_URL`. PostgreSQL should be deployed as a managed service or dedicated database instance, while the FAISS vectors can be stored on persistent volumes. A production deployment should also use HTTPS, a reverse proxy, monitoring, logging, and autoscaling.

## 29. What deployment challenges do you expect?

**A:**
- Securely managing API keys and database credentials.
- Ensuring the RAG index is rebuilt when source documents change.
- Handling model latency and request timeouts.
- Scaling the backend safely while keeping SQL execution performance predictable.
- Managing container networking and port conflicts.

## 30. How would you make this deployable on a cloud platform?

**A:**
For cloud deployment, separate each service into its own container or managed service:
- Backend/API in a container on ECS/EKS/GKE or App Service.
- PostgreSQL as a managed cloud database (RDS, Cloud SQL, Azure Database).
- Vector store on a persistent volume or a managed vector DB.
- Optional Prometheus/Grafana for monitoring in the same cluster.

Use a CI/CD pipeline to build the container image, run tests, and deploy new versions. Use environment-specific configuration for secrets and endpoints.

## 31. Can this project be extended to multiple tables, and what challenges would that bring?

**A:**
Yes, this project can be extended to multiple tables, but it introduces complexity in several areas:
- Schema management: the SQL prompt must describe multiple tables, their relationships, and join keys.
- Query generation: the model must decide when to join tables and which table contains the requested fields.
- Safety: multi-table queries are harder to validate and more likely to produce incorrect joins or aggregates.
- Database structure: you may also need foreign key relationships and additional indexing for performance.
- Prompt complexity: the prompt will grow larger, so you need careful design to keep the prompt readable and effective.

The main challenges are ensuring correct join logic, avoiding ambiguous field references, and keeping the SQL generator from inventing invalid table relationships. A more robust parser or schema-aware intent model would help manage these challenges.
