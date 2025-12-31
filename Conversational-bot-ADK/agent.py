"""
ADK Agent for Issue Management
Built on top of submit_issue backend tool
"""

from __future__ import annotations

import os
from vertexai.preview.generative_models import (
    GenerativeModel,
    Tool,
    ToolConfig,
)

# -------------------------------------------------
# Environment
# -------------------------------------------------
PROJECT_ID = os.getenv(
    "GOOGLE_CLOUD_PROJECT", "platform-support-analyst-57565"
)
LOCATION = os.getenv("GCP_LOCATION", "us-central1")

MODEL_NAME = "gemini-2.5-pro"

OPENAPI_PATH = "issue_management_openapi.yaml"


# -------------------------------------------------
# Tool Registration (OpenAPI → Tool)
# -------------------------------------------------
issue_tool = Tool.from_openapi(
    openapi_path=OPENAPI_PATH
)


# -------------------------------------------------
# Agent Definition
# -------------------------------------------------
agent = GenerativeModel(
    model_name=MODEL_NAME,
    tools=[issue_tool],
    tool_config=ToolConfig(
        function_calling_config=ToolConfig.FunctionCallingConfig(
            mode="AUTO"
        )
    ),
    system_instruction="""
You are an IT Support Agent.

Responsibilities:
- If a user reports a problem, ALWAYS create a support ticket.
- Infer priority:
    * P1 → system down / login blocked
    * P2 → major functionality broken
    * P3 → general issues
    * P4 → requests / low urgency
- After creating a ticket:
    - Confirm the issue_id
    - Summarize next steps
- Never ask the user to manually create a ticket.
"""
)


# -------------------------------------------------
# Runtime Example
# -------------------------------------------------
def run_agent(user_message: str):
    response = agent.generate_content(user_message)

    print("\n=== AGENT RESPONSE ===")
    print(response.text)

    # Debug: tool calls (important during dev)
    if response.candidates:
        for part in response.candidates[0].content.parts:
            if part.function_call:
                print("\n=== TOOL CALLED ===")
                print(part.function_call.name)
                print(part.function_call.args)


if __name__ == "__main__":
    run_agent(
        "I am unable to log in to the workflow tool since morning"
    )
