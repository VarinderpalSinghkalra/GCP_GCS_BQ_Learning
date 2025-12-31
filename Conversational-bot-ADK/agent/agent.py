"""
ADK Agent for Issue Management
Uses OpenAPI spec to call submit_issue backend
"""

from __future__ import annotations

import os
import yaml

from vertexai.preview.generative_models import (
    GenerativeModel,
    Tool,
    ToolConfig,
)

# -------------------------------------------------
# Load OpenAPI YAML manually (IMPORTANT)
# -------------------------------------------------
with open("./issue_management_openapi.yaml", "r") as f:
    openapi_spec = yaml.safe_load(f)

issue_tool = Tool.from_openapi_spec(openapi_spec)

# -------------------------------------------------
# Agent Definition
# -------------------------------------------------
agent = GenerativeModel(
    model_name="gemini-2.5-pro",
    tools=[issue_tool],
    tool_config=ToolConfig(
        function_calling_config=ToolConfig.FunctionCallingConfig(
            mode="AUTO"
        )
    ),
    system_instruction="""
You are an IT Support Agent.

Rules:
- If the user reports a problem, ALWAYS create a ticket.
- Infer priority automatically:
    P1: login blocked, system down
    P2: major functionality broken
    P3: general issue
    P4: low-priority request
- After creating the ticket:
    - Confirm the issue_id
    - Explain next steps briefly
"""
)

# -------------------------------------------------
# Run Agent
# -------------------------------------------------
def run_agent(user_message: str):
    response = agent.generate_content(user_message)

    print("\n=== AGENT RESPONSE ===")
    print(response.text)

    # Debug: show tool calls
    if response.candidates:
        for part in response.candidates[0].content.parts:
            if part.function_call:
                print("\n=== TOOL CALL DEBUG ===")
                print("Tool name :", part.function_call.name)
                print("Arguments :", part.function_call.args)


if __name__ == "__main__":
    run_agent(
        "I am unable to login to the workflow tool since morning"
    )
