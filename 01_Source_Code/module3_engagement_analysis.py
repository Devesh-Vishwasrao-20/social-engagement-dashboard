"""Module 3: Engagement analysis."""



# ---- Extracted from notebook cell 17 ----
import pandas as pd
import numpy as np

df_videos = pd.read_csv("/content/youtube_videos.csv")
df_comments = pd.read_csv("/content/youtube_comments_sentiment.csv")

# Convert numeric fields safely
for col in ["view_count", "like_count", "comment_count"]:
    df_videos[col] = pd.to_numeric(
        df_videos[col], errors="coerce"
    )

# Calculate engagement metrics
df_videos["engagement_rate_pct"] = np.where(
    df_videos["view_count"] > 0,
    (
        df_videos["like_count"].fillna(0)
        + df_videos["comment_count"].fillna(0)
    ) / df_videos["view_count"] * 100,
    np.nan
)

df_videos["like_rate_pct"] = np.where(
    df_videos["view_count"] > 0,
    df_videos["like_count"] / df_videos["view_count"] * 100,
    np.nan
)

df_videos["comment_rate_pct"] = np.where(
    df_videos["view_count"] > 0,
    df_videos["comment_count"] / df_videos["view_count"] * 100,
    np.nan
)

display(
    df_videos[
        ["title", "topic", "view_count", "like_count",
         "comment_count", "engagement_rate_pct"]
    ].head(10)
)


# ---- Extracted from notebook cell 18 ----
comment_summary = (
    df_comments.groupby("video_id")
    .agg(
        analyzed_comments=("sentiment", "size"),
        positive_comments=(
            "sentiment", lambda s: (s == "Positive").sum()
        ),
        neutral_comments=(
            "sentiment", lambda s: (s == "Neutral").sum()
        ),
        negative_comments=(
            "sentiment", lambda s: (s == "Negative").sum()
        ),
        average_sentiment_score=("sentiment_score", "mean")
    )
    .reset_index()
)

comment_summary["positive_pct"] = (
    comment_summary["positive_comments"]
    / comment_summary["analyzed_comments"] * 100
)

df_analysis = df_videos.merge(
    comment_summary, on="video_id", how="left"
)

print("Videos in combined dataset:", len(df_analysis))
print(
    "Videos with analyzed comments:",
    df_analysis["analyzed_comments"].notna().sum()
)

display(df_analysis.head())


# ---- Extracted from notebook cell 19 ----
topic_performance = (
    df_analysis.groupby("topic")
    .agg(
        video_count=("video_id", "nunique"),
        average_views=("view_count", "mean"),
        average_engagement_rate=("engagement_rate_pct", "mean"),
        average_like_rate=("like_rate_pct", "mean"),
        average_comment_rate=("comment_rate_pct", "mean"),
        average_positive_sentiment=("positive_pct", "mean")
    )
    .sort_values("average_engagement_rate", ascending=False)
    .reset_index()
)

display(topic_performance.round(2))

topic_performance.to_csv(
    "/content/topic_performance.csv", index=False
)


# ---- Extracted from notebook cell 20 ----
import matplotlib.pyplot as plt

plot_data = topic_performance.dropna(
    subset=["average_engagement_rate"]
).sort_values("average_engagement_rate")

plt.figure(figsize=(12, 8))
plt.barh(
    plot_data["topic"],
    plot_data["average_engagement_rate"]
)
plt.xlabel("Average engagement rate (%)")
plt.ylabel("Topic")
plt.title("Average YouTube Engagement Rate by Topic")
plt.tight_layout()
plt.savefig("/content/topic_engagement.png", dpi=150)
plt.show()


# ---- Extracted from notebook cell 21 ----
ranked_videos = df_analysis.sort_values(
    "engagement_rate_pct", ascending=False
)

display(
    ranked_videos[
        ["title", "topic", "view_count", "like_count",
         "comment_count", "engagement_rate_pct",
         "positive_pct"]
    ].head(20)
)

ranked_videos.to_csv(
    "/content/video_engagement_analysis.csv", index=False
)


# ---- Extracted from notebook cell 22 ----
df_analysis.to_csv(
    "/content/youtube_complete_analysis.csv",
    index=False
)

print("Saved successfully!")
print("Rows:", len(df_analysis))
print("Columns:", len(df_analysis.columns))

