import os
import sqlite3
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database schema
conn = sqlite3.connect('content_strategy.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS videos (
    video_id TEXT PRIMARY KEY,
    channel_id TEXT,
    title TEXT,
    description TEXT,
    views INTEGER,
    likes INTEGER,
    comments INTEGER,
    positive_comment_ratio REAL,
    negative_comment_ratio REAL,
    transcript_score REAL,
    highlights TEXT,
    retention REAL,
    engagement_rate REAL,
    comment_to_like_ratio REAL,
    video_length INTEGER,
    readability_score REAL,
    publish_date TEXT
)
''')
conn.commit()

logger.info("Database schema initialized successfully.")