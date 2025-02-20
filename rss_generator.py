# Generates the RSS feed

import datetime

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
    </item>
"""

def create_rss_feed(articles, output_file="feed.xml"):
    """Genera un file RSS con gli articoli passati come lista di dizionari"""
    last_build = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    items = ""

    for article in articles:
        items += ITEM_TEMPLATE.format(
            title=article["title"],
            link=article["url"],
            description=article["ai_summary"],
            pub_date=datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        )

    rss_content = RSS_TEMPLATE.format(last_build=last_build, items=items)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rss_content)

    print(f"✅ RSS feed generated: {output_file}")
