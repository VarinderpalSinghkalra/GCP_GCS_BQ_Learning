from vertexai.preview.agents import Agent
from tools.issue_management_tool import (
    submit_issue_tool,
    get_issue_status_tool,
)

agent = Agent(
    name="issue-management-agent",
    description="Handles incident creation, SLA tracking, and status queries",
    model="gemini-2.5-flash",
    tools=[
        submit_issue_tool,
        get_issue_status_tool,
    ],
)
