from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.google_search_tool import GoogleSearchTool

from .inventory_tools import get_inventory_by_name


# -----------------------------
# FINAL RESPONSE TOOL (CRITICAL)
# -----------------------------
def final_response(message: str) -> str:
    """
    This tool MUST be called last.
    Whatever this returns is sent to the user.
    """
    return message


# -----------------------------
# LOGISTICS SEARCH AGENT
# -----------------------------
logistics_search_agent = LlmAgent(
    name="logistics_search_agent",
    model="gemini-2.5-flash",
    instruction="""
You are a logistics research agent.
Only perform web searches.
Do not interact with inventory or finance.
""",
    tools=[GoogleSearchTool()],
)


# -----------------------------
# LOGISTICS AGENT
# -----------------------------
logistics_agent = LlmAgent(
    name="logistics_agent",
    model="gemini-2.5-flash",
    instruction="""
You are a logistics coordinator.
Execute shipment ONLY after approval.
""",
    tools=[agent_tool.AgentTool(agent=logistics_search_agent)],
)


# -----------------------------
# INVENTORY AGENT (INTERNAL ONLY)
# -----------------------------
inventory_agent = LlmAgent(
    name="inventory_agent",
    model="gemini-2.5-flash",
    instruction="""
You are an inventory agent.

Rules (STRICT):
- ALWAYS call get_inventory_by_name.
- Return structured data ONLY to the orchestrator.
- NEVER speak to the end user.
""",
    tools=[FunctionTool(get_inventory_by_name)],
)


# -----------------------------
# FINANCE AGENT (QUANTITY ONLY)
# -----------------------------
finance_agent = LlmAgent(
    name="finance_agent",
    model="gemini-2.5-flash",
    instruction="""
Approval rules:
- If quantity < 100 units → REJECT.
- Otherwise → APPROVE.

Return ONLY a decision message.
""",
)


# -----------------------------
# ROOT ORCHESTRATOR (FIXED)
# -----------------------------
root_agent = LlmAgent(
    name="SupplyChainOrchestrator",
    model="gemini-2.5-flash",
    instruction="""
You are the root supply chain orchestrator.

ABSOLUTE RULES (NON-NEGOTIABLE):
- You MUST ALWAYS finish by calling final_response(...).
- You MUST NEVER return raw tool outputs or JSON.
- If you receive inventory data, you MUST summarize it.

AVAILABILITY HANDLING:
When inventory data is received in this form:
{
  item_name: <string>,
  quantity: <number>,
  status: <string>
}

You MUST respond ONLY as:
final_response("<quantity> units of <item_name> are available.")

FORBIDDEN:
- Returning get_inventory_by_name_response
- Returning JSON, lists, or key-value pairs
- Exposing tool or agent internals
""",
    tools=[FunctionTool(final_response)],
    sub_agents=[
        inventory_agent,
        finance_agent,
        logistics_agent,
    ],
)
