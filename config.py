import os
from dotenv import load_dotenv

# Load environmental variables from .env file in parent or current directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

# Determine if we should run in mock mode
# Mock mode is active if credentials are empty or contain placeholder text
IS_MOCK_MODE = False
if (
    not SUPABASE_URL 
    or not SUPABASE_KEY 
    or "your-project-id" in SUPABASE_URL 
    or "your-supabase" in SUPABASE_KEY
):
    IS_MOCK_MODE = True

print("=" * 60)
print(f"MandiGrown Server Mode: {'[MOCK FALLBACK MODE]' if IS_MOCK_MODE else '[REAL SUPABASE MODE]'}")
if IS_MOCK_MODE:
    print("Running with local memory state. No Supabase configuration detected.")
else:
    print(f"Connecting to Supabase at: {SUPABASE_URL}")
print("=" * 60)
