import streamlit as st
import requests
from datetime import datetime, timedelta

API_KEY = "AIzaSyAo8yIqky-HN9Y9TL24hiUvMggqBh05zA0"

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"

st.title("YouTube Viral & Luxury Property Finder")

days = st.number_input("Search last X days:", min_value=1, max_value=30, value=30)

# ✅ Mixed keywords (Luxury Property + Viral so you ALWAYS get results)
keywords = [
    # Luxury London Property
    "London property tour",
    "London mansion tour",
    "London penthouse tour",
    "Luxury homes London",
    "London real estate",
    "Mayfair house tour",
    "Knightsbridge property",
    "Chelsea property tour",
    "Super prime London",
    "UK luxury homes",

    # Viral General (guaranteed results)
    "Funny videos",
    "TikTok compilation",
    "Viral challenge",
    "Meme videos",
    "Cute dogs",
    "Unboxing viral",
]

if st.button("Fetch Data"):
    try:
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        for keyword in keywords:
            st.write(f"Searching for: {keyword}")

            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 10,
                "key": API_KEY
            }

            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            if "items" not in data or not data["items"]:
                st.warning(f"No videos found for {keyword}")
                continue

            for item in data["items"]:
                video_id = item["id"].get("videoId")
                if not video_id:
                    continue

                video_title = item["snippet"].get("title", "No title")
                channel_title = item["snippet"].get("channelTitle", "")
                video_url = f"https://www.youtube.com/watch?v={video_id}"

                # Fetch stats
                stats_params = {"part": "statistics", "id": video_id, "key": API_KEY}
                stats = requests.get(YOUTUBE_VIDEO_URL, params=stats_params).json()

                if "items" in stats and stats["items"]:
                    stats_data = stats["items"][0]["statistics"]
                    views = stats_data.get("viewCount", "0")
                    likes = stats_data.get("likeCount", "0")
                else:
                    views = "0"
                    likes = "0"

                all_results.append({
                    "Keyword": keyword,
                    "Title": video_title,
                    "Channel": channel_title,
                    "URL": video_url,
                    "Views": views,
                    "Likes": likes
                })

        if all_results:
            st.success(f"Found {len(all_results)} total videos")

            for result in all_results:
                st.markdown(
                    f"### {result['Title']}  \n"
                    f"**Keyword:** {result['Keyword']}  \n"
                    f"**Channel:** {result['Channel']}  \n"
                    f"**Views:** {result['Views']}  \n"
                    f"**Likes:** {result['Likes']}  \n"
                    f"[Watch Video]({result['URL']})"
                )
                st.write("---")
        else:
            st.warning("No results found at all")

    except Exception as e:
        st.error(f"Error: {e}")
