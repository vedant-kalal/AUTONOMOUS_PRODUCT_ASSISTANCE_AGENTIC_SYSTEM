@echo off
REM Streamlit Multi-Thread Chatbot Launcher (Windows)

echo.
echo 🛍️  Product Assistant Streamlit App
echo ===================================
echo.
echo Starting Streamlit chatbot with multi-thread support...
echo.

REM Check PostgreSQL connection
echo ⚙️  Checking PostgreSQL connection...
python -c "from app_backend.helper import get_checkpointer_helper; get_checkpointer_helper()"
if %errorlevel% neq 0 (
    echo.
    echo ❌ Error: PostgreSQL connection failed!
    echo Please make sure PostgreSQL is running and accessible.
    pause
    exit /b 1
)

echo.
echo ✅ All checks passed!
echo.
echo 🚀 Launching Streamlit app...
echo.

REM Run Streamlit
streamlit run streamlit_app.py
