import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env if running locally

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Save BigQuery credentials from the env variable
BIGQUERY_CREDENTIALS_PATH = "credentials.json"

if os.getenv("BIGQUERY_CREDENTIALS"):  # If running in GitHub Actions
    with open(BIGQUERY_CREDENTIALS_PATH, "w") as f:
        f.write(os.getenv("BIGQUERY_CREDENTIALS"))

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = BIGQUERY_CREDENTIALS_PATH
