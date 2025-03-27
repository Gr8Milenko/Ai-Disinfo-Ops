import os
import json
import feedparser
import logging
import tweepy
from dotenv import load_dotenv
from batch_processor import extract_article_metadata, extract_tweet_metadata, save_metadata_record

# Load Twitter API token
load_dotenv()
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Setup logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "realtime_monitor.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filemode="a"
)
logger = logging.getLogger(__name__)

# Setup directories
article_dir = "data/processed/articles"
tweet_dir = "data/processed/tweets"
os.makedirs(article_dir, exist_ok=True)
os.makedirs(tweet_dir, exist_ok=True)

# ------------- RSS MONITORING -------------
def monitor_rss_feeds(feed_urls, known_urls_file="data/rss_seen.json", interval=60):
    logger.info(f"Starting RSS monitor with interval {interval}s")
    if os.path.exists(known_urls_file):
        with open(known_urls_file, "r") as f:
            seen = set(json.load(f))
    else:
        seen = set()

    while True:
        new_seen = set(seen)
        for feed_url in feed_urls:
            parsed = feedparser.parse(feed_url)
            for entry in parsed.entries:
                link = entry.link
                if link not in seen:
                    try:
                        meta = extract_article_metadata(link)
                        save_metadata_record(meta, article_dir)
                        logger.info(f"[RSS] Processed: {link}")
                        new_seen.add(link)
                    except Exception as e:
                        logger.error(f"[RSS ERROR] {link}: {e}")
        seen = new_seen
        with open(known_urls_file, "w") as f:
            json.dump(list(seen), f)
        time.sleep(interval)

# ------------- TWITTER STREAMING -------------
class TwitterStream(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        try:
            tweet_obj = {
                "id": tweet.id,
                "username": tweet.author_id,
                "text": tweet.text,
                "created_at": str(tweet.created_at),
                "retweet_count": tweet.public_metrics.get("retweet_count", 0),
                "like_count": tweet.public_metrics.get("like_count", 0),
                "reply_count": tweet.public_metrics.get("reply_count", 0),
                "quote_count": tweet.public_metrics.get("quote_count", 0),
                "lang": tweet.lang
            }
            meta = extract_tweet_metadata(tweet_obj)
            save_metadata_record(meta, tweet_dir)
            logger.info(f"[Twitter] Processed tweet {tweet.id}")
        except Exception as e:
            logger.error(f"[Twitter ERROR] {e}")

def start_twitter_stream(keywords):
    logger.info(f"Starting Twitter stream with keywords: {keywords}")
    stream = TwitterStream(BEARER_TOKEN)

    existing = stream.get_rules().data
    if existing:
        rule_ids = [rule.id for rule in existing]
        stream.delete_rules(rule_ids)

    stream.add_rules(tweepy.StreamRule(value=" OR ".join(keywords)))
    stream.filter(tweet_fields=["created_at", "lang", "public_metrics", "author_id"])
