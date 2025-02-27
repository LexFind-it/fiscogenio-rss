# Generates the RSS feed

import shutil
import datetime
import os
import re
from post_image import generate_social_image, generate_short_claim

RSS_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
    <channel>
        <title>FiscoGenio AI - Tax News</title>
        <link>https://www.fiscogenio.ai/rss</link>
        <description>Latest updates from Agenzia delle Entrate</description>
        <lastBuildDate>{last_build}</lastBuildDate>
        {items}
    </channel>
</rss>"""

ITEM_TEMPLATE = """
    <item>
        <title>{title}</title>
        <link>{link}</link>
        <description>{description}</description>
        <pubDate>{pub_date}</pubDate>
        <enclosure url="{image_url}" type="image/png" />
    </item>
"""

def create_rss_feed(articles, output_file="feed.xml"):
    """Genera un file RSS con gli articoli passati come lista di dizionari"""
    # Elimina e ricrea la cartella public/img
    img_dir = "public/img"
    if os.path.exists(img_dir):
        shutil.rmtree(img_dir)
    os.makedirs(img_dir)

    last_build = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    items = ""

    for article in articles:
        # Genera il claim e l'immagine
        claim = generate_short_claim(article["ai_summary"])
        image_filename = re.sub(r'[^\w\-_\.]', '_', f"{article['title']}.png")
        image_path = generate_social_image(claim, f"Agenzia delle Entrate: \n{article['title']}", f"public/img/{image_filename}")
        image_url = f"https://github.com/PaoloPiacenti/lexfindit/fiscogenio_rss/public/img/{image_filename}"
        #image_url = f"http://localhost:8000/public/img/{image_filename}" # Localhost testing

        items += ITEM_TEMPLATE.format(
            title=article["title"],
            link=article["url"],
            description=article["ai_summary"],
            pub_date=datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
            image_url=image_url
        )

    rss_content = RSS_TEMPLATE.format(last_build=last_build, items=items)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rss_content)

    print(f"✅ RSS feed generated: {output_file}")
