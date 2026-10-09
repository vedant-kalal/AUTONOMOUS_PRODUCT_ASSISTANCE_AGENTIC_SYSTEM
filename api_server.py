"""
FastAPI backend for the React frontend.
Thin HTTP wrapper around the existing LangGraph workflow and Memory_Functions —
no agent/memory logic lives here, it all still lives in app/.
"""

import uuid
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command

load_dotenv()

from app.agents.workflow.final_workflow import app as chatbot
from app.memory.memory_store import Memory_Functions
from app_backend.utils import ThreadManager

app = FastAPI(title="Trust Cart AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ======================= Schemas =======================

class ChatRequest(BaseModel):
    thread_id: str
    message: str
    optimization_goal: str = "Balanced"
    is_gift: bool = False


class ResumeRequest(BaseModel):
    thread_id: str
    answers: Dict[str, str] = {}
    skipped: bool = False


class FeedbackRequest(BaseModel):
    product_title: str
    rating: int
    thread_id: str = "default"
    brand: Optional[str] = None
    category: Optional[str] = None


class WishlistRequest(BaseModel):
    product: Dict[str, Any]


class ShareRequest(BaseModel):
    query: str
    response: str
    products: List[Dict[str, Any]] = []


# ======================= Helpers =======================

def attach_reasons(products: List[Dict[str, Any]], product_reasons: Dict[str, str]) -> List[Dict[str, Any]]:
    if not product_reasons:
        return products
    merged = []
    for p in products:
        if isinstance(p, dict):
            p = dict(p)
            p["why"] = product_reasons.get(p.get("title"))
        merged.append(p)
    return merged


def _config(thread_id: str) -> Dict[str, Any]:
    return {
        "configurable": {"thread_id": thread_id},
        "metadata": {"thread_id": thread_id},
        "run_name": "chat_turn",
    }


def _check_interrupt(config: Dict[str, Any]) -> Optional[List[str]]:
    state = chatbot.get_state(config)
    if state.next and len(state.tasks) > 0:
        interrupts = state.tasks[0].interrupts
        if interrupts and len(interrupts) > 0:
            questions = interrupts[0].value
            if isinstance(questions, list) and len(questions) > 0:
                return questions
    return None


def _finalize_result(result: Dict[str, Any]) -> Dict[str, Any]:
    final_output = result.get("final_output") or {}
    response_text = final_output.get("response", "")
    products = final_output.get("products", [])
    product_reasons = final_output.get("product_reasons", {})
    products = attach_reasons(products, product_reasons)
    return {"status": "complete", "response": response_text, "products": products}


# ======================= Chat =======================

@app.post("/api/chat")
def start_chat(req: ChatRequest):
    config = _config(req.thread_id)
    Memory_Functions.add_recent_message(HumanMessage(content=req.message), req.thread_id)

    final_state = None
    for event in chatbot.stream(
        {
            "user_query": req.message,
            "original_user_query": req.message,
            "mode": None,
            "supervisor_decision": None,
            "final_output": None,
            "intent": {},
            "collected_info": {},
            "generated_questions": [],
            "optimization_goal": req.optimization_goal,
            "is_gift": req.is_gift,
        },
        config,
        stream_mode="updates",
    ):
        if isinstance(event, dict):
            for key in event:
                if isinstance(event[key], dict):
                    final_state = event[key]

    result = final_state or {}

    questions = _check_interrupt(config)
    if questions is not None:
        return {"status": "awaiting_answers", "questions": questions}

    if result.get("final_output"):
        out = _finalize_result(result)
        Memory_Functions.add_recent_message(AIMessage(content=out["response"]), req.thread_id)
        return out

    return {"status": "error", "message": "No response generated."}


@app.post("/api/chat/resume")
def resume_chat(req: ResumeRequest):
    config = _config(req.thread_id)

    if req.skipped:
        answers: Dict[str, Any] = {"skipped": True}
        Memory_Functions.add_recent_message(
            AIMessage(content="Questions & Answers:\nUser skipped answering the questions."),
            req.thread_id,
        )
    else:
        if not req.answers:
            raise HTTPException(400, "Provide at least one answer or set skipped=true.")
        answers = req.answers
        qa_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in req.answers.items()])
        Memory_Functions.add_recent_message(
            AIMessage(content=f"Questions & Answers:\n{qa_text}"),
            req.thread_id,
        )

    result = chatbot.invoke(Command(resume=answers), config)

    if result.get("final_output"):
        out = _finalize_result(result)
        Memory_Functions.add_recent_message(AIMessage(content=out["response"]), req.thread_id)
        return out

    questions = _check_interrupt(config)
    if questions is not None:
        return {"status": "awaiting_answers", "questions": questions}

    return {"status": "error", "message": "Processing complete but no response generated."}


# ======================= Threads =======================

@app.post("/api/threads")
def new_thread():
    return {"thread_id": ThreadManager.generate_thread_id()}


@app.get("/api/threads")
def list_threads():
    try:
        threads = ThreadManager.get_all_threads()
    except Exception:
        threads = []
    return {"threads": sorted(threads, reverse=True)}


@app.get("/api/threads/{thread_id}/preview")
def thread_preview(thread_id: str):
    return {"preview": ThreadManager.get_thread_preview(thread_id, chatbot)}


@app.get("/api/threads/{thread_id}/messages")
def thread_messages(thread_id: str):
    messages = Memory_Functions.get_recent_messages(thread_id)
    out = []
    for msg in messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        out.append({"role": role, "content": msg.content})
    return {"messages": out}


@app.delete("/api/threads/{thread_id}")
def delete_thread(thread_id: str):
    Memory_Functions.clear_recent_messages(thread_id)
    Memory_Functions.clear_long_term_memory(thread_id)
    Memory_Functions.clear_summary(thread_id)
    return {"ok": True}


# ======================= Wishlist =======================

@app.get("/api/wishlist")
def get_wishlist():
    return {"items": Memory_Functions.get_wishlist()}


@app.post("/api/wishlist")
def add_wishlist(req: WishlistRequest):
    Memory_Functions.add_to_wishlist(req.product)
    return {"ok": True}


@app.delete("/api/wishlist/{key}")
def remove_wishlist(key: str):
    Memory_Functions.remove_from_wishlist(key)
    return {"ok": True}


# ======================= Feedback =======================

@app.post("/api/feedback")
def add_feedback(req: FeedbackRequest):
    Memory_Functions.store_feedback(req.product_title, req.rating, req.thread_id, brand=req.brand, category=req.category)
    return {"ok": True}


# ======================= Share =======================

@app.post("/api/share")
def create_share(req: ShareRequest):
    token = uuid.uuid4().hex
    Memory_Functions.store_shared_result(token, {
        "query": req.query,
        "response": req.response,
        "products": req.products,
    })
    return {"token": token}


@app.get("/api/share/{token}")
def get_share(token: str):
    snapshot = Memory_Functions.get_shared_result(token)
    if not snapshot:
        raise HTTPException(404, "Shared link not found or expired.")
    return snapshot


@app.get("/api/health")
def health():
    return {"status": "ok"}
