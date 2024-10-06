import textstat
import logging

logger = logging.getLogger(__name__)

def calculate_engagement_rate(likes, comments, views):
    logger.info(f"Calculating engagement rate for likes: {likes}, comments: {comments}, views: {views}")
    return (likes + comments) / views if views > 0 else 0

def calculate_comment_to_like_ratio(comments, likes):
    logger.info(f"Calculating comment-to-like ratio for comments: {comments}, likes: {likes}")
    return comments / likes if likes > 0 else 0

def analyze_transcript_readability(transcript):
    logger.info(f"Analyzing readability score for transcript: {transcript[:50]}...")
    readability_score = textstat.flesch_reading_ease(transcript)
    return readability_score

def calculate_transcript_score(likes, comments, views):
    logger.info(f"Calculating transcript score for likes: {likes}, comments: {comments}, views: {views}")
    score = (likes + comments) / views * 10
    return min(score, 10)