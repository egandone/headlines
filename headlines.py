import os
import feedparser
from flask import Flask
from flask import send_from_directory

app = Flask(__name__)

RSS_FEEDS = {
	'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
	'cnn': 'http://rss.cnn.com/rss/edition.rss',
	'fox': 'http://feeds.foxnews.com/foxnews/latest',
	'iol': 'http://www.iol.co.za/cmlink/1.640'} 
						

# Get port from environment variable or choose 9099 as local default
port = int(os.getenv("PORT", 5000))

@app.route("/")
@app.route("/<publication>")
def bbc(publication='bbc'):
	return get_news(publication)

@app.route('/favicon.ico')
def favicon():
	print(app.root_path)
	return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

def get_news(publication):
	feed = feedparser.parse(RSS_FEEDS[publication])
	first_article = feed['entries'][0]
	return """<html>
	<body>
		<h1>Headlines</h1>
		<b>{0}</b><br/>
		<i>{1}</i><br/>
		<p>{2}</p><br/>
	</body>
	</html>""".format(first_article.get("title"), first_article.get("published"), first_article.get("summary"))
	
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=port, debug=False)

