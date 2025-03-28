import time
import streamlit as st
import tweepy
from datetime import datetime, timedelta

# Optional: simple cooldown tracker in memory
POST_COOLDOWN_SECONDS = 10
_last_post_time = None

def get_twitter_client():
    bearer = st.secrets.get("twitter_bearer_token")
    api_key = st.secrets.get("twitter_api_key", None)
    api_secret = st.secrets.get("twitter_api_secret", None)
    access_token = st.secrets.get("twitter_access_token", None)
    access_secret = st.secrets.get("twitter_access_secret", None)

    if all([api_key, api_secret, access_token, access_secret]):
        # OAuth 1.0a for write access
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
        return tweepy.API(auth)
    elif bearer:
        # Read-only mode using bearer token
        return tweepy.Client(bearer_token=bearer)
    else:
        raise ValueError("Twitter credentials not found in Streamlit secrets.")

def post_tweet(message, dry_run=False):
    global _last_post_time

    if _last_post_time and (datetime.now() - _last_post_time).seconds < POST_COOLDOWN_SECONDS:
        print("[TWITTER] Cooldown active. Skipping tweet.")
        return

    client = get_twitter_client()

    if dry_run:
        print("[TWITTER][DRY RUN] Tweet:", message)
        return

    try:
        client.update_status(status=message)
        _last_post_time = datetime.now()
        print("[TWITTER] Tweet sent.")
    except Exception as e:
        print(f"[TWITTER][ERROR] Failed to post tweet: {e}")

def reply_to_tweet(message, reply_to_id, dry_run=False):
    global _last_post_time

    if _last_post_time and (datetime.now() - _last_post_time).seconds < POST_COOLDOWN_SECONDS:
        print("[TWITTER] Cooldown active. Skipping reply.")
        return

    client = get_twitter_client()

    if dry_run:
        print(f"[TWITTER][DRY RUN] Reply to {reply_to_id}: {message}")
        return

    try:
        client.update_status(status=message, in_reply_to_status_id=reply_to_id, auto_populate_reply_metadata=True)
        _last_post_time = datetime.now()
        print("[TWITTER] Reply sent.")
    except Exception as e:
        print(f"[TWITTER][ERROR] Failed to reply: {e}")
