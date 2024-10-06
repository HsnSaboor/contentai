import streamlit as st
import requests

st.title("YouTube Competitor Analysis")

# Input fields
user_channel_username = st.text_input("Enter your YouTube Channel Username")
competitor_channel_username = st.text_input("Enter Competitor YouTube Channel Username")
start_date = st.text_input("Enter Start Date (YYYY-MM-DD)")
end_date = st.text_input("Enter End Date (YYYY-MM-DD)")

# Button to trigger analysis
if st.button("Analyze"):
    # Fetch analytics for user channel
    user_response = requests.post("http://localhost:5000/enhanced_analyze", json={
        "channel_username": user_channel_username,
        "start_date": start_date,
        "end_date": end_date
    })
    user_data = user_response.json()

    # Fetch analytics for competitor channel
    competitor_response = requests.post("http://localhost:5000/enhanced_analyze", json={
        "channel_username": competitor_channel_username,
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
    user_videos_response = requests.get(f"http://localhost:5000/video_analytics?channel_username={user_channel_username}&limit=10")
    user_videos_data = user_videos_response.json()

    competitor_videos_response = requests.get(f"http://localhost:5000/video_analytics?channel_username={competitor_channel_username}&limit=10")
    competitor_videos_data = competitor_videos_response.json()

    # Display top videos
    st.subheader("Top Videos for User Channel")
    st.write(user_videos_data)

    st.subheader("Top Videos for Competitor Channel")
    st.write(competitor_videos_data)
