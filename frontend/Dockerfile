FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Hugging Face Spaces runs as non-root user uid=1000
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 7860

# BACKEND_URL env var must be set to the backend Space's URL
ENV BACKEND_URL=https://phaniaigeek-superkart-sales-api.hf.space

CMD ["streamlit", "run", "app.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
