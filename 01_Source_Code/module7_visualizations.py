"""Module 7: Visualizations."""



# ---- Extracted from notebook cell 33 ----
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display

# Load your existing project datasets
df = pd.read_csv("/content/youtube_complete_analysis.csv")
topic_results = pd.read_csv("/content/topic_recommendations.csv")
recommendations = pd.read_csv("/content/engagement_recommendations.csv")

# Prepare numeric columns
numeric_columns = [
    "view_count",
    "like_count",
    "comment_count",
    "engagement_rate_pct",
    "positive_pct"
]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

print("All project datasets loaded successfully!")
print("Videos:", len(df))
print("Topics:", df["topic"].nunique())
print("Total views:", f"{df['view_count'].sum():,.0f}")
print("Total likes:", f"{df['like_count'].sum():,.0f}")
print("Total comments:", f"{df['comment_count'].sum():,.0f}")

display(topic_results.head(10))
display(recommendations)


# ---- Extracted from notebook cell 34 ----
# Average engagement rate by topic
topic_engagement = (
    df.groupby("topic", as_index=False)
      .agg(
          average_engagement=("engagement_rate_pct", "mean"),
          video_count=("video_id", "nunique")
      )
      .sort_values("average_engagement", ascending=False)
)

plt.figure(figsize=(12, 7))
sns.barplot(
    data=topic_engagement,
    x="average_engagement",
    y="topic"
)

plt.title("Average YouTube Engagement Rate by Topic")
plt.xlabel("Average Engagement Rate (%)")
plt.ylabel("Topic")
plt.tight_layout()
plt.show()


# ---- Extracted from notebook cell 35 ----
topic_metrics = (
    df.groupby("topic", as_index=False)
      .agg(
          average_views=("view_count", "mean"),
          average_likes=("like_count", "mean"),
          average_comments=("comment_count", "mean")
      )
      .sort_values("average_views", ascending=False)
)

fig, axes = plt.subplots(1, 3, figsize=(20, 8))

sns.barplot(data=topic_metrics.head(10), x="average_views", y="topic", ax=axes[0])
axes[0].set_title("Top 10 Topics by Average Views")
axes[0].set_xlabel("Average Views")

sns.barplot(data=topic_metrics.head(10), x="average_likes", y="topic", ax=axes[1])
axes[1].set_title("Top 10 Topics by Average Likes")
axes[1].set_xlabel("Average Likes")

sns.barplot(data=topic_metrics.head(10), x="average_comments", y="topic", ax=axes[2])
axes[2].set_title("Top 10 Topics by Average Comments")
axes[2].set_xlabel("Average Comments")

plt.tight_layout()
plt.show()


# ---- Extracted from notebook cell 36 ----
sentiment_counts = pd.Series({
    "Positive": df["positive_comments"].sum(),
    "Neutral": df["neutral_comments"].sum(),
    "Negative": df["negative_comments"].sum()
}).fillna(0)

plt.figure(figsize=(8, 6))
plt.pie(
    sentiment_counts,
    labels=sentiment_counts.index,
    autopct="%1.1f%%",
    startangle=90
)
plt.title("Audience Comment Sentiment Distribution")
plt.axis("equal")
plt.show()

display(sentiment_counts.to_frame("Comment Count"))


# ---- Extracted from notebook cell 37 ----
sentiment_topic = (
    df.groupby("topic", as_index=False)
      .agg(
          engagement_rate=("engagement_rate_pct", "mean"),
          positive_sentiment=("positive_pct", "mean"),
          video_count=("video_id", "nunique")
      )
      .dropna(subset=["engagement_rate", "positive_sentiment"])
)

plt.figure(figsize=(12, 7))
sns.scatterplot(
    data=sentiment_topic,
    x="positive_sentiment",
    y="engagement_rate",
    size="video_count",
    hue="topic",
    sizes=(60, 300)
)

plt.title("Topic Engagement vs Positive Audience Sentiment")
plt.xlabel("Average Positive Comments (%)")
plt.ylabel("Average Engagement Rate (%)")
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.show()


# ---- Extracted from notebook cell 38 ----
import os

output_folder = "/content/social_engagement_project"
os.makedirs(output_folder, exist_ok=True)

# Save the key analysis tables
df.to_csv(f"{output_folder}/complete_video_analysis.csv", index=False)
topic_results.to_csv(f"{output_folder}/topic_recommendations.csv", index=False)
recommendations.to_csv(f"{output_folder}/engagement_recommendations.csv", index=False)
topic_metrics.to_csv(f"{output_folder}/topic_metrics.csv", index=False)
sentiment_topic.to_csv(f"{output_folder}/topic_sentiment_comparison.csv", index=False)

# Save chart images
figures = {
    "engagement_by_topic.png": 1,
}

# Save the currently generated topic metrics chart separately
plt.figure(figsize=(10, 6))
sns.barplot(data=topic_engagement, x="average_engagement", y="topic")
plt.title("Average YouTube Engagement Rate by Topic")
plt.xlabel("Average Engagement Rate (%)")
plt.ylabel("Topic")
plt.tight_layout()
plt.savefig(f"{output_folder}/engagement_by_topic.png", dpi=200, bbox_inches="tight")
plt.close()

print("Analysis tables and engagement chart saved in:", output_folder)
print("Files:", os.listdir(output_folder))


