# Deploys RSS feed online

from flask import Flask, send_file, send_from_directory

app = Flask(__name__)

@app.route('/rss')
def rss_feed():
    """Serve the RSS feed file"""
    return send_file("feed.xml", mimetype="application/rss+xml")

@app.route('/public/img/<path:filename>')
def serve_image(filename):
    """Serve images from the public/img directory"""
    return send_from_directory('public/img', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
