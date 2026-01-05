FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY newton_supercomputer.py .
COPY core/ ./core/
COPY tinytalk_py/ ./tinytalk_py/
COPY newton_sdk/ ./newton_sdk/
COPY parccloud/ ./parccloud/
COPY frontend/ ./frontend/

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "newton_supercomputer:app", "--host", "0.0.0.0", "--port", "8000"]
