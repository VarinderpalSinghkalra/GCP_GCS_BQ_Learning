from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from .inventory_tools import get_inventory_by_name

inventory_tool = FunctionTool(
    func=get_inventory_by_name
)

root_agent = LlmAgent(
    name="SupplyChainAgent",
    model="gemini-2.5-flash",
    instructions="""
You are a Supply Chain Inventory Agent.
Use the inventory tool to answer stock questions.
""",
    tools=[inventory_tool]
)
