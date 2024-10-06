import asyncio
import aiohttp
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logger = logging.getLogger(__name__)
stop_words = set(stopwords.words('english'))

async def analyze_sentiment(session, text):
    logger.info(f"Analyzing sentiment for text: {text[:50]}...")
    async with session.post('https://api.groq.com/openai/v1/chat/completions', json={
        'prompt': f"Analyze the sentiment of the following text and classify it as Positive or Negative:\n\n{text}",
        'max_tokens': 10,
        'n': 1,
        'stop': None,
        'temperature': 0.5,
    }, headers={'Authorization': f'Bearer {GROQ_API_KEY}'}) as response:
        sentiment = (await response.json())['choices'][0]['text'].strip()
        return sentiment

async def get_comments_sentiment(video_id):
    logger.info(f"Fetching comments and analyzing sentiment for video: {video_id}")
    comments = []
    next_page_token = None

    while True:
        url = f"https://www.youtube.com/watch?v={video_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                for item in soup.find_all('yt-formatted-string', {'class': 'style-scope ytd-comment-renderer'}):
                    comments.append(item.text)

        if not next_page_token:
            break

    async with aiohttp.ClientSession() as session:
        tasks = [analyze_sentiment(session, comment) for comment in comments]
        sentiments = await asyncio.gather(*tasks)

    df_comments = pd.DataFrame({'comment': comments, 'sentiment': sentiments})
    positive = df_comments[df_comments['sentiment'] == 'Positive'].shape[0]
    negative = df_comments[df_comments['sentiment'] == 'Negative'].shape[0]
    total = df_comments.shape[0]

    if total > 0:
        positive_ratio = positive / total
        negative_ratio = negative / total
    else:
        positive_ratio = negative_ratio = 0

    logger.info(f"Sentiment analysis complete for video: {video_id}")
    return positive_ratio, negative_ratio

async def analyze_transcript(transcript):
    logger.info(f"Analyzing transcript: {transcript[:50]}...")
    response = await client.chat.completions.create(
        model="llama3-groq-70b-8192-tool-use-preview",
        messages=[
            {"role": "system", "content": "Highlight the positive points in the following transcript:"},
            {"role": "user", "content": transcript}
        ],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    )
    highlights = response.choices[0].text.strip()
    logger.info(f"Transcript analysis complete: {highlights[:50]}...")
    return highlights

async def identify_competitor_content_gaps(channel_id, start_date, end_date):
    logger.info(f"Identifying content gaps for channel: {channel_id}")
    video_ids = await get_channel_videos(channel_id, published_after=start_date, published_before=end_date)
    stats_df = await get_video_statistics(video_ids)
    
    titles_descriptions = stats_df['title'] + ". " + stats_df['description']
    combined_text = ' '.join(titles_descriptions)
    
    word_tokens = word_tokenize(combined_text.lower())
    filtered_text = [word for word in word_tokens if word.isalnum() and word not in stop_words]
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([' '.join(filtered_text)])
    feature_names = vectorizer.get_feature_names_out()
    
    important_terms = sorted(zip(feature_names, tfidf_matrix.toarray()[0]), key=lambda x: x[1], reverse=True)[:20]
    
    logger.info(f"Content gaps identified for channel: {channel_id}")
    return [term for term, score in important_terms]

async def identify_top_performing_topics(channel_id):
    logger.info(f"Identifying top performing topics for channel: {channel_id}")
    cursor.execute('''
    SELECT title, description, views, likes, comments
    FROM videos
    WHERE channel_id = ?
    ORDER BY views DESC
    LIMIT 50
    ''', (channel_id,))
    top_videos = cursor.fetchall()
    
    combined_text = ' '.join([f"{video[0]}. {video[1]}" for video in top_videos])
    
    word_tokens = word_tokenize(combined_text.lower())
    filtered_text = [word for word in word_tokens if word.isalnum() and word not in stop_words]
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([' '.join(filtered_text)])
    feature_names = vectorizer.get_feature_names_out()
    
    important_terms = sorted(zip(feature_names, tfidf_matrix.toarray()[0]), key=lambda x: x[1], reverse=True)[:10]
    
    logger.info(f"Top performing topics identified for channel: {channel_id}")
    return [term for term, score in important_terms]