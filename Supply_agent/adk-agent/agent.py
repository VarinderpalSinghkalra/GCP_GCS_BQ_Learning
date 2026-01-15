from google.adk.agents import LlmAgent
from supply_chain_agent.sub_agents.inventory.agent import inventory_agent
from supply_chain_agent.sub_agents.finance.agent import finance_agent
from supply_chain_agent.sub_agents.logistics.agent import logistics_agent

GEMINI_2_5_FLASH = "gemini-2.5-flash"

root_agent = LlmAgent(
    name="OrchestratorAgent",
    model=GEMINI_2_5_FLASH,
    description="Supply chain orchestrator agent",
    instruction="""
You are a supply chain orchestrator.

Responsibilities:
- Delegate inventory queries to InventoryAgent
- Obtain approvals from FinanceAgent
- Use LogisticsAgent for shipping

Follow correct order and business rules.
""",
    sub_agents=[inventory_agent, finance_agent, logistics_agent],
)
