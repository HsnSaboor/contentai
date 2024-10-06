from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
import asyncio
import sqlite3
from init import conn, cursor, create_client_session, GROQ_API_KEY
from utils import calculate_engagement_rate, calculate_comment_to_like_ratio, analyze_transcript_readability, calculate_transcript_score
from data_retrieval import get_channel_videos, get_video_statistics
from analysis import get_comments_sentiment, analyze_transcript, identify_competitor_content_gaps, identify_top_performing_topics, get_transcript
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)

class EnhancedChannelAnalysis(Resource):
    async def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('channel_username', type=str, required=True)
        parser.add_argument('start_date', type=str)
        parser.add_argument('end_date', type=str)
        args = parser.parse_args()

        async def analyze():
            logger.info(f"Starting enhanced analysis for channel: {args['channel_username']}")
            video_ids = await get_channel_videos(args['channel_username'], args['start_date'], args['end_date'])
            stats_df = await get_video_statistics(video_ids, args['channel_username'])

            async with create_client_session() as client:
                for _, row in stats_df.iterrows():
                    video_id = row['video_id']
                    positive_ratio, negative_ratio = await get_comments_sentiment(video_id)
                    transcript = await get_transcript(video_id)
                    highlights = await analyze_transcript(transcript, client)
                    score = calculate_transcript_score(row['likes'], row['comments'], row['views'])
                    
                    engagement_rate = calculate_engagement_rate(row['likes'], row['comments'], row['views'])
                    comment_to_like_ratio = calculate_comment_to_like_ratio(row['comments'], row['likes'])
                    readability_score = analyze_transcript_readability(transcript)

                    cursor.execute('''
                    INSERT OR REPLACE INTO videos 
                    (video_id, channel_username, title, description, views, likes, comments, 
                    positive_comment_ratio, negative_comment_ratio, transcript_score, highlights,
                    engagement_rate, comment_to_like_ratio, video_length, readability_score, publish_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (video_id, row['channel_username'], row['title'], row['description'], 
                          row['views'], row['likes'], row['comments'], positive_ratio, 
                          negative_ratio, score, highlights, engagement_rate, comment_to_like_ratio,
                          row['duration'], readability_score, row['publishedAt']))
                    conn.commit()

                content_gaps = await identify_competitor_content_gaps(args['channel_username'], args['start_date'], args['end_date'])
                top_performing_topics = await identify_top_performing_topics(args['channel_username'])

            logger.info(f"Enhanced analysis complete for channel: {args['channel_username']}")
            return {
                "message": "Enhanced analysis complete",
                "content_gaps": content_gaps,
                "top_performing_topics": top_performing_topics
            }

        return await analyze()

class VideoAnalytics(Resource):
    def get(self, video_id):
        logger.info(f"Fetching analytics for video: {video_id}")
        cursor.execute('SELECT * FROM videos WHERE video_id = ?', (video_id,))
        video = cursor.fetchone()

        if not video:
            logger.warning(f"Video not found: {video_id}")
            return {"error": "Video not found"}, 404

        logger.info(f"Analytics fetched for video: {video_id}")
        return {
            "video_id": video[0],
            "title": video[2],
            "views": video[4],
            "likes": video[5],
            "comments": video[6],
            "engagement_rate": video[12],
            "comment_to_like_ratio": video[13],
            "video_length": video[14],
            "readability_score": video[15],
        }

class CompetitorChannelTracking(Resource):
    async def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('channel_username', type=str, required=True)
        parser.add_argument('start_date', type=str)
        parser.add_argument('end_date', type=str)
        parser.add_argument('order', type=str, choices=['date', 'rating', 'relevance', 'title', 'videoCount', 'viewCount'], default='date')
        args = parser.parse_args()

        async def track():
            logger.info(f"Starting competitor channel tracking for channel: {args['channel_username']}")
            video_ids = await get_channel_videos(args['channel_username'], args['start_date'], args['end_date'], args['order'])
            stats_df = await get_video_statistics(video_ids, args['channel_username'])

            async with create_client_session() as client:
                for _, row in stats_df.iterrows():
                    video_id = row['video_id']
                    positive_ratio, negative_ratio = await get_comments_sentiment(video_id)
                    transcript = await get_transcript(video_id)
                    highlights = await analyze_transcript(transcript, client)
                    score = calculate_transcript_score(row['likes'], row['comments'], row['views'])
                    
                    engagement_rate = calculate_engagement_rate(row['likes'], row['comments'], row['views'])
                    comment_to_like_ratio = calculate_comment_to_like_ratio(row['comments'], row['likes'])
                    readability_score = analyze_transcript_readability(transcript)

                    cursor.execute('''
                    INSERT OR REPLACE INTO videos 
                    (video_id, channel_username, title, description, views, likes, comments, 
                    positive_comment_ratio, negative_comment_ratio, transcript_score, highlights,
                    engagement_rate, comment_to_like_ratio, video_length, readability_score, publish_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (video_id, row['channel_username'], row['title'], row['description'], 
                          row['views'], row['likes'], row['comments'], positive_ratio, 
                          negative_ratio, score, highlights, engagement_rate, comment_to_like_ratio,
                          row['duration'], readability_score, row['publishedAt']))
                    conn.commit()

                content_gaps = await identify_competitor_content_gaps(args['channel_username'], args['start_date'], args['end_date'])
                top_performing_topics = await identify_top_performing_topics(args['channel_username'])

            logger.info(f"Competitor channel tracking complete for channel: {args['channel_username']}")
            return {
                "message": "Competitor channel tracking complete",
                "content_gaps": content_gaps,
                "top_performing_topics": top_performing_topics
            }

        return await track()

api.add_resource(EnhancedChannelAnalysis, '/enhanced_analyze')
api.add_resource(VideoAnalytics, '/video_analytics/<string:video_id>')
api.add_resource(CompetitorChannelTracking, '/competitor_tracking')

if __name__ == '__main__':
    app.run(debug=True)