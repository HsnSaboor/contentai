import os
import sqlite3
import logging
import aiohttp
import nltk

# Download the stopwords corpus if it's not already downloaded
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define your API key
GROQ_API_KEY = os.getenv('GROQ_API_KEY')  # Assuming you store your API key in an environment variable

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

# Factory function to create a ClientSession
async def create_client_session():
    return aiohttp.ClientSession()