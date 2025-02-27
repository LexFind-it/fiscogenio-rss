from PIL import Image, ImageDraw, ImageFont
import textwrap
import random
import os
import openai
import datetime
# Load API keys
from config import OPENAI_API_KEY

# Ensure paths to assets
BASE_DIR = os.path.dirname(__file__)

FONT_PATH_REG = os.path.join(BASE_DIR, "assets", "Poppins-Regular.ttf")
FONT_PATH_BOLD = os.path.join(BASE_DIR, "assets", "Poppins-Bold.ttf")

# Verify font file exists
if not os.path.exists(FONT_PATH_REG):
    raise FileNotFoundError(f"Font file not found: {FONT_PATH_REG}")
if not os.path.exists(FONT_PATH_BOLD):
    raise FileNotFoundError(f"Font file not found: {FONT_PATH_BOLD}")

LOGO_PATH_BLUE = os.path.join(BASE_DIR, "assets", "logo_blue.png")
LOGO_PATH_GREEN= os.path.join(BASE_DIR, "assets", "logo_green.png")
LOGO_PATH_SKY_BLUE = os.path.join(BASE_DIR, "assets", "logo_sky_blue.png")

# Verify logo file exists
if not os.path.exists(LOGO_PATH_BLUE):
    raise FileNotFoundError(f"Logo file not found: {LOGO_PATH_BLUE}")
if not os.path.exists(LOGO_PATH_GREEN):
    raise FileNotFoundError(f"Logo file not found: {LOGO_PATH_GREEN}")
if not os.path.exists(LOGO_PATH_SKY_BLUE):
    raise FileNotFoundError(f"Logo file not found: {LOGO_PATH_SKY_BLUE}")

# List of tuples Background Font Colors
COLORS_COMB = [("#224394","#6bf292", LOGO_PATH_SKY_BLUE), # "Dark Blue", "Light Green"
               ("#6bf292","#224394", LOGO_PATH_SKY_BLUE), # "Light Green", "Dark Blue"
               ("#f4e45f","#224394", LOGO_PATH_BLUE ), # "Yellow", "Dark Blue"
               ("#ecf4ff","#224394", LOGO_PATH_SKY_BLUE), # "Very Light Blue", "Dark Blue"
               ("#4894ff","#ecf4ff", LOGO_PATH_GREEN),  # "Sky Blue", "Very Light Blue"
               ("#224394","#ecf4ff", LOGO_PATH_SKY_BLUE)  # "Dark Blue", "Very Light Blue"
               ]

if not OPENAI_API_KEY:
    print("❌ OpenAI API Key is missing! Set the OPENAI_API_KEY environment variable.")
    exit(1)

# Load API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_short_claim(summary, model="gpt-4-turbo", max_tokens=50):
    """
    Generates a short, impactful claim summarizing the key news for a social media post.

    Parameters:
    - summary (str): The AI-generated summary of the document.
    - model (str): The OpenAI model to use.
    - max_tokens (int): The maximum number of tokens for the output.

    Returns:
    - str: A concise, engaging claim.
    """
    prompt = (
        "Crea un claim brevissimo e d'impatto (max 10 parole). No virgolette, no hashtag. Il deve essere inserito in un immagine instagram. Basa il claim su questo riassunto: \n"
        f"""{summary}"""
    )

    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "system", "content": "Sei un copywriter esperto in comunicazione fiscale."},
                  {"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.3
    )

    claim = response["choices"][0]["message"]["content"].strip()

    # Ensure the claim does not start or end with quotes and is not truncated
    return claim.strip('"')

def generate_social_image(text, source, output_path="output_image.png"):
    """Genera un'immagine con testo e fonte per LinkedIn/Instagram"""

    # Scegli una coppia di colori casuale dalla palette
    colors = random.sample(COLORS_COMB, 1)[0]
    bg_color, font_color,LOGO_PATH = colors

    # Crea una nuova immagine
    img = Image.new("RGB", (1080, 1080), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Carica il font
    font = ImageFont.truetype(FONT_PATH_REG, 38)
    font_bold = ImageFont.truetype(FONT_PATH_BOLD, 80)

    # Wrappa il testo in più righe
    wrapped_text = textwrap.fill(text, width=20)

    # Posiziona il testo centrato
    text_x, text_y = 100, 340
    draw.text((text_x, text_y), wrapped_text, font=font_bold, fill=font_color)

    # Aggiungi la fonte in piccolo
    source_text = source
    draw.text((100, 900), source_text, font=font, fill=font_color)

    # Carica e posiziona il logo
    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo = logo.resize((810, 160))  # Resize se necessario
        img.paste(logo, (30, 80), logo)

    # Salva l'immagine
    img.save(output_path)
    return output_path



test = {'title': 'Risposta n. 49 del 25/02/2025',
 'url': 'https://www.agenziaentrate.gov.it/portale/documents/20143/8473268/Risposta+n.+49_2025.pdf/881172f1-9bc2-c8a1-9447-9287fd2c3ece?t=1740496787713',
 'original_summary': "Soggetto aderente al regime di adempimento collaborativo – Regime di esenzione dalla ritenuta sugli interessi corrisposti a controllante Svizzera, in assenza dell'holding period, ai sensi dell'articolo 9 dell'Accordo tra la Comunità Europea e la Confederazione svizzera, siglato il 26 ottobre 2004",
 'upload_date': datetime.datetime(2025, 2, 26, 0, 56, 38, 395107, tzinfo=datetime.timezone.utc),
 'ai_summary': "📢 Regime di esenzione da ritenuta sugli interessi corrisposti a controllante Svizzera\n\n⚖️ L'Agenzia delle Entrate ha chiarito che è possibile applicare l'esenzione dalla ritenuta sugli interessi corrisposti da una società italiana a una controllante svizzera, anche in assenza del requisito di holding period, ai sensi dell'articolo 9 dell'Accordo del 2004.\n\n💼 Implicazioni pratiche? Le aziende devono verificare il rispetto dei requisiti previsti dalla normativa per beneficiare di tale esenzione, agevolando transazioni infragruppo con operatori svizzeri.\n\n#Fisco #Tasse #AccordoSvizzera #DirittoTributario #Interessi #HoldingPeriod #AgenziaDelleEntrate"}

# Main execution
if __name__ == "__main__":
    generated_claim = generate_short_claim(test['ai_summary'])
    source = test['title']

    img_path = generate_social_image(generated_claim,f"Agenzia delle Entrate: \n{source}", "img/post_image_test.png")
    print(img_path)
