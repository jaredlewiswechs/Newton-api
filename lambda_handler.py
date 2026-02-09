"""
AWS Lambda entry point for Newton Supercomputer.

Uses Mangum to adapt the FastAPI ASGI app to AWS Lambda + API Gateway.
Supports both REST API Gateway (v1) and HTTP API Gateway (v2) payloads.
"""
import sys
import os
from pathlib import Path

# Ensure project root is on the import path
parent_dir = str(Path(__file__).parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Set environment marker so the app knows it's running on Lambda
os.environ.setdefault("AWS_EXECUTION_ENV", "AWS_Lambda_python3.11")

from mangum import Mangum  # noqa: E402
from newton_supercomputer import app  # noqa: E402

# Mangum wraps the FastAPI ASGI app for Lambda
# lifespan="off" avoids issues with Lambda's execution model
handler = Mangum(app, lifespan="off")
