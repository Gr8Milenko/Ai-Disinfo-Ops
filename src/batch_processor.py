import os
import json
import re
import dateparser
import tldextract
import concurrent.futures
import uuid
import spacy
from newspaper import Article
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

from infer import auto_infer_from_saved_metadata

# Load spaCy
nlp = spacy.load("en_core_web_sm")

# Logging
import logging
from datetime import datetime

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"batch_processor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filemode="w"
)
logger = logging.getLogger(__name__)
# --------- Extractors ---------

def extract_article_metadata(url):
    article = Article(url)
    article.download()
    article.parse()
    return {
        "type": "article",
        "title": article.title,
        "authors": article.authors,
        "publish_date": str(article.publish_date),
        "text": article.text,
        "source_domain": tldextract.extract(url).domain,
        "url": url,
        "word_count": len(article.text.split())
    }

def extract_tweet_metadata(tweet_obj):
    return {
        "type": "tweet",
        "tweet_id": tweet_obj["id"],
        "username": tweet_obj["username"],
        "text": tweet_obj["text"],
        "created_at": str(tweet_obj["created_at"]),
        "retweet_count": tweet_obj.get("retweet_count", 0),
        "like_count": tweet_obj.get("like_count", 0),
        "reply_count": tweet_obj.get("reply_count", 0),
        "quote_count": tweet_obj.get("quote_count", 0),
        "lang": tweet_obj.get("lang", "und")
    }

def extract_youtube_id(url: str) -> str:
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else str(uuid.uuid4())

def get_transcript_from_youtube(video_url: str) -> str:
    video_id = extract_youtube_id(video_url)
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return TextFormatter().format_transcript(transcript)

def extract_video_transcript_metadata(video_url: str):
    transcript_text = get_transcript_from_youtube(video_url)
    doc = nlp(transcript_text)
    return {
        "type": "video_transcript",
        "video_url": video_url,
        "video_id": extract_youtube_id(video_url),
        "text": transcript_text,
        "word_count": len(transcript_text.split()),
        "sentence_count": len(list(doc.sents)),
        "named_entities": list(set(ent.text for ent in doc.ents))
    }
  # --------- Batch Processor ---------

def batch_process_sources(article_urls=[], tweet_objects=[], video_urls=[],
                          processed_dir="data/processed/", save_combined=True):
    os.makedirs(processed_dir, exist_ok=True)
    subdirs = {
        "article": os.path.join(processed_dir, "articles"),
        "tweet": os.path.join(processed_dir, "tweets"),
        "video_transcript": os.path.join(processed_dir, "transcripts")
    }
    for sub in subdirs.values():
        os.makedirs(sub, exist_ok=True)

    results = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        for url in article_urls:
            futures.append(executor.submit(safe_call, extract_article_metadata, url))

        for tweet in tweet_objects:
            futures.append(executor.submit(safe_call, extract_tweet_metadata, tweet))

        for video_url in video_urls:
            futures.append(executor.submit(safe_call, extract_video_transcript_metadata, video_url))

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
                save_metadata_record(result, subdirs[result["type"]])

    if save_combined:
        save_metadata_to_json(results, os.path.join(processed_dir, "metadata_combined.json"))
# --------- Helpers ---------

def safe_call(func, *args):
    try:
        result = func(*args)
        logger.info(f"[SUCCESS] {func.__name__} - {args[0] if args else ''}")
        return result
    except Exception as e:
        logger.error(f"[FAILURE] {func.__name__} - {args[0] if args else ''} - {e}")
        return None

def save_metadata_record(metadata: dict, output_dir: str):
    uid = metadata.get("video_id") or metadata.get("tweet_id") or str(uuid.uuid4())
    filename = f"{uid}.json"
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
    logger.info(f"[SAVE] {metadata['type']} saved to {path}")
    auto_infer_from_saved_metadata(metadata, path)

def save_metadata_to_json(metadata: list, filepath: str):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
    logger.info(f"[COMBINED] All metadata saved to {filepath}")
