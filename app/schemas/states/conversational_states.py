from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class ConversationalState(dict):
    messages: Annotated[list[BaseMessage], add_messages]
    summary: str
    last_recommendation: dict | None
