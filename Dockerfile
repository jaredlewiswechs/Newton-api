FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY newton_supercomputer.py .
COPY core/ ./core/

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "newton_supercomputer:app", "--host", "0.0.0.0", "--port", "8000"]
