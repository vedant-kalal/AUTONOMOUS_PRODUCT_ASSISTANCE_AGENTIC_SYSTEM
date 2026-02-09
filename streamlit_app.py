"""
Streamlit Chat Interface for Product Assistant
Dark theme with proper message ordering and improved UI
"""

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command

from app.agents.workflow.final_workflow import app as chatbot
from app_backend.utils import ThreadManager, SessionManager
from app.memory.memory_store import Memory_Functions
from app.core.logging.utils import log_chat_start, log_error, log_qa_session, log_chat_response


# ======================= Page Configuration ===================
st.set_page_config(
    page_title="AI Shopping Assistant",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================= Dark Theme CSS ===================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Bright Black Background */
    .stApp {
        background-color: #0a0a0a;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #121212;
        border-right: 1px solid #2a2a2a;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding: 1.5rem 1rem;
    }
    
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    
    /* Main content */
    .main {
        background-color: #0a0a0a;
    }
    
    .main > div {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Headings */
    h1 {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2, h3, h4, h5, h6 {
        color: #e0e0e0 !important;
    }
    
    p {
        color: #b0b0b0 !important;
        font-size: 1rem;
    }
    
    /* User Message Panel - Dark Blue */
    [data-testid="stChatMessage"][data-testid*="user"] {
        background-color: #1a1f3a !important;
        border-left: 3px solid #5865f2 !important;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin: 0.75rem 0;
    }
    
    [data-testid="stChatMessage"][data-testid*="user"] p {
        color: #ffffff !important;
    }
    
    /* AI Message Panel - Dark Green */
    [data-testid="stChatMessage"][data-testid*="assistant"] {
        background-color: #1a2f1a !important;
        border-left: 3px solid #3ba55c !important;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin: 0.75rem 0;
    }
    
    [data-testid="stChatMessage"][data-testid*="assistant"] p {
        color: #e0e0e0 !important;
    }
    
    /* Q&A Table Styling */
    .qa-table {
        background-color: #1a1a2a;
        border: 1px solid #2a2a4a;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .qa-row {
        padding: 0.5rem;
        margin: 0.3rem 0;
        background-color: #0f0f1a;
        border-radius: 4px;
    }
    
    .qa-question {
        color: #8b8bff;
        font-weight: 500;
    }
    
    .qa-answer {
        color: #7fff7f;
        margin-left: 1rem;
    }
    
    /* Chat input */
    .stChatInput {
        background-color: #1a1a1a !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 8px !important;
    }
    
    .stChatInput input {
        color: #ffffff !important;
        background-color: #1a1a1a !important;
    }
    
    .stChatInput input::placeholder {
        color: #606060 !important;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 6px;
        padding: 0.6rem 1rem;
        font-weight: 500;
        border: 1px solid #2a2a2a;
        background-color: #1a1a1a;
        color: #e0e0e0;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #2a2a2a;
        border-color: #3a3a3a;
        transform: translateY(-1px);
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #5865f2 0%, #7289da 100%);
        color: #ffffff;
        border: none;
        font-weight: 600;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #7289da 0%, #5865f2 100%);
        box-shadow: 0 4px 12px rgba(88, 101, 242, 0.3);
    }
    
    .stButton > button:disabled {
        background-color: #2a2a2a;
        color: #3ba55c;
        border-color: #3ba55c;
        opacity: 1;
    }
    
    /* Delete button - centered and styled */
    .delete-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
    }
    
    .delete-btn button {
        padding: 0.5rem !important;
        min-width: 38px !important;
        width: 38px !important;
        height: 38px !important;
        font-size: 1.2rem !important;
        background-color: #2a1a1a !important;
        border: 1px solid #ff4444 !important;
        border-radius: 6px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    .delete-btn button:hover {
        background-color: #ff4444 !important;
        transform: scale(1.05) !important;
    }
    
    .stAlert {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        color: #e0e0e0;
    }
    
    hr {
        margin: 1.5rem 0;
        border-color: #2a2a2a;
        opacity: 0.5;
    }
    
    .stCaption {
        color: #606060 !important;
        font-size: 0.85rem;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        text-align: left;
        margin-bottom: 0.4rem;
        font-size: 0.9rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0a0a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #2a2a2a;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #3a3a3a;
    }
    
    /* Form elements */
    .stTextInput input {
        background-color: #1a1a1a !important;
        border: 1px solid #2a2a2a !important;
        color: #ffffff !important;
        border-radius: 6px !important;
    }
    
    .stTextInput label {
        color: #e0e0e0 !important;
        font-weight: 500 !important;
    }
    
    footer {
        visibility: hidden;
    }
    
    .custom-footer {
        text-align: center;
        padding: 1rem;
        color: #606060;
        font-size: 0.85rem;
        border-top: 1px solid #2a2a2a;
        margin-top: 2rem;
    }
    
    /* Spinner visibility fix */
    .stSpinner > div {
        border-color: #3ba55c transparent transparent transparent !important;
    }
</style>
""", unsafe_allow_html=True)


# ======================= Helper Functions ===================
def load_thread_history(thread_id: str):
    """Load message history in chronological order with Q&A table reconstruction"""
    try:
        messages = Memory_Functions.get_recent_messages(thread_id)
        history = []
        
        for msg in messages:
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                # Check if this is a Q&A table (stored as plain text)
                if msg.content.startswith("Questions & Answers:"):
                    # Parse and reconstruct Q&A table
                    qa_pairs = []
                    # Handle both literal newlines and escaped newlines
                    content = msg.content.replace('\\n', '\n')
                    lines = content.split('\n')[1:]  # Skip header
                    
                    current_q = None
                    for line in lines:
                        line = line.strip()
                        if line.startswith("Q: "):
                            current_q = line[3:]  # Remove "Q: "
                        elif line.startswith("A: ") and current_q:
                            current_a = line[3:]  # Remove "A: "
                            qa_pairs.append({"question": current_q, "answer": current_a})
                            current_q = None
                    
                    # Add as Q&A table format
                    if qa_pairs:
                        history.append({
                            "role": "assistant",
                            "type": "qa_table",
                            "content": qa_pairs
                        })
                    else:
                        # Fallback to plain text if parsing fails
                        history.append({"role": "assistant", "content": msg.content})
                else:
                    history.append({"role": "assistant", "content": msg.content})
        
        return history
    except Exception as e:
        print(f"Error loading history: {e}")
        return []


def stream_response(text):
    """Stream text word by word"""
    words = text.split()
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")


# ======================= Session Init ===================
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = ThreadManager.generate_thread_id()

if "message_history" not in st.session_state:
    st.session_state["message_history"] = load_thread_history(st.session_state["thread_id"])

if "chat_threads" not in st.session_state:
    try:
        all_threads = ThreadManager.get_all_threads()
        st.session_state["chat_threads"] = sorted(all_threads, reverse=True)
        if st.session_state["thread_id"] not in st.session_state["chat_threads"]:
            st.session_state["chat_threads"].insert(0, st.session_state["thread_id"])
    except:
        st.session_state["chat_threads"] = [st.session_state["thread_id"]]

if "waiting_for_questions" not in st.session_state:
    st.session_state["waiting_for_questions"] = False
    st.session_state["pending_questions"] = []
    st.session_state["pending_config"] = {}


# ============================ Sidebar ============================
with st.sidebar:
    st.markdown("# 🛍️ Product Assistant")
    st.markdown("---")
    
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        new_thread_id = ThreadManager.generate_thread_id()
        st.session_state["thread_id"] = new_thread_id
        st.session_state["message_history"] = []
        st.session_state["waiting_for_questions"] = False
        st.session_state["pending_questions"] = []
        
        if new_thread_id not in st.session_state["chat_threads"]:
            st.session_state["chat_threads"].insert(0, new_thread_id)
        
        st.rerun()
    
    st.markdown("")
    st.markdown("### 💬 Conversations")
    
    if st.session_state["chat_threads"]:
        for thread_id in st.session_state["chat_threads"]:
            preview = ThreadManager.get_thread_preview(thread_id, chatbot)
            is_current = thread_id == st.session_state["thread_id"]
            
            # Simple button for thread selection
            if st.button(
                f"{'🔵 ' if is_current else '💬 '}{preview}",
                key=f"thread_{thread_id}",
                use_container_width=True,
                disabled=is_current
            ):
                st.session_state["thread_id"] = thread_id
                st.session_state["message_history"] = load_thread_history(thread_id)
                st.session_state["waiting_for_questions"] = False
                st.session_state["pending_questions"] = []
                st.rerun()
    else:
        st.info("No conversations yet!")
    
    st.markdown("---")
    st.caption(f"🆔 {st.session_state['thread_id'][:8]}...")


# ============================ Main Chat ============================
header_col1, header_col2 = st.columns([6, 1])

with header_col1:
    st.markdown("# 🤖 AI Shopping Assistant")
    st.markdown("Ask me anything!")

with header_col2:
    with st.popover("⋮", use_container_width=True):
        if st.button("🗑️ Delete Chat", key="delete_current_chat", type="primary"):
            ThreadManager.delete_thread(st.session_state["thread_id"])
            if st.session_state["thread_id"] in st.session_state["chat_threads"]:
                st.session_state["chat_threads"].remove(st.session_state["thread_id"])
            
            Memory_Functions.clear_recent_messages(st.session_state["thread_id"])
            Memory_Functions.clear_long_term_memory(st.session_state["thread_id"])
            Memory_Functions.clear_summary(st.session_state["thread_id"])
            
            # Delete log files
            import os
            import glob
            try:
                log_pattern = f"logs/*/*_{st.session_state['thread_id']}.log"
                for log_file in glob.glob(log_pattern):
                    try:
                        os.remove(log_file)
                    except:
                        pass
            except:
                pass
            
            # Generate new thread and reload
            st.session_state["thread_id"] = ThreadManager.generate_thread_id()
            st.session_state["message_history"] = []
            st.session_state["waiting_for_questions"] = False
            
            if st.session_state["thread_id"] not in st.session_state["chat_threads"]:
                st.session_state["chat_threads"].insert(0, st.session_state["thread_id"])
                
            st.rerun()

st.markdown("")

# Display chat history in chronological order (oldest → newest)
for message in st.session_state["message_history"]:
    # Check if it's a Q&A table format
    if message["role"] == "assistant" and message.get("type") == "qa_table":
        with st.chat_message("assistant"):
            st.markdown("### 📋 Questions & Answers")
            qa_html = '<div class="qa-table">'
            for qa in message["content"]:
                qa_html += f'<div class="qa-row"><span class="qa-question">Q: {qa["question"]}</span><br><span class="qa-answer">A: {qa["answer"]}</span></div>'
            qa_html += '</div>'
            st.markdown(qa_html, unsafe_allow_html=True)
    else:
        with st.chat_message(message["role"]):
            if "role" == "assistant":
                 with st.container(border=True):
                     st.markdown(message["content"])
            else:
                 st.markdown(message["content"])

# Handle questions inline
if st.session_state.get("waiting_for_questions", False):
    with st.chat_message("assistant"):
        st.markdown("### 📋 I need some information:")
        
        # Use a form to prevent auto-submit on Enter and stabilize UI
        with st.form(key=f"qa_form_{st.session_state['thread_id']}"):
            collected_answers = {}
            for i, question in enumerate(st.session_state["pending_questions"], 1):
                answer = st.text_input(
                    f"**{i}.** {question}",
                    key=f"q_{i}_{st.session_state['thread_id']}",
                    label_visibility="visible"
                )
                if answer:
                    collected_answers[question] = answer
            
            # Submit button
            submit_clicked = st.form_submit_button("Submit Answers", type="primary")

        # Process submission outside the form
        if submit_clicked:
            # Validate all questions answered
            if len(collected_answers) == len(st.session_state["pending_questions"]) and all(collected_answers.values()):
                # Store Q&A as table
                qa_pairs = [{"question": q, "answer": a} for q, a in collected_answers.items()]
                st.session_state["message_history"].append({
                    "role": "assistant",
                    "type": "qa_table",
                    "content": qa_pairs
                })
                
                # Store in memory
                # Store in memory
                qa_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in collected_answers.items()])
                Memory_Functions.add_recent_message(
                    AIMessage(content=f"Questions & Answers:\n{qa_text}"),
                    st.session_state["thread_id"]
                )
                
                CONFIG = st.session_state["pending_config"]
                
                # Show thinking spinner
                with st.spinner("🤔 Finding products..."):
                    try:
                        # Pass the single dictionary of collected answers
                        result = chatbot.invoke(Command(resume=collected_answers), CONFIG)
                        
                        if result.get("final_output"):
                            response = result["final_output"].get("response", "No response")
                            
                            st.session_state["message_history"].append({
                                "role": "assistant",
                                "content": response
                            })
                            
                            Memory_Functions.add_recent_message(
                                AIMessage(content=response),
                                st.session_state["thread_id"]
                            )
                            
                            # Success! Clear waiting state
                            st.session_state["waiting_for_questions"] = False
                            st.session_state["pending_questions"] = []
                            st.session_state["pending_config"] = {}
                            st.rerun()
                        
                        else:
                            # Check for NEW interrupts (e.g. clarification needed)
                            current_state = chatbot.get_state(CONFIG)
                            if current_state.next and current_state.tasks[0].interrupts:
                                new_interrupts = current_state.tasks[0].interrupts
                                if new_interrupts:
                                    st.warning("⚠️ The agent has more questions.")
                                    st.session_state["pending_questions"] = new_interrupts[0].value
                                    st.rerun()
                            
                            # Fallback: Logic finished but no response?
                            st.warning("⚠️ Processing complete but no response generated.")
                            st.session_state["waiting_for_questions"] = False
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ {str(e)}")
                        log_error(st.session_state["thread_id"], "Streamlit Resumption", e)
            else:
                st.warning("⚠️ Please answer all questions before submitting.")


# Chat input
if not st.session_state.get("waiting_for_questions", False):
    user_input = st.chat_input("Type here...")

    if user_input:
        try:
            # Log chat start
            log_chat_start(st.session_state["thread_id"], user_input)
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(user_input)
        
            # Add to history
            st.session_state["message_history"].append({"role": "user", "content": user_input})
            Memory_Functions.add_recent_message(
                HumanMessage(content=user_input),
                st.session_state["thread_id"]
            )
            
            CONFIG = {
                "configurable": {"thread_id": st.session_state["thread_id"]},
                "metadata": {"thread_id": st.session_state["thread_id"]},
                "run_name": "chat_turn",
            }
            
            # AI response with visible thinking spinner
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                status_placeholder = st.empty()
                
                try:
                    # Show thinking status
                    with status_placeholder:
                        with st.spinner("Thinking..."):
                            # Stream events to update status
                            final_state = None
                            result = {}
                            
                            for event in chatbot.stream(
                                {
                                    "user_query": user_input,
                                    "original_user_query": user_input,
                                    "mode": None,
                                    "supervisor_decision": None,
                                    "final_output": None,
                                    "intent": {},
                                    "collected_info": {},
                                    "generated_questions": []
                                },
                                CONFIG,
                                stream_mode="updates"
                            ):
                                # Keep track of the latest state for final output
                                if isinstance(event, dict):
                                    for key in event:
                                        if isinstance(event[key], dict):
                                            final_state = event[key]
                            
                            # Prepare result from final state
                            result = final_state if final_state else {}
                            
                            # Check for interrupts
                            current_graph_state = chatbot.get_state(CONFIG)
                            if current_graph_state.next:
                                if len(current_graph_state.tasks) > 0 and str(current_graph_state.tasks[0].interrupts):
                                    interrupts = current_graph_state.tasks[0].interrupts
                                    if interrupts:
                                        questions = interrupts[0].value
                                        st.session_state["waiting_for_questions"] = True
                                        st.session_state["pending_questions"] = questions
                                        st.session_state["pending_config"] = CONFIG
                                        st.rerun()

                    # Display response with streaming
                    if result.get("final_output"):
                        response_text = result["final_output"].get("response", "No response")
                        
                        # Use a container wrapper for cleaner presentation
                        with response_placeholder.container(border=True):
                            st.markdown(response_text)
                        
                        st.session_state["message_history"].append({
                            "role": "assistant",
                            "content": response_text
                        })
                        
                        Memory_Functions.add_recent_message(
                            AIMessage(content=response_text),
                            st.session_state["thread_id"]
                        )
                        log_chat_response(st.session_state["thread_id"], response_text)
                    else:
                        response_placeholder.warning("⚠️ No response")
                
                except Exception as e:
                    response_placeholder.error(f"❌ {str(e)}")
                    log_error(st.session_state["thread_id"], "Streamlit Chat Processing", e)
                    with st.expander("Details"):
                        import traceback
                        st.code(traceback.format_exc())
        
        except Exception as e:
            st.error(f"❌ Error processing message: {str(e)}")
            log_error(st.session_state["thread_id"], "Streamlit UI", e)

# Auto-scroll to bottom using JavaScript
import streamlit.components.v1 as components
components.html("""
<script>
    function scrollToBottom() {
        var element = window.parent.document.getElementsByClassName('stChatInput')[0];
        if (element) {
            element.scrollIntoView({behavior: "instant", block: "end"});
        } else {
            window.parent.window.scrollTo(0, window.parent.document.body.scrollHeight);
        }
    }
    // Run with a slight delay to allow DOM updates
    setTimeout(scrollToBottom, 100);
    setTimeout(scrollToBottom, 500); // Retry just in case
</script>
""", height=0)


st.markdown('<div class="custom-footer">Made with ❤️ by <a href="https://www.linkedin.com/in/vedantkalal">Vedant Kalal</a></div>', unsafe_allow_html=True)
