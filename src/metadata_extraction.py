# Optional placeholder for custom metadata functions

# This module can be used to isolate reusable extractors,
# or to run manual metadata pulls during testing.

from batch_processor import (
    extract_article_metadata,
    extract_tweet_metadata,
    extract_video_transcript_metadata
)

__all__ = [
    "extract_article_metadata",
    "extract_tweet_metadata",
    "extract_video_transcript_metadata"
]
