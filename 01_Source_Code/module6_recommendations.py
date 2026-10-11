"""Module 6: Recommendations."""



# ---- Extracted from notebook cell 30 ----
import pandas as pd
import numpy as np

df = pd.read_csv("/content/youtube_complete_analysis.csv")

# Keep valid engagement observations
df = df.dropna(subset=["topic", "engagement_rate_pct"]).copy()

topic_recommendations = (
    df.groupby("topic")
    .agg(
        video_count=("video_id", "nunique"),
        median_engagement=("engagement_rate_pct", "median"),
        mean_engagement=("engagement_rate_pct", "mean"),
        median_views=("view_count", "median"),
        mean_positive_sentiment=("positive_pct", "mean")
    )
    .reset_index()
)

# Avoid making strong recommendations from very small groups
topic_recommendations["eligible_for_ranking"] = (
    topic_recommendations["video_count"] >= 5
)

topic_recommendations = topic_recommendations.sort_values(
    ["eligible_for_ranking", "median_engagement"],
    ascending=[False, False]
)

display(topic_recommendations.round(3))

topic_recommendations.to_csv(
    "/content/topic_recommendations.csv",
    index=False
)


# ---- Extracted from notebook cell 32 ----
recommendations = []

eligible = topic_recommendations[
    topic_recommendations["video_count"] >= 5
].copy()

if not eligible.empty:
    best_topic = eligible.iloc[0]

    recommendations.append({
        "area": "Topic selection",
        "finding": (
            f"{best_topic['topic']} has the highest median "
            "engagement among eligible topics in this sample."
        ),
        "action": (
            "Test additional videos in this topic and validate "
            "the pattern on a fresh sample."
        )
    })

    positive_available = eligible.dropna(
        subset=["mean_positive_sentiment"]
    )

    if not positive_available.empty:
        best_sentiment_topic = positive_available.sort_values(
            "mean_positive_sentiment", ascending=False
        ).iloc[0]

        recommendations.append({
            "area": "Audience sentiment",
            "finding": (
                f"{best_sentiment_topic['topic']} has the highest "
                "average positive-comment percentage among eligible topics."
            ),
            "action": (
                "Review comments for recurring questions, preferences "
                "and themes; do not treat automated sentiment as ground truth."
            )
        })

recommendations.append({
    "area": "Content evaluation",
    "finding": (
        "Engagement differs across topic groups in the current sample."
    ),
    "action": (
        "Compare similar videos and account for video age, channel "
        "size and sampling bias before choosing a content strategy."
    )
})

recommendations_df = pd.DataFrame(recommendations)

display(recommendations_df)

recommendations_df.to_csv(
    "/content/engagement_recommendations.csv",
    index=False
)

print("Recommendation file saved.")

