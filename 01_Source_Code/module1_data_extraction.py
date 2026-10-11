
# ---- Extracted from notebook cell 2 ----
from google.colab import userdata
from googleapiclient.discovery import build

API_KEY = userdata.get("YOUTUBE_API_KEY")

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

response = youtube.videos().list(
    part="snippet,statistics",
    chart="mostPopular",
    regionCode="IN",
    maxResults=5
).execute()

for video in response.get("items", []):
    print(
        video["snippet"]["title"],
        "| Views:",
        video["statistics"].get("viewCount", "Unavailable")
    )


# ---- Extracted from notebook cell 3 ----
import pandas as pd
import time
from googleapiclient.errors import HttpError

TOPICS = [
    "Gaming",
    "Technology",
    "Education",
    "Fitness and Health",
    "Food and Cooking",
    "Travel and Tourism",
    "Entertainment and Movies",
    "Music",
    "Sports",
    "Finance and Investing",
    "Fashion and Beauty",
    "Science and Space",
    "Comedy",
    "News and Current Affairs",
    "Lifestyle and Vlogging",
    "Data Science and Artificial Intelligence",
    "Business and Entrepreneurship",
    "Motivation and Self-Improvement",
    "Photography and Videography",
    "Digital Marketing and Social Media"
]

videos_found = {}
errors = []

for topic in TOPICS:
    print(f"Searching: {topic}")

    try:
        response = youtube.search().list(
            part="snippet",
            q=topic,
            type="video",
            order="viewCount",
            maxResults=10,
            relevanceLanguage="en"
        ).execute()

        for item in response.get("items", []):
            video_id = item["id"].get("videoId")

            if video_id and video_id not in videos_found:
                videos_found[video_id] = {
                    "video_id": video_id,
                    "topic": topic,
                    "search_title": item["snippet"]["title"]
                }

        time.sleep(0.1)

    except HttpError as e:
        errors.append({"topic": topic, "error": str(e)})
        print(f"API error for {topic}: {e}")

print("\nUnique videos collected:", len(videos_found))
print("Topics searched:", len(TOPICS))
print("Errors:", len(errors))


# ---- Extracted from notebook cell 4 ----
from datetime import datetime, timezone
from pathlib import Path

video_ids = list(videos_found.keys())
video_details = []

for start in range(0, len(video_ids), 50):
    batch = video_ids[start:start + 50]

    try:
        response = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(batch)
        ).execute()

        for item in response.get("items", []):
            video_id = item["id"]
            base = videos_found[video_id]
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            details = item.get("contentDetails", {})

            video_details.append({
                "video_id": video_id,
                "topic": base["topic"],
                "title": snippet.get("title"),
                "channel_title": snippet.get("channelTitle"),
                "channel_id": snippet.get("channelId"),
                "published_at": snippet.get("publishedAt"),
                "description": snippet.get("description"),
                "tags": ", ".join(snippet.get("tags", [])),
                "category_id": snippet.get("categoryId"),
                "duration": details.get("duration"),
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats["likeCount"])
                    if "likeCount" in stats else None,
                "comment_count": int(stats["commentCount"])
                    if "commentCount" in stats else None,
                "collected_at": datetime.now(timezone.utc).isoformat()
            })

    except HttpError as e:
        print(f"Error retrieving batch: {e}")

df_videos = pd.DataFrame(video_details)

output_path = Path("/content/youtube_videos.csv")
df_videos.to_csv(output_path, index=False)

print("Videos saved:", len(df_videos))
print("Dataset shape:", df_videos.shape)
display(df_videos.head(10))


# ---- Extracted from notebook cell 9 ----
from googleapiclient.errors import HttpError
import pandas as pd
import time
import os

COMMENTS_FILE = "/content/youtube_comments.csv"
MAX_COMMENTS_PER_VIDEO = 100

# Resume from previously saved results if the file exists
if os.path.exists(COMMENTS_FILE):
    df_comments = pd.read_csv(COMMENTS_FILE)
    processed_ids = set(df_comments["video_id"].astype(str).unique())
else:
    df_comments = pd.DataFrame()
    processed_ids = set()

new_comments = []

for index, row in df_videos.iterrows():
    video_id = str(row["video_id"])

    if video_id in processed_ids:
        continue

    print(f"Collecting comments for {index + 1}/{len(df_videos)}: {row['title'][:60]}")

    collected_for_video = 0
    page_token = None

    try:
        while collected_for_video < MAX_COMMENTS_PER_VIDEO:
            response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(100, MAX_COMMENTS_PER_VIDEO - collected_for_video),
                pageToken=page_token,
                textFormat="plainText",
                order="relevance"
            ).execute()

            items = response.get("items", [])
            if not items:
                break

            for item in items:
                top = item["snippet"]["topLevelComment"]
                snippet = top["snippet"]

                new_comments.append({
                    "video_id": video_id,
                    "topic": row["topic"],
                    "video_title": row["title"],
                    "comment_id": top["id"],
                    "comment_text": snippet.get("textDisplay", ""),
                    "like_count": snippet.get("likeCount", 0),
                    "published_at": snippet.get("publishedAt"),
                    "reply_count": item["snippet"].get("totalReplyCount", 0)
                })

            collected_for_video += len(items)
            page_token = response.get("nextPageToken")

            if not page_token:
                break

        processed_ids.add(video_id)

    except HttpError as e:
        print("Could not collect comments:", e)
        if "quotaExceeded" in str(e):
            print("API quota exhausted. Stopping safely.")
            break
        # Videos with disabled comments may produce an API error.
        processed_ids.add(video_id)

    # Save progress after every video
    if new_comments:
        batch_df = pd.DataFrame(new_comments)
        if os.path.exists(COMMENTS_FILE):
            batch_df.to_csv(COMMENTS_FILE, mode="a", header=False, index=False)
        else:
            batch_df.to_csv(COMMENTS_FILE, index=False)
        new_comments = []

    time.sleep(0.1)

print("Comment collection finished.")
if os.path.exists(COMMENTS_FILE):
    df_comments = pd.read_csv(COMMENTS_FILE)
    print("Comments collected:", len(df_comments))
    print("Videos represented:", df_comments["video_id"].nunique())
    display(df_comments.head())
else:
    print("No comments saved yet.")

