from google.adk.agents import LlmAgent

legal_review_agent = LlmAgent(
    name="LegalReviewAgent",
    model="gemini-2.5-flash",
    instruction="Identify legal risks and escalation needs. JSON only."
)

