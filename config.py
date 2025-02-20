import os
from dotenv import load_dotenv

# Load .env for local development
load_dotenv()

# Get OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set up Google Cloud Credentials
BIGQUERY_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = BIGQUERY_CREDENTIALS_PATH
