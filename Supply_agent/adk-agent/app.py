from fastapi import FastAPI
from supply_chain_agent.agent import root_agent

app = FastAPI()

@app.post("/chat")
def chat(payload: dict):
    user_message = payload.get("message")
    response = root_agent.run(user_message)
    return {"response": response}
