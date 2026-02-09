#!/bin/bash

# Streamlit Multi-Thread Chatbot Launcher

echo "🛍️  Product Assistant Streamlit App"
echo "==================================="
echo ""
echo "Starting Streamlit chatbot with multi-thread support..."
echo ""

# Make sure PostgreSQL is running
echo "⚙️  Checking PostgreSQL connection..."
python -c "from app_backend.helper import get_checkpointer_helper; get_checkpointer_helper()" || {
    echo "❌ Error: PostgreSQL connection failed!"
    echo "Please make sure PostgreSQL is running and accessible."
    exit 1
}

echo ""
echo "✅ All checks passed!"
echo ""
echo "🚀 Launching Streamlit app..."
echo ""

# Run Streamlit
streamlit run streamlit_app.py
