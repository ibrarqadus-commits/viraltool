import streamlit as st
import requests
from datetime import datetime, timedelta
import json
import os

API_KEY = "AIzaSyAo8yIqky-HN9Y9TL24hiUvMggqBh05zA0"
SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"

DATA_FILE = "viral_data.json"

st.title("YouTube Viral Tracker")

days = st.number_input("Look back days:", min_value=1, max_value=7, value=2)

# Luxury London property keywords
keywords = [
    "London luxury property",
    "Mayfair apartments",
    "Kensington homes",
    "Knightsbridge real estate",
    "Chelsea mansion",
    "London penthouse",
    "Prime central London property",
    "London investment property",
    "Luxury house London",
    "London property market",
    "London real estate trends",
    "Luxury flat London",
    "Super-prime London homes",
    "London property prices",
    "London property for sale"
]

if st.button("Fetch Viral Videos"):
    start_date = (datetime.utcnow() - timedelta(days=days)).isoformat("T") + "Z"
    all_results = []

    # Load previous data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            previous_data = json.load(f)
    else:
        previous_data = {}

    for keyword in keywords:
        keyword = keyword.strip()
        st.write(f"Searching for: {keyword}")
        try:
            # Search videos
            params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "date",
                "publishedAfter": start_date,
                "maxResults": 10,
                "key": API_KEY
            }
            response = requests.get(SEARCH_URL, params=params).json()
            videos = response.get("items", [])
            video_ids = [v["id"]["videoId"] for v in videos if "videoId" in v["id"]]

            if not video_ids:
                st.warning(f"No videos found for {keyword}")
                continue

            # Fetch stats
            stats_response = requests.get(
                VIDEO_URL,
                params={"part": "snippet,statistics", "id": ",".join(video_ids), "key": API_KEY}
            ).json()
            stats = stats_response.get("items", [])

            for s in stats:
                vid = s["id"]
                title = s["snippet"]["title"]
                views = int(s["statistics"].get("viewCount", 0))
                published = s["snippet"]["publishedAt"]

                # Previous views
                prev_views = previous_data.get(vid, {}).get("views", 0)
                growth = views - prev_views

                all_results.append({
                    "id": vid,
                    "title": title,
                    "views": views,
                    "growth": growth,
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "published": published
                })

                # Update previous data
                previous_data[vid] = {"views": views, "last_checked": datetime.utcnow().isoformat()}

        except Exception as e:
            st.error(f"Error fetching data for {keyword}: {e}")

    # Save updated data
    with open(DATA_FILE, "w") as f:
        json.dump(previous_data, f, indent=2)

    # Sort by growth
    viral_sorted = sorted(all_results, key=lambda x: x["growth"], reverse=True)

    if viral_sorted:
        st.success(f"Top trending videos based on view growth:")
        for v in viral_sorted:
            st.markdown(
                f"**Title:** {v['title']}  \n"
                f"**Views:** {v['views']}  \n"
                f"**Growth since last check:** {v['growth']}  \n"
                f"**Published:** {v['published']}  \n"
                f"[Watch Video]({v['url']})"
            )
            st.write("---")
    else:
        st.warning("No viral videos found.")
