import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

st.title("YouTube Competitor Analysis")

# Input fields
user_channel_id = st.text_input("Enter your YouTube Channel ID")
competitor_channel_id = st.text_input("Enter Competitor YouTube Channel ID")
start_date = st.text_input("Enter Start Date (YYYY-MM-DD)")
end_date = st.text_input("Enter End Date (YYYY-MM-DD)")

# Button to trigger analysis
if st.button("Analyze"):
    # Fetch analytics for user channel
    user_response = requests.post("http://localhost:5000/enhanced_analyze", json={
        "channel_id": user_channel_id,
        "start_date": start_date,
        "end_date": end_date
    })
    user_data = user_response.json()

    # Fetch analytics for competitor channel
    competitor_response = requests.post("http://localhost:5000/enhanced_analyze", json={
        "channel_id": competitor_channel_id,
        "start_date": start_date,
        "end_date": end_date
    })
    competitor_data = competitor_response.json()

    # Display results
    st.subheader("User Channel Analysis")
    st.write(f"Content Gaps: {user_data['content_gaps']}")
    st.write(f"Top Performing Topics: {user_data['top_performing_topics']}")

    st.subheader("Competitor Channel Analysis")
    st.write(f"Content Gaps: {competitor_data['content_gaps']}")
    st.write(f"Top Performing Topics: {competitor_data['top_performing_topics']}")

    # Fetch top videos for both channels
    user_videos_response = requests.get(f"http://localhost:5000/video_analytics?channel_id={user_channel_id}&limit=10")
    user_videos_data = user_videos_response.json()

    competitor_videos_response = requests.get(f"http://localhost:5000/video_analytics?channel_id={competitor_channel_id}&limit=10")
    competitor_videos_data = competitor_videos_response.json()

    # Display top videos
    st.subheader("Top Videos for User Channel")
    st.write(pd.DataFrame(user_videos_data))

    st.subheader("Top Videos for Competitor Channel")
    st.write(pd.DataFrame(competitor_videos_data))

    # Plot engagement rates
    user_engagement_rates = [video['engagement_rate'] for video in user_videos_data]
    competitor_engagement_rates = [video['engagement_rate'] for video in competitor_videos_data]

    plt.figure(figsize=(10, 5))
    plt.bar(["User Channel", "Competitor Channel"], [sum(user_engagement_rates)/len(user_engagement_rates), sum(competitor_engagement_rates)/len(competitor_engagement_rates)], color=['blue', 'red'])
    plt.ylabel("Average Engagement Rate")
    st.pyplot(plt)