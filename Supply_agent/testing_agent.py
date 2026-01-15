from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.google_search_tool import GoogleSearchTool

from .inventory_tools import get_inventory_by_name


# =========================================================
# FINAL RESPONSE TOOL (ONLY USER OUTPUT)
# =========================================================
def final_response(message: str) -> str:
    return message


# =========================================================
# INVENTORY AGENT (INTERNAL / SILENT)
# =========================================================
inventory_agent = LlmAgent(
    name="inventory_agent",
    model="gemini-2.5-flash",
    instruction="""
Always call get_inventory_by_name.
Return the tool output exactly as received.
Never format text.
Never speak to the user.
""",
    tools=[FunctionTool(get_inventory_by_name)],
)


# =========================================================
# FINANCE AGENT (BUSINESS ETHICAL / SILENT)
# =========================================================
finance_agent = LlmAgent(
    name="finance_agent",
    model="gemini-2.5-flash",
    instruction="""
You are a finance approval authority.

Policy:
- Orders below 100 units are not cost-effective.
- Orders of 100 units or more are financially justified.

Return EXACTLY one sentence:

If not approved:
"After financial review, the requested order does not meet procurement cost-efficiency guidelines."

If approved:
"Financial review completed successfully and the order is approved for further processing."

Never speak to the end user.
""",
)


# =========================================================
# LOGISTICS SEARCH AGENT
# =========================================================
logistics_search_agent = LlmAgent(
    name="logistics_search_agent",
    model="gemini-2.5-flash",
    instruction="""
Provide shipping and delivery options when requested.
""",
    tools=[GoogleSearchTool()],
)


# =========================================================
# LOGISTICS AGENT (INTERNAL / SILENT)
# =========================================================
logistics_agent = LlmAgent(
    name="logistics_agent",
    model="gemini-2.5-flash",
    instruction="""
Handle logistics ONLY after financial approval.
Never speak to the user.
""",
    tools=[agent_tool.AgentTool(agent=logistics_search_agent)],
)


# =========================================================
# ROOT ORCHESTRATOR (ONLY SPEAKER)
# =========================================================
root_agent = LlmAgent(
    name="SupplyChainOrchestrator",
    model="gemini-2.5-flash",
    instruction="""
You are the Supply Chain Orchestrator and the ONLY agent allowed to respond to the user.

ABSOLUTE RULES:
- You MUST always call final_response(message) as the last step.
- You MUST NEVER return JSON, lists, or tool outputs.

====================
INVENTORY HANDLING
====================
Inventory tool may return:
1) A STRING → inventory not found
2) A LIST of inventory records

RULES:
- If STRING:
    final_response(the string exactly as received)

- If LIST:
    - Take ONLY the FIRST item
    - Extract item_name and quantity
    - Respond ONLY as:
      final_response("<quantity> units of <item_name> are available.")

====================
ORDER HANDLING
====================
1. Send requested quantity to finance_agent

2. If finance response indicates NOT approved:
   Return the finance justification using final_response

3. If finance response indicates approval:
   - Route request to logistics_agent
   - Respond ONLY with:
     final_response(
       "The order for <quantity> units of <item_name> has been approved following financial review and is now being processed for shipment."
     )

Never explain internal reasoning.
Never expose agent or tool behavior.
""",
    tools=[FunctionTool(final_response)],
    sub_agents=[
        inventory_agent,
        finance_agent,
        logistics_agent,
    ],
)
