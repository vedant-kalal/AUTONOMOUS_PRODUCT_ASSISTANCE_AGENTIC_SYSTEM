#!/bin/bash

# Streamlit Multi-Thread Chatbot Launcher

# Resolve script directory so this works from any CWD
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"
VENV_STREAMLIT="$SCRIPT_DIR/.venv/bin/streamlit"

echo "🛍️  Product Assistant Streamlit App"
echo "==================================="
echo ""
echo "Starting Streamlit chatbot with multi-thread support..."
echo ""

# Verify venv exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment not found at $SCRIPT_DIR/.venv"
    echo "Run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Make sure PostgreSQL is running
echo "⚙️  Checking PostgreSQL connection..."
"$VENV_PYTHON" -c "from app_backend.helper import get_checkpointer_helper; get_checkpointer_helper()" || {
    echo "❌ Error: PostgreSQL connection failed!"
    echo "Please make sure PostgreSQL is running and accessible."
    exit 1
}

echo ""
echo "✅ All checks passed!"
echo ""
echo "🚀 Launching Streamlit app..."
echo ""

# Run Streamlit using the venv's binary
"$VENV_STREAMLIT" run "$SCRIPT_DIR/streamlit_app.py"
