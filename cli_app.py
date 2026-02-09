#!/usr/bin/env python3
"""
CLI Application for Product Assistant Terminal Chat
Beautiful UI with Rich library - ChatGPT-style interface
"""

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command
from app.agents.workflow.final_workflow import app
from app.memory.memory_store import Memory_Functions
from app.schemas.states.agentic_state import AgentState

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich import box
from rich.theme import Theme
import pyfiglet
import sys
from io import StringIO

# Custom theme for the chatbot
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "user": "bold magenta",
    "assistant": "bold cyan",
})

console = Console(theme=custom_theme)


def show_banner():
    """Display the product assistant banner"""
    # Generate ASCII art logo
    logo_text = pyfiglet.figlet_format("AUTONOMOUS\nPRODUCT\nASSISTANT\nAGENT", font="slant")
    
    logo = Text(logo_text, style="bold cyan")
    
    # Create a beautiful panel
    panel = Panel(
        logo,
        title="[bold yellow]🛍️  AI Shopping Assistant  🛍️[/bold yellow]",
        subtitle="[italic]Your intelligent product finder[/italic]",
        border_style="bright_blue",
        box=box.DOUBLE,
        padding=(1, 2)
    )
    
    console.print(panel)
    console.print()


def run_terminal_chat():
    """Run the interactive terminal chat interface with Rich UI"""
    
    # Show banner
    show_banner()
    
    # Welcome message
    welcome_panel = Panel(
        "[bold green]Welcome![/bold green] 👋\n\n"
        "I'm your AI shopping assistant. I can help you:\n"
        "• Find products across multiple categories\n"
        "• Get personalized recommendations\n"
        "• Answer questions about products\n\n"
        "[dim italic]Type 'exit' or 'quit' to end the session[/dim italic]",
        border_style="green",
        box=box.ROUNDED
    )
    console.print(welcome_panel)
    console.print()
    
    # Clear short-term memory for fresh session
    Memory_Functions.clear_recent_messages()
    console.print("[dim]🧹 Cleared previous session memory[/dim]\n")

    current_intent = {}

    while True:
        # Show "You:" prompt and get input
        console.print("[bold magenta]You:[/bold magenta] ", end="")
        user_input = input()
        
        # Show user input in a special box
        user_panel = Panel(
            user_input,
            title="[bold magenta]👤 Your Message[/bold magenta]",
            border_style="magenta",
            box=box.ROUNDED,
            padding=(0, 1)
        )
        console.print(user_panel)
        console.print()
        
        if user_input.lower() in {"exit", "quit"}:
            console.print(Panel(
                "[bold yellow]👋 Thanks for chatting! Goodbye![/bold yellow]",
                border_style="yellow"
            ))
            break

        try:
            Memory_Functions.add_recent_message(
                HumanMessage(content=user_input)
            )

            state: AgentState = {
                "user_query": user_input,
                "original_user_query": user_input,
                "mode": None,
                "supervisor_decision": None,
                "final_output": None,
                "intent": current_intent,
                "collected_info": {}
            }

            # Capture debug output while processing
            debug_log = []
            
            # Invoke workflow with thread_id for checkpointer
            config = {"configurable": {"thread_id": "cli_session"}}
            
            with console.status("[bold cyan]🤔 Thinking...", spinner="dots"):
                # Capture all DEBUG output
                old_stdout = sys.stdout
                
                class DebugCapturer:
                    def write(self, text):
                        if text.strip():
                            debug_log.append(text.rstrip())
                    def flush(self):
                        pass
                
                sys.stdout = DebugCapturer()
                
                try:
                    result = app.invoke(state, config)
                finally:
                    sys.stdout = old_stdout
            
            # Check if workflow was interrupted (paused for questions)
            while "__interrupt__" in result:
                interrupts = result["__interrupt__"]
                
                if interrupts and len(interrupts) > 0:
                    interrupt_data = interrupts[0]
                    questions = interrupt_data.value
                    
                    # Show questions panel
                    questions_panel = Panel(
                        "[bold]I need some information to help you better:[/bold]\n",
                        title="[bold cyan]📋 Questions[/bold cyan]",
                        border_style="cyan",
                        box=box.ROUNDED
                    )
                    console.print(questions_panel)
                    
                    collected_info = {}
                    
                    # Ask each question one by one
                    for i, question in enumerate(questions, 1):
                        answer = Prompt.ask(f"[bold cyan]{i}. {question}[/bold cyan]")
                        collected_info[question] = answer
                        
                        Memory_Functions.add_recent_message(AIMessage(content=question))
                        Memory_Functions.add_recent_message(HumanMessage(content=answer))
                    
                    console.print()
                    
                    # Resume workflow
                    with console.status("[bold cyan]🔍 Processing your preferences...", spinner="dots"):
                        sys.stdout = DebugCapturer()
                        try:
                            result = app.invoke(Command(resume=collected_info), config)
                        finally:
                            sys.stdout = old_stdout
                else:
                    break
            
            # Update intent context
            if result.get("final_output"):
                current_intent = {}
            else:
                current_intent = result.get("intent", {})
            
            # Handle final output
            if result.get("final_output") is None:
                console.print("[warning]⚠️ No response generated[/warning]")
                continue
            
            final_output = result["final_output"]
            response = final_output.get("response", "No response generated")
            
            # Save AI response to memory
            Memory_Functions.add_recent_message(AIMessage(content=response))
            
            # Display response in a beautiful panel
            response_panel = Panel(
                Markdown(response),
                title="[bold cyan]🤖 Assistant[/bold cyan]",
                border_style="cyan",
                box=box.ROUNDED,
                padding=(1, 2)
            )
            console.print(response_panel)
            
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n")
            console.print(Panel(
                "[bold yellow]⚠️ Session interrupted. Goodbye![/bold yellow]",
                border_style="yellow"
            ))
            break
        except Exception as e:
            console.print(Panel(
                f"[error]❌ Error: {e}[/error]",
                title="[bold red]Error[/bold red]",
                border_style="red"
            ))
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")


if __name__ == "__main__":
    run_terminal_chat()
