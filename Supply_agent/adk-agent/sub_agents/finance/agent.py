from google.adk.agents.remote.a2a_agent import RemoteA2AAgent
from google.adk.agents.remote.a2a_agent import AGENT_CARD_WELL_KNOWN_PATH

finance_agent = RemoteA2AAgent(
    name="finance_agent",
    description="Helpful financial controller that can approve expenditures",
    agent_card=f"http://localhost:8001/{AGENT_CARD_WELL_KNOWN_PATH}",
)
