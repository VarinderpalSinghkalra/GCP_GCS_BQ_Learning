from google.adk.agents import LlmAgent
from .tool import find_shipping_options, execute_shipment

GEMINI_2_5_FLASH = "gemini-2.5-flash"

logistics_agent = LlmAgent(
    name="LogisticsAgent",
    model=GEMINI_2_5_FLASH,
    instruction="""
You are a logistics coordinator.

Rules:
- You must obtain financial approval before executing shipment.
- Use tools to find and execute shipping options.
""",
    tools=[find_shipping_options, execute_shipment],
    description="Manages shipping and logistics.",
)
