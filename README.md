# MCP Couchbase Agent

An MCP based database agent using Couchbase, Amazon Bedrock ( nova ) and langgraph.

The agent generates SQL queries via tool calling, then executes them through an MCP server, and returns results from the couchbase `travel-sample` bucket (`inventory` scope)

---

## Setup

### 1. Start Couchbase (Docker Compose)

```bash
docker compose up -d
```

Open:

http://127.0.0.1:8091

- Complete cluster setup
- Install `travel-sample` bucket

---

### 2. Install dependencies

```bash
uv sync
```

---

### 3. Create `.env` ( use the .env.example for ref)

---

### 4. Run the agent

```bash
uv run main.py
```

---

## Example Queries

- find 5 hotels in France
- count routes from SFO
- which country has the most hotels?

---

> note : bedrock model access must be enabled in your aws account for nova in the selected region.
