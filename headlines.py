import os
import feedparser
from flask import Flask
from flask import send_from_directory
from flask import render_template
from flask import request

app = Flask(__name__)

RSS_FEEDS = {
	'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
	'cnn': 'http://rss.cnn.com/rss/edition.rss',
	'fox': 'http://feeds.foxnews.com/foxnews/latest',
	'iol': 'http://www.iol.co.za/cmlink/1.640'}


# Get port from environment variable or choose 9099 as local default
port = int(os.getenv("PORT", 5000))

@app.route("/", methods=['GET', 'POST'])
def get_news():
	query = request.form.get("publication")
	if not query or query.lower() not in RSS_FEEDS:
		query = 'bbc'
	publication = query.lower()
	feed = feedparser.parse(RSS_FEEDS[publication])
	return render_template("home.html", articles=feed['entries'])

@app.route('/favicon.ico')
def favicon():
	print(app.root_path)
	return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=port, debug=False)

