# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if any needed for psycopg2 or others)
# libpq-dev is often needed for psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Healthcheck to ensure app is running
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Command to run the application
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]