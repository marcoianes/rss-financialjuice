from flask import Flask, Response
import requests
from bs4 import BeautifulSoup
import datetime

app = Flask(__name__)

def get_tweets():
    url = "https://nitter.poast.org/financialjuice"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.find_all("div", class_="timeline-item")
    
    tweets = []
    for item in items[:25]:
        content = item.find("div", class_="tweet-content").text.strip()
        link = "https://x.com" + item.find("a", {"href": True})["href"]
        date_tag = item.find("span", class_="tweet-date")
        pub_date = date_tag["title"] if date_tag and "title" in date_tag.attrs else ""
        try:
            pub_date = datetime.datetime.strptime(pub_date, "%Y-%m-%d %H:%M:%S %Z").strftime("%a, %d %b %Y %H:%M:%S +0000")
        except:
            pub_date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
        tweets.append((content, link, pub_date))
    return tweets

@app.route("/rss")
def rss_feed():
    tweets = get_tweets()
    rss_items = ""
    for tweet in tweets:
        title, link, pub_date = tweet
        rss_items += f"""
        <item>
            <title>{title}</title>
            <link>{link}</link>
            <pubDate>{pub_date}</pubDate>
        </item>
        """
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
    <channel>
        <title>FinancialJuice Feed</title>
        <link>https://x.com/financialjuice</link>
        <description>Tweets from FinancialJuice</description>
        {rss_items}
    </channel>
    </rss>"""
    return Response(rss, mimetype='application/rss+xml')

@app.route("/")
def home():
    return "Vai su /rss per vedere il feed RSS di FinancialJuice"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
