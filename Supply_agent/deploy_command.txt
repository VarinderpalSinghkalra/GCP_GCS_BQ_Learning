from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.google_search_tool import GoogleSearchTool

from .inventory_tools import get_inventory_by_name


# -----------------------------
# FINAL RESPONSE TOOL (REQUIRED)
# -----------------------------
def final_response(message: str) -> str:
    """Return the final user-facing response."""
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

Return structured availability data ONLY to the orchestrator.
Never speak to the end user.
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
Reject if quantity < 100 units.
Approve otherwise.
""",
)


# -----------------------------
# ROOT ORCHESTRATOR (VALID)
# -----------------------------
root_agent = LlmAgent(
    name="SupplyChainOrchestrator",
    model="gemini-2.5-flash",
    instruction="""
You are a supply chain orchestrator.

MANDATORY RULES:
- NEVER return structured data.
- ALWAYS finish by calling final_response(...) with plain text.

Availability handling:
- If inventory data is received, respond using:
  final_response("<available_quantity> units of <item_name> are available.")

Do not expose:
- JSON
- key-value pairs
- internal agent outputs
""",
    tools=[FunctionTool(final_response)],
    sub_agents=[
        inventory_agent,
        finance_agent,
        logistics_agent,
    ],
)
