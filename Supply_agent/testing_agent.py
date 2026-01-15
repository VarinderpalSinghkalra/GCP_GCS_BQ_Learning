from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.google_search_tool import GoogleSearchTool

from .inventory_tools import get_inventory_by_name


# -----------------------------
# LOGISTICS SEARCH AGENT
# -----------------------------
logistics_search_agent = LlmAgent(
    name="logistics_search_agent",
    model="gemini-2.5-flash",
    instruction="""
You are a logistics research agent.

Responsibilities:
- Search the web for shipping providers and routes.

Rules:
- Only perform web searches.
- Do NOT approve finances.
- Do NOT execute shipments.
- Do NOT interact with inventory data.
- Do NOT expose raw search results.
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

Responsibilities:
- Execute shipment ONLY after approval.

Rules:
- Use logistics_search_agent.
- Do NOT approve costs.
- Do NOT check inventory.
- Do NOT expose internal data.
""",
    tools=[agent_tool.AgentTool(agent=logistics_search_agent)],
)


# -----------------------------
# INVENTORY AGENT (STRICT – INTERNAL ONLY)
# -----------------------------
inventory_agent = LlmAgent(
    name="inventory_agent",
    model="gemini-2.5-flash",
    instruction="""
You are an inventory agent.

Responsibilities:
- Retrieve item availability by name or ID.

STRICT INTERNAL CONTRACT:
You MUST return ONLY structured data to the orchestrator.

Allowed fields (INTERNAL ONLY):
- item_name
- available_quantity
- status

Rules:
- DO NOT greet.
- DO NOT ask questions.
- DO NOT approve finances.
- DO NOT manage logistics.
- ALWAYS call get_inventory_by_name.
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
You are a financial approval agent.

DECISION RULES (STRICT):

- If order quantity is LESS THAN 100 units → REJECT.
- If order quantity is 100 units or more → APPROVE.

REJECTION MESSAGE:
"The request is rejected because the order quantity is below the minimum approval threshold."

APPROVAL MESSAGE:
"The request meets the quantity requirements and is approved."

Rules:
- DO NOT check inventory.
- DO NOT check cost.
- DO NOT execute logistics.
- ALWAYS return a clear decision.
""",
)


# -----------------------------
# ROOT ORCHESTRATOR (CRITICAL FIX)
# -----------------------------
root_agent = LlmAgent(
    name="SupplyChainOrchestrator",
    model="gemini-2.5-flash",
    output_mime_type="text/plain",  # 🔥 PREVENTS JSON / STRUCTURED OUTPUT
    instruction="""
You are a supply chain orchestrator.

ABSOLUTE OUTPUT RULE:
- You MUST ALWAYS return a single human-readable sentence.
- You MUST NEVER return JSON, structured data, or key-value output.

AVAILABILITY HANDLING:
- Respond ONLY as:
  "<available_quantity> units of <item_name> are available."

ORDER HANDLING:
- Validate quantity using FinanceAgent.
- If approved → proceed to logistics.
- If rejected → return rejection message.

FORBIDDEN OUTPUTS:
- JSON
- item_name:
- available_quantity:
- status:
- lists, tables, or schemas

WORKFLOW:
1. Detect user intent.
2. Call InventoryAgent (internal).
3. Summarize result in one sentence.
4. End the response.
""",
    sub_agents=[
        inventory_agent,
        finance_agent,
        logistics_agent,
    ],
)
