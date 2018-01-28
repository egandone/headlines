import os
import feedparser
import json
import urllib.request
from flask import Flask
from flask import send_from_directory
from flask import render_template
from flask import request

open_weather_map_apikey = '8fc0349f33ab53f5381af6bddb741586'

RSS_FEEDS = {
  'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
  'cnn': 'http://rss.cnn.com/rss/edition.rss',
  'fox': 'http://feeds.foxnews.com/foxnews/latest',
  'iol': 'http://www.iol.co.za/cmlink/1.640'}

DEFAULTS = {'publication':'bbc',
            'city':'Toronto,CA'}

app = Flask(__name__)


# Get port from environment variable or choose 9099 as local default
port = int(os.getenv("PORT", 5000))

@app.route("/")
def get_news():
  publication = get_arg("publication", RSS_FEEDS).lower()
  feed = feedparser.parse(RSS_FEEDS[publication])
  city = get_arg("city")
  weather = get_weather(city)
  return render_template("home.html", feed=publication, articles=feed['entries'], weather=weather)

def get_arg(name, valid_opts=None):
  arg = request.args.get(name)
  if not arg or (valid_opts and arg.lower() not in valid_opts):
    arg = DEFAULTS[name]
  return arg

@app.route('/favicon.ico')
def favicon():
  print(app.root_path)
  return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

def get_weather(query):
  api_url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}'
  query = urllib.request.quote(query)
  url = api_url.format(query, open_weather_map_apikey)
  response_bytes = urllib.request.urlopen(url, timeout=1).read()
  response_dict = json.loads(response_bytes)
  weather = None
  if response_dict.get("weather"):
    weather = {"description":response_dict["weather"][0]["description"],
      "temperature":response_dict["main"]["temp"],
      "city":response_dict["name"],
      "country":response_dict["sys"]["country"]}
  return weather

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=port, debug=False)

