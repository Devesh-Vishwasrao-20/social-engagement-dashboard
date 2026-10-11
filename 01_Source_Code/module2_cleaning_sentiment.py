"""Module 2: Cleaning and sentiment analysis."""


# ---- Extracted from notebook cell 11 ----
import pandas as pd
import numpy as np
import os

COMMENTS_FILE = "/content/youtube_comments.csv"
VIDEO_FILE = "/content/youtube_videos.csv"

df_comments = pd.read_csv(COMMENTS_FILE)
df_videos = pd.read_csv(VIDEO_FILE)

df_comments["comment_text"] = (
    df_comments["comment_text"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df_comments = df_comments[
    df_comments["comment_text"].ne("")
].drop_duplicates(subset=["comment_id"])

print("Clean comments:", len(df_comments))
print("Videos with comments:", df_comments["video_id"].nunique())
print("Missing comment text:", df_comments["comment_text"].isna().sum())

display(df_comments.head())


# ---- Extracted from notebook cell 12 ----
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def classify_sentiment(text):
    score = analyzer.polarity_scores(str(text))["compound"]

    if score >= 0.05:
        label = "Positive"
    elif score <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    return pd.Series([score, label])

df_comments[["sentiment_score", "sentiment"]] = (
    df_comments["comment_text"]
    .apply(classify_sentiment)
)

print("Sentiment analysis completed.")
display(df_comments[
    ["topic", "comment_text", "sentiment_score", "sentiment"]
].head(10))


# ---- Extracted from notebook cell 13 ----
import matplotlib.pyplot as plt

sentiment_counts = df_comments["sentiment"].value_counts()

sentiment_counts.plot(kind="bar", figsize=(8, 5))
plt.title("YouTube Audience Sentiment Distribution")
plt.xlabel("Sentiment")
plt.ylabel("Number of Comments")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

print(sentiment_counts)


# ---- Extracted from notebook cell 14 ----
topic_sentiment = pd.crosstab(
    df_comments["topic"],
    df_comments["sentiment"],
    normalize="index"
) * 100

display(topic_sentiment.round(2))

topic_sentiment.plot(
    kind="bar",
    stacked=True,
    figsize=(14, 6)
)

plt.title("Sentiment Distribution by YouTube Topic")
plt.xlabel("Topic")
plt.ylabel("Percentage of Comments")
plt.legend(title="Sentiment")
plt.xticks(rotation=60, ha="right")
plt.tight_layout()
plt.show()


# ---- Extracted from notebook cell 15 ----
OUTPUT_FILE = "/content/youtube_comments_sentiment.csv"

df_comments.to_csv(OUTPUT_FILE, index=False)

print("Saved:", OUTPUT_FILE)
print("Rows:", len(df_comments))

