"""CLI entry point for testing the AcmeCloud support agent without Streamlit."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_framework import Content, WorkflowEvent
from agent_framework.orchestrations import HandoffAgentUserRequest

from src.config import load_config
from src.observability.setup import configure_observability
from src.orchestration.workflow import build_support_workflow


async def main():
    config = load_config()
    configure_observability(config)
    workflow = build_support_workflow(config)

    print("=" * 60)
    print("  AcmeCloud Customer Support Agent (CLI)")
    print("  Type 'quit' to exit")
    print("=" * 60)

    pending_requests: list[WorkflowEvent] = []
    first_message = True

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if not user_input:
            continue

        # Collect events
        events: list[WorkflowEvent] = []

        user_requests = [
            r for r in pending_requests
            if isinstance(r.data, HandoffAgentUserRequest)
        ]

        if user_requests:
            responses = {
                req.request_id: HandoffAgentUserRequest.create_response(user_input)
                for req in user_requests
            }
            async for event in workflow.run(responses=responses, stream=True):
                events.append(event)
            pending_requests = [r for r in pending_requests if r not in user_requests]
        else:
            async for event in workflow.run(user_input, stream=True):
                events.append(event)

        # Process events
        for event in events:
            if event.type == "request_info":
                if isinstance(event.data, HandoffAgentUserRequest):
                    for msg in event.data.agent_response.messages:
                        if msg.text and msg.text.strip():
                            author = msg.author_name or event.executor_id
                            print(f"\n[{author}]: {msg.text}")
                    pending_requests.append(event)

                elif isinstance(event.data, Content) and event.data.type == "function_approval_request":
                    func_call = event.data.function_call
                    args = func_call.parse_arguments() or {}
                    print(f"\n⚠️  APPROVAL REQUIRED: {func_call.name}")
                    print(f"   Arguments: {args}")
                    approval = input("   Approve? (y/n): ").strip().lower()
                    approved = approval == "y"
                    response = event.data.to_function_approval_response(approved=approved)
                    approval_events: list[WorkflowEvent] = []
                    async for evt in workflow.run(responses={event.request_id: response}, stream=True):
                        approval_events.append(evt)
                    events.extend(approval_events)

            elif event.type == "output":
                if hasattr(event, "data") and event.data:
                    if isinstance(event.data, list):
                        for msg in event.data:
                            if hasattr(msg, "text") and msg.text and msg.text.strip():
                                author = getattr(msg, "author_name", "Agent") or "Agent"
                                print(f"\n[{author}]: {msg.text}")

            elif event.type == "agent_response_update":
                if hasattr(event, "update") and event.update:
                    if hasattr(event.update, "text") and event.update.text:
                        author = getattr(event, "executor_id", "Agent") or "Agent"
                        print(f"\n[{author}]: {event.update.text}")


if __name__ == "__main__":
    asyncio.run(main())
