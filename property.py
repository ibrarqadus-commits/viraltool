import streamlit as st
import requests
from datetime import datetime, timedelta

API_KEY = "YOUR_YOUTUBE_API_KEY"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

st.title("YouTube Viral Topics Tool")

days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)

keywords = ["North Korea", "smartphone", "iPhone", "Kim Jong Un"]

if st.button("Fetch Data"):
    start_date = (datetime.utcnow() - timedelta(days=days)).isoformat("T") + "Z"
    all_results = []

    for keyword in keywords:
        st.write(f"Searching for keyword: {keyword}")
        try:
            # Search videos
            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY
            }
            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params).json()
            if "items" not in response or not response["items"]:
                st.warning(f"No videos found for keyword: {keyword}")
                continue

            video_ids = [item["id"]["videoId"] for item in response["items"] if "videoId" in item["id"]]
            channel_ids = [item["snippet"]["channelId"] for item in response["items"]]

            # Fetch video stats
            stats_response = requests.get(
                YOUTUBE_VIDEO_URL,
                params={"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            ).json()
            stats = stats_response.get("items", [])

            # Fetch channel stats
            channel_response = requests.get(
                YOUTUBE_CHANNEL_URL,
                params={"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            ).json()
            channels = channel_response.get("items", [])

            # Combine data
            for video, stat, channel in zip(response["items"], stats, channels):
                title = video["snippet"].get("title", "N/A")
                description = video["snippet"].get("description", "")[:200]
                video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                views = int(stat["statistics"].get("viewCount", 0))
                subs = int(channel["statistics"].get("subscriberCount", 0))

                # Optional: remove low subscriber filter to get more results
                all_results.append({
                    "Title": title,
                    "Description": description,
                    "URL": video_url,
                    "Views": views,
                    "Subscribers": subs
                })

        except Exception as e:
            st.error(f"Error fetching data for {keyword}: {e}")

    # Sort by views
    all_results = sorted(all_results, key=lambda x: x["Views"], reverse=True)

    if all_results:
        st.success(f"Found {len(all_results)} results!")
        for result in all_results:
            st.markdown(
                f"**Title:** {result['Title']}  \n"
                f"**Description:** {result['Description']}  \n"
                f"**URL:** [Watch Video]({result['URL']})  \n"
                f"**Views:** {result['Views']}  \n"
                f"**Subscribers:** {result['Subscribers']}"
            )
            st.write("---")
    else:
        st.warning("No results found.")
