# workflow/final_workflow.py

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

from app.schemas.states.agentic_state import AgentState

from app.agents.nodes.decider import decider_node
from app.agents.nodes.conversational import conversational_node
from app.agents.nodes.intent_analyzer import intent_analyzer_node
from app.agents.nodes.supervisor import supervisor_node
from app.agents.nodes.info_collector import info_collector_node
from app.agents.nodes.validator import validator_node
from app.agents.nodes.query_refinement import query_refinement_node
from app.agents.nodes.data_retrieval import data_retrieval_node
from app.agents.nodes.response_generator import response_generator_node
from app.agents.nodes.memory_store_node import memory_store_node

from app.memory.memory_store import Memory_Functions
from app_backend.helper import get_checkpointer_helper


# ----------------------------
# Routers
# ----------------------------




# ----------------------------
# Routers
# ----------------------------

def decide_mode(state: AgentState) -> str:
    return state["mode"]


def supervisor_router(state: AgentState) -> str:
    return state["supervisor_decision"]





# ----------------------------
# Graph
# ----------------------------

graph = StateGraph(AgentState)

graph.add_node("decider", decider_node)
graph.add_node("conversation", conversational_node)

graph.add_node("intent", intent_analyzer_node)
graph.add_node("supervisor", supervisor_node)
graph.add_node("info_collector", info_collector_node)
graph.add_node("validator", validator_node)
graph.add_node("query_refinement", query_refinement_node)
graph.add_node("data_retrieval", data_retrieval_node)


graph.add_node("response_generator", response_generator_node)

graph.add_node("memory_store", memory_store_node)

graph.set_entry_point("decider")

graph.add_conditional_edges(
    "decider",
    decide_mode,
    {
        "conversation": "conversation",
        "agentic": "intent",
    },
)

graph.add_edge("conversation", END)

graph.add_edge("intent", "supervisor")

graph.add_conditional_edges(
    "supervisor",
    supervisor_router,
    {
        "need_info": "info_collector",
        "invalid": "validator",
        "ready": "query_refinement",  # Changed: go to query_refinement first
        "end": END,
    },
)

# Info collector loops back to supervisor after collecting info
graph.add_edge("info_collector", "supervisor")  # Fixed: loops back for continuation
graph.add_edge("validator", "supervisor")

# New flow: query_refinement -> data_retrieval
graph.add_edge("query_refinement", "data_retrieval")

# Reasoning Removed (it was empty)
# Data Retrieval -> Response Generator
graph.add_edge("data_retrieval", "response_generator")

# Finalize
graph.add_edge("response_generator", "memory_store")
graph.add_edge("memory_store", END)

# Compile with PostgreSQL checkpointer to enable interrupt/resume and thread persistence
checkpointer_helper = get_checkpointer_helper()
checkpointer = checkpointer_helper.get_checkpointer()
app = graph.compile(checkpointer=checkpointer)


def get_compiled_app():
    """Return the compiled workflow app"""
    return app

# Compiled graph for LangGraph Studio (no custom checkpointer)
studio_app = graph.compile()
