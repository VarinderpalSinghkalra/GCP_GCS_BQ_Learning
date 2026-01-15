from fastapi import FastAPI
from google.adk.agents.remote.a2a_server import A2AServer
from finance.agent import finance_agent

app = FastAPI()
A2AServer(app, finance_agent)
