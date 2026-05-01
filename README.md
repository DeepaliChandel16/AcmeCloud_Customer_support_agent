# ☁️ AcmeCloud Customer Support Agent

AI-powered multi-agent customer support system built with **Microsoft Agent Framework**, **Ollama**, **OpenTelemetry**, **Streamlit**, and **SQLite**.

Five specialized agents handle knowledge base queries, account operations, billing, ticket management, and intelligent triage routing — with human-in-the-loop approval gates for sensitive actions.

---

## Quick Start

**Prerequisites:** Python 3.12+, [Ollama](https://ollama.com)

```bash
# 1. Install dependencies
pip install -r requirements.txt --pre

# 2. Pull the LLM model (~2GB)
ollama pull llama3.2

# 3. Copy environment config
cp .env.example .env

# 4. Start the app
# Windows:
start.bat
# Mac/Linux:
chmod +x start.sh stop.sh
./start.sh
```

Open **http://localhost:8501** in your browser.

To also launch the DevUI debug tool (trace viewer at port 8080):
```bash
start.bat --devui       # Windows
./start.sh --devui      # Mac/Linux
```

Stop everything:
```bash
stop.bat                # Windows
./stop.sh               # Mac/Linux
```

---

## Architecture

```
Customer → Streamlit UI → Triage Agent → Specialist Agent → Tools → Response
                                ↓
                   ┌────────────┼────────────┐
                   ↓            ↓            ↓            ↓
              Knowledge    Account      Billing      Ticket
               Agent        Agent        Agent        Agent
                   ↓            ↓            ↓            ↓
              search_kb   check_status  get_invoice  create_ticket
              get_policy  verify_id     refund 🔒    update_ticket
              svc_status  reset_pw 🔒   cancel 🔒    get_ticket
```

**Orchestration:** Handoff pattern — Triage classifies and routes; specialists resolve and hand back.

**🔒 HITL:** `reset_password`, `process_refund`, and `cancel_subscription` require human approval.

---

## Agents & Tools

| Agent | Tools | Description |
|-------|-------|-------------|
| **Triage** | None (router) | Classifies intent, routes to specialist |
| **Knowledge** | `search_kb`, `get_policy`, `get_service_status` | Docs, policies, service health |
| **Account** | `check_account_status`, `verify_identity`, `get_customer_profile`, `reset_password` 🔒 | Account ops, identity verification |
| **Billing** | `get_invoice`, `get_customer_profile`, `process_refund` 🔒, `cancel_subscription` 🔒 | Invoices, refunds, cancellations |
| **Ticket** | `create_ticket`, `update_ticket`, `get_ticket` | Support ticket CRUD |

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Orchestration | Microsoft Agent Framework v1.2.2 | Multi-agent Handoff workflow |
| LLM | Ollama + llama3.2 (3B) | Local inference with tool calling |
| UI | Streamlit | Chat interface + session sidebar |
| Persistence | SQLite | Chat history (swappable to Redis) |
| Observability | OpenTelemetry | Console + OTLP trace exporters |
| Debug | Agent Framework DevUI | Trace viewer at localhost:8080 |
| Deployment | Docker Compose | App + Ollama + Aspire Dashboard |

---

## Integration Providers

Factory pattern — swap mock to real with one config change in `config/settings.yaml`:

| Domain | Active | Production Stub |
|--------|--------|----------------|
| Ticketing | Mock | Zendesk |
| Knowledge Base | Mock | SharePoint + Azure AI Search |
| CRM | Mock | Salesforce |
| Billing | Mock | Stripe |
| Account/Auth | Mock | Azure Entra ID |
| Session Store | SQLite | Redis |
| Telemetry | Mock | — |

```yaml
# config/settings.yaml
integrations:
  ticketing:   { provider: "zendesk" }      # was: "mock"
  billing:     { provider: "stripe" }       # was: "mock"
  crm:         { provider: "salesforce" }   # was: "mock"
```

---

## Observability

| Mode | Config | Description |
|------|--------|-------------|
| Console | `exporter: "console"` (default) | Traces + logs printed to terminal |
| OTLP | `exporter: "otlp"` | Sends to Aspire Dashboard / Jaeger / Azure Monitor |
| DevUI | `start.bat --devui` | Built-in trace viewer at localhost:8080 |

Traced spans: `invoke_agent`, `chat <model>`, `execute_tool`, `handoff` — each with timing and metadata.

---

## Project Structure

```
├── start.bat / start.sh          # Start app (--devui for debug UI)
├── stop.bat / stop.sh            # Stop all processes
├── devui_server.py               # DevUI debug launcher
├── config/settings.yaml          # All configuration
├── data/conversations.db         # SQLite chat history (auto-created)
├── src/
│   ├── config.py                 # YAML + env config loader
│   ├── clients.py                # PatchedOllamaChatClient
│   ├── main.py                   # CLI entry point
│   ├── agents/                   # 5 agent definitions
│   ├── tools/
│   │   ├── interfaces.py         # 7 abstract base classes
│   │   ├── registry.py           # Central ToolRegistry + _safe_call()
│   │   ├── ticketing/            # Mock + Zendesk stub
│   │   ├── knowledge_base/       # Mock + SharePoint stub
│   │   ├── crm_module/           # Mock + Salesforce stub
│   │   ├── billing_module/       # Mock + Stripe stub
│   │   ├── account_module/       # Mock + Entra ID stub
│   │   └── memory/               # SQLite + InMemory + Redis stub
│   ├── orchestration/workflow.py # HandoffBuilder wiring
│   ├── observability/setup.py    # OTel + structured logging
│   └── ui/app.py                 # Streamlit chat UI
├── docker-compose.yml            # Docker deployment
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Sample Test Data

| Type | IDs |
|------|-----|
| Customers | `CUST-001` (Alice, Pro), `CUST-002` (Bob, Enterprise), `CUST-003` (Carol, Starter) |
| Invoices | `INV-1001` to `INV-1004` |
| Subscriptions | `SUB-001` to `SUB-003` |
| Security answers | `fluffy` (CUST-001), `rover` (CUST-002), `sunshine` (CUST-003) |

---

## Docker

```bash
docker-compose up --build
# Then pull the model:
docker exec <ollama-container> ollama pull llama3.2
```

Services: App (8501), Ollama (11434), Aspire Dashboard (18888).

Set `exporter: "otlp"` in `settings.yaml` when using Docker Compose.

---

## License

Internal project — not licensed for public distribution.
