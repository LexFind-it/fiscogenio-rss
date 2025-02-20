# Deploys RSS feed online

from flask import Flask, send_file

app = Flask(__name__)

@app.route('/rss')
def rss_feed():
    """Serve the RSS feed file"""
    return send_file("feed.xml", mimetype="application/rss+xml")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
