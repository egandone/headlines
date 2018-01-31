import os
import feedparser
import json
import datetime
import urllib.request
from flask import Flask
from flask import send_from_directory
from flask import render_template
from flask import request
from flask import make_response

open_weather_map_apikey = '8fc0349f33ab53f5381af6bddb741586'
OPEN_WEATHER_MAP_URL = 'http://api.openweathermap.org/data/2.5/weather?appid={}&units=metric'.format(open_weather_map_apikey)
open_exchange_apikey = '72418b2c9f5e429f8ebe531076f6fbe5'
OPEN_EXCHANGE_URL = 'https://openexchangerates.org/api/latest.json?app_id={}'.format(open_exchange_apikey)

RSS_FEEDS = {
  'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
  'cnn': 'http://rss.cnn.com/rss/edition.rss',
  'fox': 'http://feeds.foxnews.com/foxnews/latest',
  'iol': 'http://www.iol.co.za/cmlink/1.640'}

DEFAULTS = {'publication':'bbc',
            'city':'Toronto,CA',
            'currency_from':'CAD',
            'currency_to':'USD'}

app = Flask(__name__)


# Get port from environment variable or choose 9099 as local default
port = int(os.getenv("PORT", 5000))

@app.route("/")
def home():
  publication = get_arg("publication", RSS_FEEDS).lower()
  feed = feedparser.parse(RSS_FEEDS[publication])
  city = get_arg("city")
  weather = get_weather(city)
  currency_from = get_arg("currency_from")
  currency_to = get_arg("currency_to")
  rate,currencies = get_rate(currency_from, currency_to)
  response = make_response(render_template("home.html", 
    feed=publication, 
    articles=feed['entries'], 
    weather=weather, 
    currency_from=currency_from, 
    currency_to=currency_to, 
    rate=rate, 
    currencies=sorted(currencies)))
  expires = datetime.datetime.now() + datetime.timedelta(days=30);
  response.set_cookie("publication", publication, expires=expires)
  response.set_cookie("city", city, expires=expires)
  response.set_cookie("currency_from", currency_from, expires=expires)
  response.set_cookie("currency_to", currency_to, expires=expires)
  return response

def get_arg(name, valid_opts=None):
  # Check the request parameters first for the argument
  arg = request.args.get(name)
  if not arg:
    # If the request parameter didn't have check the cookies
    arg = request.cookies.get(name)
    if not arg or (valid_opts and arg.lower() not in valid_opts):
      arg = DEFAULTS[name]
  return arg

@app.route('/favicon.ico')
def favicon():
  print(app.root_path)
  return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

def get_weather(query):
  api_url = OPEN_WEATHER_MAP_URL + '&q={}'
  query = urllib.request.quote(query)
  url = api_url.format(query)
  response_bytes = urllib.request.urlopen(url, timeout=1).read()
  response_string = response_bytes.decode("utf-8")
  response_dict = json.loads(response_string)
  weather = None
  if response_dict.get("weather"):
    weather = {"description":response_dict["weather"][0]["description"],
      "temperature":response_dict["main"]["temp"],
      "city":response_dict["name"],
      "country":response_dict["sys"]["country"]}
  return weather

def get_rate(currency_from, currency_to):
  all_currencies = urllib.request.urlopen(OPEN_EXCHANGE_URL).read()
  all_currencies = all_currencies.decode("utf-8")
  all_currencies = json.loads(all_currencies)
  rates = all_currencies["rates"]
  from_rate = rates[currency_from.upper()]
  to_rate = rates[currency_to.upper()]
  return (to_rate / from_rate, rates.keys())


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=port, debug=False)

