from flask import Flask, render_template, request, json
import pickle
import traceback
import numpy as np
import asyncio
import asyncpraw
from apify_client import ApifyClient
from playwright.sync_api import sync_playwright
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime
from dotenv import load_dotenv
import os


# --- Initial NLTK VADER Download ---
# The first time this runs, it will download the necessary lexicon.
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    print("Downloading VADER lexicon for sentiment analysis...")
    nltk.download('vader')
    print("Download complete.")

# ---------- Config ----------
MODEL_PATH = './content/model_nb.pkl'

load_dotenv()  # Loads variables from .env

REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')
APIFY_API_TOKEN = os.getenv('APIFY_API_TOKEN')


# Thresholds
THRESHOLD_ABNORMAL = 0.55

app = Flask(__name__)

# ---------- Load Model & Sentiment Analyzer ----------
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)
sia = SentimentIntensityAnalyzer()

# ---------- Helpers ----------
def get_class_indices():
    """Gets the index for the 'abnormal' class from the model."""
    if hasattr(model, "classes_"):
        classes = list(model.classes_)
        try:
            # Assuming '1' is the 'abnormal' class
            return classes.index(1)
        except ValueError:
            return 1 if len(classes) > 1 else 0
    return 1

IDX_ABNORMAL = get_class_indices()

def analyze_posts(posts):
    """
    Analyzes a list of post objects (dict with 'text' and 'timestamp').
    Returns detailed analysis for each post and aggregate results.
    """
    if not posts:
        return None

    analyzed_posts = []
    total_abnormal_prob = 0
    total_neg_sentiment = 0
    total_pos_sentiment = 0
    total_neu_sentiment = 0

    for post in posts:
        text = post.get('text', '')
        if not text:
            continue

        # 1. Mental Health Model Prediction
        try:
            proba = model.predict_proba([text])[0]
            prob_abnormal = float(proba[IDX_ABNORMAL])
        except Exception:
            prob_abnormal = 0.0

        # 2. Sentiment Analysis
        sentiment = sia.polarity_scores(text)

        analyzed_posts.append({
            'text': text,
            'prob_abnormal': prob_abnormal,
            'sentiment': sentiment,
            'timestamp': post.get('timestamp')
        })

        # Accumulate totals for averages
        total_abnormal_prob += prob_abnormal
        total_neg_sentiment += sentiment['neg']
        total_pos_sentiment += sentiment['pos']
        total_neu_sentiment += sentiment['neu']

    # Sort by timestamp for chronological graphing
    analyzed_posts.sort(key=lambda x: x['timestamp'])

    # Prepare data for the graph
    graph_labels = [datetime.fromtimestamp(p['timestamp']).strftime('%Y-%m-%d') for p in analyzed_posts]
    graph_abnormal_prob = [p['prob_abnormal'] for p in analyzed_posts]
    graph_neg_sentiment = [p['sentiment']['neg'] for p in analyzed_posts]

    # Calculate averages
    post_count = len(analyzed_posts)
    aggregates = {
        'avg_abnormal_prob': total_abnormal_prob / post_count if post_count > 0 else 0,
        'avg_neg_sentiment': total_neg_sentiment / post_count if post_count > 0 else 0,
        'avg_pos_sentiment': total_pos_sentiment / post_count if post_count > 0 else 0,
        'avg_neu_sentiment': total_neu_sentiment / post_count if post_count > 0 else 0,
        'post_count': post_count
    }
    
    # Determine overall verdict
    if aggregates['avg_abnormal_prob'] >= THRESHOLD_ABNORMAL:
        verdict = "High Concern"
    else:
        verdict = "Low Concern"

    return {
        'verdict': verdict,
        'posts': analyzed_posts,
        'aggregates': aggregates,
        'graph_data': {
            'labels': graph_labels,
            'abnormal_prob': graph_abnormal_prob,
            'neg_sentiment': graph_neg_sentiment
        }
    }

# ---------- Reddit Fetch ----------
async def fetch_user_comments_async(username, limit=20):
    posts = []
    async with asyncpraw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    ) as reddit:
        user = await reddit.redditor(username)
        async for comment in user.comments.new(limit=limit):
            posts.append({'text': comment.body, 'timestamp': comment.created_utc})
    return posts

def fetch_user_comments(username, limit=20):
    return asyncio.run(fetch_user_comments_async(username, limit))

# ---------- Instagram Fetch ----------
def fetch_instagram_captions(profile_input, limit=10):
    if not APIFY_API_TOKEN:
        raise RuntimeError("Apify API token is not set.")
    
    profile_url = f"https://www.instagram.com/{profile_input}/" if not profile_input.startswith("http") else profile_input
    
    client = ApifyClient(APIFY_API_TOKEN)
    run_input = {
        "directUrls": [profile_url], "resultsType": "posts", "resultsLimit": limit,
    }
    run = client.actor("apify/instagram-scraper").call(run_input=run_input)
    
    posts = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        if item.get("caption"):
            # Convert ISO 8601 timestamp to Unix timestamp
            timestamp = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00')).timestamp()
            posts.append({'text': item["caption"], 'timestamp': timestamp})
    return posts

# ---------- Twitter Fetch ----------
def fetch_twitter_tweets(username, limit=20):
    posts = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"https://twitter.com/{username}", timeout=60000)
        page.wait_for_selector("article")
        
        seen_tweets = set()
        while len(posts) < limit:
            articles = page.query_selector_all("article")
            for article in articles:
                try:
                    text_elem = article.query_selector("div[lang]")
                    time_elem = article.query_selector("time")
                    if text_elem and time_elem:
                        text = text_elem.inner_text().strip()
                        if text not in seen_tweets:
                            datetime_str = time_elem.get_attribute("datetime")
                            timestamp = datetime.fromisoformat(datetime_str.replace('Z', '+00:00')).timestamp()
                            posts.append({'text': text, 'timestamp': timestamp})
                            seen_tweets.add(text)
                            if len(posts) >= limit:
                                break
                except Exception:
                    continue
            if len(posts) >= limit:
                break
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(2000)
        browser.close()
    return posts


# ---------- Routes ----------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict_reddit', methods=['POST'])
def predict_reddit():
    username = request.form.get('username', '').strip()
    if not username:
        return render_template('index.html', error="⚠️ Please enter a Reddit username.")
    try:
        posts = fetch_user_comments(username, limit=25)
        if not posts:
            return render_template('index.html', error=f"⚠️ No recent comments found for user '{username}'.")
        results = analyze_posts(posts)
        return render_template('index.html', results=results, source='Reddit', user=username)
    except Exception as e:
        traceback.print_exc()
        return render_template('index.html', error=f"⚠️ An error occurred fetching Reddit data: {e}")

@app.route('/predict_instagram', methods=['POST'])
def predict_instagram():
    profile_input = request.form.get('username', '').strip()
    if not profile_input:
        return render_template('index.html', error="⚠️ Please enter an Instagram username.")
    try:
        posts = fetch_instagram_captions(profile_input, limit=12)
        if not posts:
            return render_template('index.html', error=f"⚠️ No captions found for {profile_input}")
        results = analyze_posts(posts)
        return render_template('index.html', results=results, source='Instagram', user=profile_input)
    except Exception as e:
        traceback.print_exc()
        return render_template('index.html', error=f"⚠️ An error occurred fetching Instagram data: {e}")

@app.route('/predict_twitter', methods=['POST'])
def predict_twitter():
    username = request.form.get('twitter_username', '').strip()
    if not username:
        return render_template('index.html', error="⚠️ Please enter a Twitter username.")
    try:
        posts = fetch_twitter_tweets(username, limit=20)
        if not posts:
            return render_template('index.html', error=f"⚠️ No tweets found for user '{username}'.")
        results = analyze_posts(posts)
        return render_template('index.html', results=results, source='Twitter', user=username)
    except Exception as e:
        traceback.print_exc()
        return render_template('index.html', error=f"⚠️ An error occurred fetching Twitter data: {e}")


if __name__ == '__main__':
    app.run(debug=True)