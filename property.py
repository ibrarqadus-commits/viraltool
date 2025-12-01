import streamlit as st
import requests
from datetime import datetime, timedelta
import json
import os

API_KEY = "AIzaSyAo8yIqky-HN9Y9TL24hiUvMggqBh05zA0"
SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"

DATA_FILE = "viral_data.json"

st.title("YouTube Viral + London Property Tracker")

days = st.number_input("Look back days:", min_value=1, max_value=30, value=7)
max_results = st.number_input("Max results per keyword:", min_value=5, max_value=50, value=20)
min_views = st.number_input("Minimum views to include:", min_value=0, value=100)
min_like_ratio = st.number_input("Minimum like ratio (%) to include:", min_value=0, max_value=100, value=1)

# Pre-filled keywords for testing + luxury property
keywords = [
    # Viral / trending
    "Funny videos",
    "TikTok compilation",
    "Viral challenge",
    "Trending music",
    "Meme videos",
    "Gaming highlights",
    "Unboxing videos",
    "ASMR",
    "Tech review",
    "Cute animals",
    # Luxury London property
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

# Luxury keyword boost for relevance filtering
luxury_keywords = ["luxury", "penthouse", "mansion", "prime", "Mayfair", "Kensington", "Knightsbridge", "Chelsea"]

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
        st.write(f"Searching for: {keyword}")
        try:
            # Search videos
            params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "date",
                "publishedAfter": start_date,
                "maxResults": max_results,
                "key": API_KEY
            }
            response = requests.get(SEARCH_URL, params=params).json()
            videos = response.get("items", [])
            video_ids = [v["id"]["videoId"] for v in videos if "videoId" in v["id"]]

            if not video_ids:
                st.warning(f"No videos found for {keyword}")
                continue

            # Fetch video stats
            stats_response = requests.get(
                VIDEO_URL,
                params={"part": "snippet,statistics", "id": ",".join(video_ids), "key": API_KEY}
            ).json()
            stats = stats_response.get("items", [])

            for s in stats:
                vid = s["id"]
                title = s["snippet"]["title"]
                views = int(s["statistics"].get("viewCount", 0))
                likes = int(s["statistics"].get("likeCount", 0)) if "likeCount" in s["statistics"] else 0
                published = s["snippet"]["publishedAt"]

                # Previous views for growth
                prev_views = previous_data.get(vid, {}).get("views", 0)
                growth = views - prev_views

                # Luxury relevance boost
                is_luxury = any(k.lower() in title.lower() for k in luxury_keywords)

                # Engagement ratio
                like_ratio = (likes / views * 100) if views > 0 else 0

                # Filter by minimum views, like ratio, or luxury relevance
                if views >= min_views and (like_ratio >= min_like_ratio or is_luxury):
                    all_results.append({
                        "id": vid,
                        "title": title,
                        "views": views,
                        "likes": likes,
                        "like_ratio": round(like_ratio, 2),
                        "growth": growth,
                        "url": f"https://www.youtube.com/watch?v={vid}",
                        "published": published,
                        "is_luxury": is_luxury
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
        st.success(f"Top trending videos based on growth & engagement:")
        for v in viral_sorted:
            st.markdown(
                f"**Title:** {v['title']}  \n"
                f"**Views:** {v['views']}  \n"
                f"**Likes:** {v['likes']}  \n"
                f"**Like Ratio:** {v['like_ratio']}%  \n"
                f"**Growth since last check:** {v['growth']}  \n"
                f"**Published:** {v['published']}  \n"
                f"**Luxury Related:** {'Yes' if v['is_luxury'] else 'No'}  \n"
                f"[Watch Video]({v['url']})"
            )
            st.write("---")
    else:
        st.warning("No viral videos found matching filters.")
