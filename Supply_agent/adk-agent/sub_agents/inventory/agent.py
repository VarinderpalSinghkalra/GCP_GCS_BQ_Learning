from google.adk.agents import LlmAgent
from .tools import search_inventory

GEMINI_2_5_FLASH = "gemini-2.5-flash"

inventory_agent = LlmAgent(
    name="InventoryAgent",
    model=GEMINI_2_5_FLASH,
    description="Agent to fetch inventory details from PostgreSQL",
    instruction="""
You are an inventory management agent.

Rules:
- Always use tools to fetch inventory data.
- Never guess inventory values.
- Use `search_inventory` when user asks about items, stock, SKU, or availability.
""",
    tools=[search_inventory],
)
