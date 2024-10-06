import asyncio
import aiohttp
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

async def get_channel_videos(channel_id, published_after=None, published_before=None, order='date'):
    logger.info(f"Fetching videos for channel: {channel_id}")
    video_ids = []
    next_page_token = None

    while True:
        url = f"https://www.youtube.com/channel/{channel_id}/videos"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                for item in soup.find_all('a', {'class': 'yt-simple-endpoint style-scope ytd-grid-video-renderer'}):
                    video_ids.append(item['href'].split('=')[-1])

        if not next_page_token:
            break

    logger.info(f"Fetched {len(video_ids)} video IDs for channel: {channel_id}")
    return video_ids

async def get_video_statistics(video_ids):
    logger.info(f"Fetching statistics for {len(video_ids)} videos")
    stats = []
    for video_id in video_ids:
        url = f"https://www.youtube.com/watch?v={video_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                title = soup.find('meta', {'name': 'title'})['content']
                description = soup.find('meta', {'name': 'description'})['content']
                views = int(soup.find('meta', {'itemprop': 'interactionCount'})['content'])
                likes = int(soup.find('button', {'title': 'I like this'}).text.replace(',', ''))
                comments = int(soup.find('h2', {'id': 'count'}).text.replace(',', ''))
                stats.append({
                    'video_id': video_id,
                    'channel_id': channel_id,
                    'title': title,
                    'description': description,
                    'views': views,
                    'likes': likes,
                    'comments': comments,
                    'duration': '00:00:00',
                    'publishedAt': datetime.now().strftime('%Y-%m-%d')
                })
    logger.info(f"Fetched statistics for {len(stats)} videos")
    return pd.DataFrame(stats)