from google.cloud import bigquery
import pdfplumber
import requests
from rss_generator import create_rss_feed
import os
import io
import openai

# Load API keys
from config import OPENAI_API_KEY

if not OPENAI_API_KEY:
    print("❌ OpenAI API Key is missing! Set the OPENAI_API_KEY environment variable.")
    exit(1)

# Load API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize BigQuery client
# Get credentials from environment (set by GitHub Actions)
BIGQUERY_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")

# Debugging: Check if the credentials file exists
if not os.path.exists(BIGQUERY_CREDENTIALS_PATH):
    print(f"❌ Credentials file not found: {BIGQUERY_CREDENTIALS_PATH}")
    exit(1)

print(f"✅ Using Google credentials from: {BIGQUERY_CREDENTIALS_PATH}")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = BIGQUERY_CREDENTIALS_PATH
client = bigquery.Client()

def fetch_documents():
    """Get new tax documents from BigQuery"""
    query = """
        SELECT title, url, original_summary, upload_date
        FROM `tuo_progetto.tuo_dataset.tua_tabella`
        WHERE DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY) =
            PARSE_DATE('%d/%m/%Y', REGEXP_EXTRACT(title, r'(\d{2}/\d{2}/\d{4})'))
        ORDER BY PARSE_DATE('%d/%m/%Y', REGEXP_EXTRACT(title, r'(\d{2}/\d{2}/\d{4})')) DESC
    """
    return [dict(row) for row in client.query(query).result()]

def extract_text_from_pdf(pdf_url):
    """Downloads a PDF from a URL and extracts text."""
    try:
        response = requests.get(pdf_url)
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

    prompt = f"""
    Sei un esperto di diritto tributario italiano. Ti fornisco il testo di un documento fiscale ufficiale e il suo riassunto originale.

    - **Testo estratto dal documento**: {text}
    - **Riassunto originale**: {original_summary}

    🔎 **Obiettivo:**
    Genera un post LinkedIn chiaro e sintetico in italiano, adatto a professionisti fiscali (avvocati tributaristi, commercialisti, consulenti del lavoro).

    📝 **Struttura del post:**
    1️⃣ **Titolo breve e chiaro** (senza formattazione Markdown).
    2️⃣ **Novità normative** introdotte dal documento (usa una frase breve e diretta).
    3️⃣ **Implicazioni pratiche** per aziende e professionisti.
    4️⃣ **Aggiungi hashtag automatici** su parole chiave rilevanti, come concetti fiscali, leggi, enti e settori interessati.


    ✅ **Regole di stile:**
    - Scrivi in modo chiaro e leggibile, evitando un linguaggio troppo tecnico.
    - Usa emoji per migliorare la leggibilità (📌⚖️💼).
    - Evita ripetizioni e informazioni superflue.
    - Aggiungi **hashtag automatici** sulle parole chiave più importanti (es. #Fisco, #Tasse, #IVA, #LeggeBilancio).
    - Formatta il testo con spaziature per renderlo leggibile su LinkedIn.

    🎯 **Esempio di output desiderato:**

    📢 Nuove regole fiscali per le plusvalenze sui metalli preziosi

    ⚖️ L' #AgenziaDelleEntrate ha chiarito che anche il #palladio è considerato un metallo prezioso ai fini fiscali.

    🪙 Cosa cambia? Le plusvalenze dalla vendita di palladio saranno soggette a un'imposta del 26%.

    💼 Cosa significa per te? I professionisti del settore devono includere il palladio nella pianificazione fiscale.

    Scrivi il post seguendo questa struttura e stile.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Sei un esperto di diritto tributario italiano che gestisce una pagina linkedin."},
            {"role": "user", "content": prompt}
        ],
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
