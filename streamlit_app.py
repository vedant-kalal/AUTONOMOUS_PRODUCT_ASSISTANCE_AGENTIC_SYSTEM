"""
Streamlit Chat Interface for Product Assistant
Dark theme with proper message ordering and improved UI
"""

import uuid

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command
from streamlit_mic_recorder import speech_to_text

from app.agents.workflow.final_workflow import app as chatbot
from app_backend.utils import ThreadManager, SessionManager
from app.memory.memory_store import Memory_Functions
from app.core.logging.utils import log_chat_start, log_error, log_qa_session, log_chat_response


# ======================= Page Configuration ===================
st.set_page_config(
    page_title="Trust Cart AI",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================= Bespoke styling (beyond what config.toml theming covers) ===================
# Base colors, fonts, borders, and button styling all live in .streamlit/config.toml.
# This block only covers the handful of custom shapes native theming has no hook for:
# per-role chat bubble accents, the gradient brand title, and the scrollbar.
st.markdown("""
<style>
    /* Gradient brand title */
    .tc-title {
        font-size: 2.1rem;
        font-weight: 700;
        background: linear-gradient(135deg, #818CF8 0%, #6366F1 45%, #34D399 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        margin-bottom: 0;
    }

    .tc-subtitle {
        color: #8B93A1;
        font-size: 0.95rem;
        margin-top: -0.3rem;
    }

    /* User message: indigo accent */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        border-left: 3px solid #6366F1 !important;
        border-radius: 12px;
    }

    /* Assistant message: emerald accent */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
        border-left: 3px solid #10B981 !important;
        border-radius: 12px;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #0B0D12; }
    ::-webkit-scrollbar-thumb { background: #242832; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #333947; }

    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ======================= Shared (read-only) result view ===================
# If the URL has ?share=<token>, render a standalone read-only page instead of the chat UI.
_share_token = st.query_params.get("share")
if _share_token:
    snapshot = Memory_Functions.get_shared_result(_share_token)
    st.markdown('<p class="tc-title">🛒 Trust Cart AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="tc-subtitle">Shared recommendation</p>', unsafe_allow_html=True)
    if not snapshot:
        st.error("This shared link is invalid or has expired.", icon=":material/link_off:")
    else:
        st.caption(f'Originally asked: "{snapshot.get("query", "")}"')
        st.markdown(snapshot.get("response", ""))
        products = snapshot.get("products", [])
        image_products = [p for p in products if isinstance(p, dict) and p.get("thumbnail")]
        if image_products:
            st.markdown("##### :material/storefront: Product gallery")
            cols = st.columns(min(len(image_products), 3))
            for idx, prod in enumerate(image_products[:6]):
                with cols[idx % 3], st.container(border=True):
                    try:
                        st.image(prod.get("thumbnail", ""), width="stretch")
                    except Exception:
                        pass
                    st.markdown(f"**{prod.get('title', 'Product')}**")
                    if prod.get("url"):
                        st.link_button("View product", prod["url"], icon=":material/shopping_cart:", width="stretch")
    st.caption("This is a read-only shared view. Open Trust Cart AI directly to start your own search.")
    st.stop()


# ======================= Product gallery renderer ===================
def render_product_gallery(products, key_prefix: str, thread_id: str):
    """Render product cards (image, price, why-this, save/feedback actions) for one assistant turn.

    `key_prefix` must be stable and unique per rendered turn so widget keys don't collide
    across reruns or across different messages in history.
    """
    image_products = [p for p in products if isinstance(p, dict) and p.get("thumbnail")]
    if not image_products:
        return

    st.markdown("##### :material/storefront: Product gallery")
    cols = st.columns(min(len(image_products), 3))
    for idx, prod in enumerate(image_products[:6]):
        col = cols[idx % 3]
        with col, st.container(border=True):
            thumb = prod.get("thumbnail", "")
            title = prod.get("title", "Product")
            price = prod.get("price")
            rating = prod.get("rating")
            url = prod.get("url") or prod.get("link")
            brand = prod.get("brand", "")
            why = prod.get("why")
            item_key = f"{key_prefix}_{idx}_{(title or '')[:40]}"

            try:
                st.image(thumb, width="stretch")
            except Exception:
                pass

            st.markdown(f"**{title}**")
            badge_row = st.container(horizontal=True)
            with badge_row:
                if price:
                    st.badge(f"${price:.2f}", icon=":material/payments:", color="green")
                if rating:
                    st.badge(f"{rating}/5", icon=":material/star:", color="orange")
                if brand:
                    st.badge(brand, icon=":material/sell:", color="violet")

            if url:
                st.link_button("View product", url, icon=":material/shopping_cart:", width="stretch")

            if why:
                with st.expander("Why this?", icon=":material/psychology:"):
                    st.write(why)

            action_row = st.container(horizontal=True)
            with action_row:
                if st.button("", icon=":material/thumb_up:", key=f"up_{item_key}", help="Good recommendation"):
                    Memory_Functions.store_feedback(title, 1, thread_id, brand=brand, category=prod.get("category"))
                    st.toast("Thanks! I'll recommend more like this.", icon=":material/thumb_up:")
                if st.button("", icon=":material/thumb_down:", key=f"down_{item_key}", help="Not a good fit"):
                    Memory_Functions.store_feedback(title, -1, thread_id, brand=brand, category=prod.get("category"))
                    st.toast("Got it — I'll avoid recommending similar items.", icon=":material/thumb_down:")
                if st.button("Save", icon=":material/bookmark_add:", key=f"save_{item_key}", help="Save for later"):
                    Memory_Functions.add_to_wishlist(prod)
                    st.toast(f"Saved \"{title}\" to your wishlist.", icon=":material/bookmark_added:")


def render_share_button(response_text: str, user_query: str, products, key: str):
    """Render a 'Share' button that snapshots this turn's response to a public read-only link."""
    if st.button("Share this recommendation", icon=":material/share:", key=f"share_{key}"):
        token = uuid.uuid4().hex
        Memory_Functions.store_shared_result(token, {
            "query": user_query,
            "response": response_text,
            "products": products,
        })
        try:
            base_url = st.context.url.split("?")[0]
        except Exception:
            base_url = "http://localhost:8501/"
        st.code(f"{base_url}?share={token}", language=None)


def attach_reasons(products, product_reasons):
    """Merge structured 'why this' text onto each product dict so it survives history redraws."""
    if not product_reasons:
        return products
    merged = []
    for p in products:
        if isinstance(p, dict):
            p = dict(p)
            p["why"] = product_reasons.get(p.get("title"))
        merged.append(p)
    return merged


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

if "last_products" not in st.session_state:
    st.session_state["last_products"] = []


# ============================ Sidebar ============================
with st.sidebar:
    st.markdown('<div class="tc-title" style="font-size:1.5rem;">Trust Cart AI</div>', unsafe_allow_html=True)
    st.caption("Your personal shopping assistant")

    st.markdown("##### :material/tune: Personality")
    optimization_goal = st.select_slider(
        "Optimize for",
        options=["Cheapest", "Balanced", "Highest Quality", "Most Sustainable"],
        value="Balanced",
        label_visibility="collapsed",
    )
    st.session_state["optimization_goal"] = optimization_goal

    gift_mode = st.toggle(":material/redeem: Shopping for someone else?", value=st.session_state.get("gift_mode", False))
    st.session_state["gift_mode"] = gift_mode

    if st.button("New chat", icon=":material/add:", width="stretch", type="primary", key="new_chat_btn"):
        new_thread_id = ThreadManager.generate_thread_id()
        st.session_state["thread_id"] = new_thread_id
        st.session_state["message_history"] = []
        st.session_state["waiting_for_questions"] = False
        st.session_state["pending_questions"] = []
        st.session_state["last_products"] = []

        if new_thread_id not in st.session_state["chat_threads"]:
            st.session_state["chat_threads"].insert(0, new_thread_id)

        st.rerun()

    st.markdown("##### :material/forum: Conversations")

    if st.session_state["chat_threads"]:
        for thread_id in st.session_state["chat_threads"]:
            preview = ThreadManager.get_thread_preview(thread_id, chatbot)
            is_current = thread_id == st.session_state["thread_id"]

            if st.button(
                preview,
                key=f"thread_{thread_id}",
                icon=":material/chat_bubble:" if is_current else ":material/chat_bubble_outline:",
                width="stretch",
                disabled=is_current,
                type="tertiary",
            ):
                st.session_state["thread_id"] = thread_id
                st.session_state["message_history"] = load_thread_history(thread_id)
                st.session_state["waiting_for_questions"] = False
                st.session_state["pending_questions"] = []
                st.rerun()
    else:
        st.caption("No conversations yet — start one below.")

    with st.expander("Wishlist", icon=":material/favorite:"):
        wishlist_items = Memory_Functions.get_wishlist()
        if not wishlist_items:
            st.caption("No saved products yet — tap Save on any recommendation.")
        else:
            for item in wishlist_items:
                with st.container(border=True):
                    product = item.get("product", {})
                    title = product.get("title", "Product")
                    price = product.get("price")
                    st.markdown(f"**{title}**" + (f"  ·  ${price:.2f}" if price else ""))
                    wl_cols = st.columns([3, 1])
                    with wl_cols[0]:
                        if product.get("url"):
                            st.link_button("View", product["url"], icon=":material/open_in_new:", width="stretch", key=f"wl_view_{item['key']}")
                    with wl_cols[1]:
                        if st.button("", icon=":material/delete:", key=f"wl_remove_{item['key']}", help="Remove from wishlist"):
                            Memory_Functions.remove_from_wishlist(item["key"])
                            st.rerun()

    st.caption(f":material/tag: {st.session_state['thread_id'][:8]}")


# ============================ Main Chat ============================
header_col1, header_col2 = st.columns([6, 1], vertical_alignment="center")

with header_col1:
    st.markdown('<p class="tc-title">🛒 Trust Cart AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="tc-subtitle">Tell me what you\'re looking for — I\'ll ask a few questions and find it.</p>', unsafe_allow_html=True)

with header_col2:
    with st.popover("", icon=":material/more_vert:", width="stretch"):
        if st.button("Delete chat", icon=":material/delete:", key="delete_current_chat", type="primary", width="stretch"):
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
for i, message in enumerate(st.session_state["message_history"]):
    # Check if it's a Q&A table format
    if message["role"] == "assistant" and message.get("type") == "qa_table":
        with st.chat_message("assistant"):
            st.markdown("**Your answers**")
            with st.container(border=True):
                for qa in message["content"]:
                    st.caption(qa["question"])
                    st.markdown(f":green[**{qa['answer']}**]")
    else:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("products"):
                render_product_gallery(message["products"], f"hist_{i}", st.session_state["thread_id"])
                prior_query = ""
                for prev in reversed(st.session_state["message_history"][:i]):
                    if prev["role"] == "user":
                        prior_query = prev["content"]
                        break
                render_share_button(message["content"], prior_query, message["products"], f"hist_{i}")


# Handle questions inline
if st.session_state.get("waiting_for_questions", False):
    questions = st.session_state["pending_questions"]
    with st.chat_message("assistant"):
        with st.container(border=True):
            icon_col, text_col = st.columns([1, 10], vertical_alignment="center")
            with icon_col:
                st.markdown(":material/checklist:")
            with text_col:
                st.markdown("**A few quick questions**")
                st.caption("Answer what you can — the more I know, the better the match.")

        with st.form(key=f"hitl_form_{st.session_state['thread_id']}"):
            collected_answers = {}
            for i, question in enumerate(questions, 1):
                q_col1, q_col2 = st.columns([1, 20], vertical_alignment="top")
                with q_col1:
                    st.badge(str(i), color="violet")
                with q_col2:
                    st.markdown(question)
                answer = st.text_input(
                    label=f"Answer {i}",
                    placeholder="Your answer...",
                    key=f"hitl_q_{i}_{st.session_state['thread_id']}",
                    label_visibility="collapsed"
                )
                if answer.strip():
                    collected_answers[question] = answer.strip()

            col1, col2 = st.columns(2)
            with col1:
                submit_clicked = st.form_submit_button(
                    f"Submit {len(questions)} answers",
                    icon=":material/check_circle:",
                    type="primary",
                    width="stretch"
                )
            with col2:
                skip_clicked = st.form_submit_button(
                    "Skip all",
                    icon=":material/skip_next:",
                    width="stretch"
                )

        # Process submission outside the form
        if submit_clicked or skip_clicked:
            if skip_clicked:
                # User skipped all questions - pass a flag so supervisor doesn't loop back
                collected_answers = {"skipped": True}
                qa_pairs = [{"question": "Did you answer the questions?", "answer": "No, skipped."}]
                st.session_state["message_history"].append({
                    "role": "assistant",
                    "type": "qa_table",
                    "content": qa_pairs
                })
                Memory_Functions.add_recent_message(
                    AIMessage(content="Questions & Answers:\nUser skipped answering the questions."),
                    st.session_state["thread_id"]
                )
            else:
                # Allow partial answers — only require at least 1 answered
                if len(collected_answers) == 0:
                    st.warning("Please answer at least one question or click Skip.", icon=":material/warning:")
                    st.stop()
                    
                # Store Q&A as table in chat history (only answered questions)
                qa_pairs = [{"question": q, "answer": a} for q, a in collected_answers.items()]
                st.session_state["message_history"].append({
                    "role": "assistant",
                    "type": "qa_table",
                    "content": qa_pairs
                })
                
                # Store in STM memory
                qa_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in collected_answers.items()])
                Memory_Functions.add_recent_message(
                    AIMessage(content=f"Questions & Answers:\n{qa_text}"),
                    st.session_state["thread_id"]
                )
                
            CONFIG = st.session_state["pending_config"]
                
            # Show thinking spinner
            with st.spinner("Finding the best products for you..."):
                try:
                    result = chatbot.invoke(Command(resume=collected_answers), CONFIG)
                    
                    if result.get("final_output"):
                        response = result["final_output"].get("response", "No response")
                        products = result["final_output"].get("products", [])
                        product_reasons = result["final_output"].get("product_reasons", {})
                        products = attach_reasons(products, product_reasons)

                        st.session_state["message_history"].append({
                            "role": "assistant",
                            "content": response,
                            "products": products
                        })

                        Memory_Functions.add_recent_message(
                            AIMessage(content=response),
                            st.session_state["thread_id"]
                        )

                        # Store product images in session for re-render
                        st.session_state["last_products"] = products

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
                                st.warning("The agent has more questions.", icon=":material/help:")
                                st.session_state["pending_questions"] = new_interrupts[0].value
                                st.rerun()

                        # Fallback: Logic finished but no response?
                        st.warning("Processing complete but no response generated.", icon=":material/warning:")
                        st.session_state["waiting_for_questions"] = False
                        st.rerun()
                except Exception as e:
                    st.error(str(e), icon=":material/error:")
                    log_error(st.session_state["thread_id"], "Streamlit Resumption", e)


# Voice input
if not st.session_state.get("waiting_for_questions", False):
    mic_row = st.container(horizontal=True)
    with mic_row:
        transcript = speech_to_text(
            start_prompt="🎤 Record",
            stop_prompt="⏹️ Stop",
            just_once=True,
            language="en",
            key="voice_recorder",
        )
    if transcript:
        st.session_state["voice_query"] = transcript

# Chat input
if not st.session_state.get("waiting_for_questions", False):
    typed_input = st.chat_input("Ask about anything you'd like to buy...")
    voice_query = st.session_state.pop("voice_query", None)
    user_input = typed_input or voice_query

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
                                    "generated_questions": [],
                                    "optimization_goal": st.session_state.get("optimization_goal", "Balanced"),
                                    "is_gift": st.session_state.get("gift_mode", False)
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
                            
                            # ── Interrupt detection (fixed: was using str() truthiness) ──
                            current_graph_state = chatbot.get_state(CONFIG)
                            if current_graph_state.next and len(current_graph_state.tasks) > 0:
                                interrupts = current_graph_state.tasks[0].interrupts
                                if interrupts and len(interrupts) > 0:
                                    questions = interrupts[0].value
                                    if isinstance(questions, list) and len(questions) > 0:
                                        st.session_state["waiting_for_questions"] = True
                                        st.session_state["pending_questions"] = questions
                                        st.session_state["pending_config"] = CONFIG
                                        st.rerun()

                    # ── Display AI text response ──
                    if result.get("final_output"):
                        response_text = result["final_output"].get("response", "No response")
                        products = result["final_output"].get("products", [])
                        product_reasons = result["final_output"].get("product_reasons", {})
                        products = attach_reasons(products, product_reasons)

                        with response_placeholder.container():
                            st.markdown(response_text)
                            render_product_gallery(products, f"live_{st.session_state['thread_id']}", st.session_state["thread_id"])
                            render_share_button(response_text, user_input, products, f"live_{st.session_state['thread_id']}")

                        st.session_state["message_history"].append({
                            "role": "assistant",
                            "content": response_text,
                            "products": products
                        })

                        Memory_Functions.add_recent_message(
                            AIMessage(content=response_text),
                            st.session_state["thread_id"]
                        )
                        log_chat_response(st.session_state["thread_id"], response_text)
                    else:
                        response_placeholder.warning("No response generated.", icon=":material/warning:")

                except Exception as e:
                    response_placeholder.error(str(e), icon=":material/error:")
                    log_error(st.session_state["thread_id"], "Streamlit Chat Processing", e)
                    with st.expander("Details", icon=":material/bug_report:"):
                        import traceback
                        st.code(traceback.format_exc())

        except Exception as e:
            st.error(f"Error processing message: {str(e)}", icon=":material/error:")
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



