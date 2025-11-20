import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env.local if it exists
env_local = Path(__file__).resolve().parents[1] / ".env.local"
if env_local.exists():
    load_dotenv(env_local)

USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://localhost:3203/users")