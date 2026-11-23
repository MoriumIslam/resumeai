import os

# Get the absolute path to the project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Configure upload folder as absolute path
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "uploads")
ALLOWED_EXTENSIONS = {"pdf"}

OPENAI_API_KEY = "your_api_key_here"  # optional