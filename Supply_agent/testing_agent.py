from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools import url_context

from .inventory_tools import get_inventory_by_name

# -----------------------------
# LOGISTICS SEARCH AGENT
# -----------------------------
logistics_search_agent = LlmAgent(
    name="logistics_search_agent",
    model="gemini-2.5-flash",
    instruction="Search the web for logistics providers and shipping options.",
    tools=[GoogleSearchTool()],
)

# -----------------------------
# LOGISTICS AGENT
# -----------------------------
logistics_agent = LlmAgent(
    name="logistics_agent",
    model="gemini-2.5-flash",
    instruction="Manage shipping and logistics queries.",
    tools=[agent_tool.AgentTool(agent=logistics_search_agent)],
)

# -----------------------------
# INVENTORY AGENT (POSTGRES)
# -----------------------------
inventory_agent = LlmAgent(
    name="inventory_agent",
    model="gemini-2.5-flash",
    instruction="""
You are an inventory management agent.

Rules:
- Always call get_inventory_by_name for inventory questions
- Summarize the tool result in plain English
- Do not ask unnecessary follow-up questions
""",
    tools=[FunctionTool(get_inventory_by_name)],
)

# -----------------------------
# FINANCE AGENT
# -----------------------------
finance_agent = LlmAgent(
    name="finance_agent",
    model="gemini-2.5-flash",
    instruction="Handle finance approvals and validations.",
    tools=[agent_tool.AgentTool(agent=logistics_search_agent)],
)

# -----------------------------
# ROOT ORCHESTRATOR
# -----------------------------
root_agent = LlmAgent(
    name="SupplyChainOrchestrator",
    model="gemini-2.5-flash",
    instruction="""
Route requests:
- Inventory → inventory_agent
- Logistics → logistics_agent
- Finance → finance_agent
""",
    sub_agents=[inventory_agent, logistics_agent, finance_agent],
)
