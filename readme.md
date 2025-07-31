# 🧠 Natural Language to SQL Execution using IBM Watsonx

This FastAPI application allows users to convert **natural language queries into optimized SQL** using IBM Watsonx Orchestrate AgenticAI, execute the queries via REST APIs, and get the results in structured and downloadable formats.

> ✅ Supports MSSQL,MySQL & PostgreSQL
> ✉️ Email result support
> 🌐 Web UI with basic and float layout
> 🔒 IBM Cloud IAM authentication

---

## 📁 Project Structure

```
your_project/
.
├── Aldextra_agent_v2
│   ├── agents
│   │   └── native
│   │       ├── Aldextra_agent_v2.yaml
│   │       ├── authentication_agent.yaml
│   │       ├── emailResultAgent.yaml
│   │       └── NLQWXO_SQL.yaml
│   └── tools
│       └── user_auth_tool
│           ├── auth_tool.py
│           └── requirements.txt
├── arch.xml
├── db
│   ├── db_schema_llm_summary.txt
│   └── db_schema.txt
├── Dockerfile
├── examples
│   └── few_shot_examples.py
├── main.py
├── prompts
│   └── system_prompt_template.py
├── readme.md
├── requirements.txt
├── services
│   └── sql_rest_executor.py
├── static
│   ├── AI-Agents.jpg.webp
│   └── chat_logo.png
├── templates
│   ├── index.html
│   └── indexv2.html
└── v4_ald_openapi.json
```

---

## 🚀 Features

* 🔁 **Natural Language → SQL → Execution → Results**
* 🧠 Integrated with **IBM Watsonx** LLM for generation
* 📩 Emailing of query result XLS
* 🗃 Uploadable DB schema (`.txt`)
* 🎨 Clean Web UI (Jinja2 templates)
* ✅ FastAPI backend with Pydantic validation
* 🤖 Configurable Watsonx Orchestrate Agents (via YAML)

---

## 🤖 Watsonx Orchestrate Integration

This REST API is integrated as a **Tool** within **Watsonx Orchestrate**, enabling orchestration agents to use this app for natural language-to-SQL generation and execution.

### 🔧 Tool Integration

* Endpoints `/generate-sql`, `/execute-sql`, `/generate-sql-execute-result`, and `/send-email` are registered as **tools**.
* The OpenAPI spec `v4_ald_openapi.json` is imported in Watsonx Orchestrate to define tool capabilities.

### 🧠 Agent Configuration

* Agent YAMLs like `nlsqlagent_2268HN.yaml` and `emailResultAgent.yaml` in `nlsql-v3agent/agents/native/` define:

  * Task grounding and tool bindings
  * Dialogue state flow and decisions
  * Access to environment variables (via context)
* Agents are grounded on uploaded schema using `/upload-schema`.

### 🗂️ Typical Agent Flow

1. **User Input**: "List all failed transactions for June."
2. **Agent Trigger**: `nlsqlagent_2268HN.yaml` fires, generates SQL.
3. **Tool Call**: Executes `/generate-sql-execute-result`.
4. **Post-Process**: Returns results, optionally triggers `/send-email` via `emailResultAgent.yaml`.

### 💡 Orchestration Benefits

* Seamless Watsonx integration with LLM & tools
* Reusable agent YAMLs for other workflows
* Task chaining (e.g. generate → execute → email)
* Context-driven invocation and control

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/your-repo-name.git
cd your-repo-name
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
wx_api_key=YOUR_IBM_API_KEY
wx_service_url=YOUR_MODEL_INFERENCE_URL
wx_project_id=YOUR_WX_PROJECT_ID
wx_model_id=google/flan-ul2 # Or any other model
wx_model_param_max_tokens=300
DB_ENGINE=mysql
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

> ✅ Recommended Python version: `>=3.9`

### 4. Run the App

```bash
uvicorn main:app --reload
```

Access: [http://localhost:8000](http://localhost:8000)

---

## 🧪 API Endpoints

### 🔼 Upload Schema

`POST /upload-schema`

Upload `.txt` schema file used for query generation.

---

### 🧠 Generate SQL Only

`POST /generate-sql`

```json
{
  "user_query": "List top 5 customers by purchase"
}
```

Returns:

```json
{
  "sql": "SELECT * FROM ..."
}
```

---

### ⚡ Generate SQL and Execute

`POST /generate-sql-execute-result`

Returns both the SQL and result (with XLS & HTML).

---

### 📨 Send Result via Email

`POST /send-email`

```json
{
  "email": "your@email.com"
}
```

---

### ❌ Discard Result File

`POST /no-send-email`

---

### 📄 Execute Given SQL

`POST /execute-sql`

```json
{
  "sql": "SELECT * FROM customers LIMIT 5"
}
```

---

## 🖥 UI Access

* Basic: `GET /`
* Float layout: `GET /v2`

---

## 💪 Docker (Optional)

```bash
docker build -t nlsql-watsonx .
docker run -p 8000:8000 --env-file .env nlsql-watsonx
```

---

## 📚 References

* [IBM Watsonx](https://www.ibm.com/watsonx)
* [FastAPI Documentation](https://fastapi.tiangolo.com/)
* [Pydantic Models](https://docs.pydantic.dev/)
* [Uvicorn ASGI Server](https://www.uvicorn.org/)

---

## 🧑‍💻 Author

Developed by [Shan S](https://github.com/shancs09),[Muralidhar](https://github.com/muralidharchavan)

---

## 📝 License

This project is licensed under the MIT License. See `LICENSE` for details.
