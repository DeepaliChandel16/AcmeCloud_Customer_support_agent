import asyncio
import logging
import sys
import uuid
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent_framework import Content, WorkflowEvent
from agent_framework.orchestrations import HandoffAgentUserRequest

from src.config import load_config
from src.observability.setup import configure_observability
from src.orchestration.workflow import build_support_workflow
from src.tools.memory import get_conversation_store

logger = logging.getLogger("acmecloud.ui")

st.set_page_config(page_title="AcmeCloud Support", page_icon="☁️", layout="wide")

# --- One-time init ---
if "config" not in st.session_state:
    st.session_state.config = load_config()
    configure_observability(st.session_state.config)

if "store" not in st.session_state:
    store_cfg = st.session_state.config.integrations.get("conversation_store", {})
    st.session_state.store = get_conversation_store(store_cfg)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_requests" not in st.session_state:
    st.session_state.pending_requests = []

if "escalated" not in st.session_state:
    st.session_state.escalated = False

store = st.session_state.store


def new_session():
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.pending_requests = []
    st.session_state.escalated = False


def load_session(sid: str):
    st.session_state.session_id = sid
    history = store.get_history(sid, limit=200)
    st.session_state.messages = [
        {"role": m["role"], "content": m["content"], "agent": m.get("agent", "")}
        for m in history
    ]
    st.session_state.pending_requests = []
    st.session_state.escalated = False


def delete_session(sid: str):
    store.delete_session(sid)
    if st.session_state.session_id == sid:
        new_session()


# --- Sidebar: session list ---
with st.sidebar:
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        new_session()
        st.rerun()

    st.divider()
    st.markdown("**Chat History**")

    sessions = store.list_sessions()
    if not sessions:
        st.caption("No conversations yet.")
    else:
        for s in sessions:
            sid = s["id"]
            title = s["title"] or "New chat"
            is_active = sid == st.session_state.session_id

            col1, col2 = st.columns([5, 1])
            with col1:
                label = f"**▶ {title}**" if is_active else title
                if st.button(label, key=f"load_{sid}", use_container_width=True,
                             disabled=is_active):
                    load_session(sid)
                    st.rerun()
            with col2:
                if st.button("🗑", key=f"del_{sid}", help="Delete this chat"):
                    delete_session(sid)
                    st.rerun()

    st.divider()
    st.markdown(
        """
        **Agents:**
        📚 Knowledge · 👤 Account · 💳 Billing · 🎫 Tickets

        **Sample IDs:**
        Customers: CUST-001 to 003
        Invoices: INV-1001 to 1004
        Subscriptions: SUB-001 to 003
        """
    )


# --- Main chat area ---
st.title("☁️ AcmeCloud Customer Support")
st.caption("Powered by Microsoft Agent Framework + Ollama")


async def run_workflow_async(config, user_input: str | None = None, responses: dict | None = None):
    workflow = build_support_workflow(config)
    events = []
    if user_input:
        logger.info(">>> User message: %s", user_input)
        async for event in workflow.run(user_input, stream=True):
            logger.debug("Event: type=%s executor=%s", event.type, getattr(event, "executor_id", "?"))
            events.append(event)
    elif responses:
        logger.info(">>> Sending responses: %s", list(responses.keys()))
        async for event in workflow.run(responses=responses, stream=True):
            events.append(event)
    logger.info("<<< Workflow complete (%d events)", len(events))
    return events


def run_workflow(config, user_input: str | None = None, responses: dict | None = None):
    return asyncio.run(run_workflow_async(config, user_input=user_input, responses=responses))


def process_events(events: list[WorkflowEvent]):
    agent_messages = []
    pending = []
    seen_texts = set()
    has_request_info = any(e.type == "request_info" for e in events)

    for event in events:
        if event.type == "request_info":
            if isinstance(event.data, HandoffAgentUserRequest):
                for msg in event.data.agent_response.messages:
                    if msg.text and msg.text.strip() and msg.text not in seen_texts:
                        seen_texts.add(msg.text)
                        agent = msg.author_name or event.executor_id
                        logger.info("[%s] %s", agent, msg.text[:200])
                        agent_messages.append({"agent": agent, "text": msg.text})
                pending.append(event)
            elif isinstance(event.data, Content) and event.data.type == "function_approval_request":
                logger.info("HITL approval requested: %s", getattr(event.data, "function_call", "?"))
                pending.append(event)
        elif event.type == "output" and not has_request_info:
            if hasattr(event, "data") and event.data:
                if isinstance(event.data, list):
                    for msg in event.data:
                        if hasattr(msg, "text") and msg.text and msg.text.strip() and msg.text not in seen_texts:
                            seen_texts.add(msg.text)
                            agent = getattr(msg, "author_name", "Agent") or "Agent"
                            logger.info("[%s] %s", agent, msg.text[:200])
                            agent_messages.append({"agent": agent, "text": msg.text})
                elif hasattr(event.data, "text") and event.data.text and event.data.text not in seen_texts:
                    seen_texts.add(event.data.text)
                    logger.info("[Agent] %s", event.data.text[:200])
                    agent_messages.append({"agent": "Agent", "text": event.data.text})
    logger.info("Processed %d events -> %d messages, %d pending", len(events), len(agent_messages), len(pending))
    return agent_messages, pending


# --- Render chat history ---
for msg in st.session_state.messages:
    role = msg["role"]
    with st.chat_message(role):
        if role == "assistant" and msg.get("agent"):
            st.markdown(f"**[{msg['agent']}]** {msg['content']}")
        else:
            st.markdown(msg["content"])

# --- Escalation banner ---
if st.session_state.escalated:
    st.warning("This conversation has been escalated to a human representative.")

# --- Chat input ---
if user_input := st.chat_input("Type your message...", disabled=st.session_state.escalated):
    sid = st.session_state.session_id
    st.session_state.messages.append({"role": "user", "content": user_input, "agent": ""})
    store.save_message(sid, "user", user_input)

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Agent is thinking..."):
        config = st.session_state.config
        st.session_state.pending_requests = []
        events = run_workflow(config, user_input=user_input)
        agent_msgs, new_pending = process_events(events)

        for am in agent_msgs:
            st.session_state.messages.append({
                "role": "assistant",
                "agent": am["agent"],
                "content": am["text"],
            })
            store.save_message(sid, "assistant", am["text"], agent=am["agent"])

        st.session_state.pending_requests.extend(new_pending)

    st.rerun()
