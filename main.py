from google.cloud import bigquery
import pdfplumber
import requests
from openai import OpenAI
from rss_generator import create_rss_feed
import os
import io

# Load API keys
from config import OPENAI_API_KEY

# Initialize OpenAI
OpenAI.api_key = OPENAI_API_KEY

# Initialize BigQuery client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/Paolo/Library/Mobile Documents/com~apple~CloudDocs/LexFind_it/GCP/private_keys/R_Metadata_BQ/taxfinder-mvp-534c73e834c1.json"
client = bigquery.Client()

def fetch_documents():
    """Get new tax documents from BigQuery"""
    query = """
        SELECT title, url, original_summary, upload_date
        FROM `taxfinder-mvp.sources_metadata.documents_agenzia_entrate`
        -- WHERE upload_date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
        WHERE upload_date >= TIMESTAMP_SUB('2024-11-20', INTERVAL 1 DAY)
        ORDER BY upload_date DESC
        LIMIT 1
    """
    return [dict(row) for row in client.query(query).result()]

def extract_text_from_pdf(pdf_url):
    """Downloads a PDF from a URL and extracts text."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with pdfplumber.open(io.BytesIO(response.content)) as pdf:
                # Extract text from the first few pages (to avoid huge documents)
                text = "\n".join([page.extract_text() for page in pdf.pages[:3] if page.extract_text()])
                return text.strip() if text else "No text extracted."
        else:
            return "Failed to download PDF."
    except Exception as e:
        return f"Error processing PDF: {e}"

def generate_summary(text, original_summary):
    """Summarize the document using OpenAI"""

    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""
    Sei un esperto di diritto tributario italiano. Ti fornisco il testo di un documento fiscale ufficiale e il suo riassunto originale.

    - **Testo estratto dal documento**: {text}
    - **Riassunto originale**: {original_summary}

    Genera un post linkedin con un riassunto chiaro e sintetico in italiano, adatto a professionisti fiscali (avvocati tributaristi, commercialisti, consulenti del lavoro).
    Il post deve avere la seguente struttura:
    - **novità normative** introdotte dal documento.
    - **implicazioni pratiche** per aziende e professionisti.

    Mantenere un tono tecnico ma leggibile e evitare ridondanze e informazioni inutili. Usa emoticon per aumentare la leggibilità.

    Struttura il riassunto con un **breve titolo** che riassuma il tema principale e 2-3 frasi di spiegazione.
    """

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Sei un esperto di diritto tributario italiano."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

# Main execution
if __name__ == "__main__":
    documents = fetch_documents()
    for doc in documents:
        pdf_text = extract_text_from_pdf(doc["url"])
        doc["ai_summary"] = generate_summary(pdf_text, doc["original_summary"])
        print(f"✅ {doc['title']}\n{doc['ai_summary']}\n")

    # ✅ Generate the RSS feed
    create_rss_feed(documents)
