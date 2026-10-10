import os
import json
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# ---------------- Page setup ----------------
st.set_page_config(
    page_title="Social Engagement Analytics",
    page_icon="📊",
    layout="wide"
)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

st.title("📊 Social Media Engagement Analytics")
st.caption("Data-driven insights, audience sentiment and virality prediction")

# ---------------- Load data ----------------
@st.cache_data
def load_data():
    path = os.path.join(DATA_DIR, "complete_video_analysis.csv")
    if not os.path.exists(path):
        path = os.path.join(DATA_DIR, "youtube_complete_analysis.csv")

    df = pd.read_csv(path)

    numeric_cols = [
        "view_count", "like_count", "comment_count",
        "engagement_rate_pct", "positive_pct",
        "average_sentiment_score"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

df = load_data()

# ---------------- Sidebar filters ----------------
st.sidebar.header("Dashboard Filters")

if "topic" in df.columns:
    topics = sorted(df["topic"].dropna().astype(str).unique().tolist())
    selected_topics = st.sidebar.multiselect(
        "Select topics",
        topics,
        default=topics
    )
    filtered = df[df["topic"].astype(str).isin(selected_topics)].copy()
else:
    filtered = df.copy()

if "channel_title" in filtered.columns:
    channels = sorted(
        filtered["channel_title"].dropna().astype(str).unique().tolist()
    )
    selected_channels = st.sidebar.multiselect(
        "Select channels",
        channels
    )
    if selected_channels:
        filtered = filtered[
            filtered["channel_title"].astype(str).isin(selected_channels)
        ]

if filtered.empty:
    st.warning("No videos match the selected filters.")
    st.stop()

# ---------------- KPI metrics ----------------
def total_or_zero(column):
    return filtered[column].fillna(0).sum() if column in filtered.columns else 0

def average_or_zero(column):
    return filtered[column].mean() if column in filtered.columns else 0

views = total_or_zero("view_count")
likes = total_or_zero("like_count")
comments = total_or_zero("comment_count")
avg_engagement = average_or_zero("engagement_rate_pct")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Videos Analyzed", f"{len(filtered):,}")
c2.metric("Total Views", f"{views:,.0f}")
c3.metric("Total Likes", f"{likes:,.0f}")
c4.metric("Avg. Engagement Rate", f"{avg_engagement:.2f}%")

st.caption(
    "Engagement rate is calculated from likes and comments divided by views. "
    "It does not include shares, saves or watch-time retention."
)

# ---------------- Tabs ----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Engagement",
    "💬 Sentiment",
    "🎬 Video Explorer",
    "📥 Downloads"
])

with tab1:
    st.subheader("Average Engagement Rate by Topic")

    if {"topic", "engagement_rate_pct"}.issubset(filtered.columns):
        topic_engagement = (
            filtered.groupby("topic", dropna=False)["engagement_rate_pct"]
            .mean()
            .sort_values(ascending=False)
        )

        fig, ax = plt.subplots(figsize=(10, 5))
        topic_engagement.plot(kind="bar", ax=ax)
        ax.set_xlabel("Topic")
        ax.set_ylabel("Average engagement rate (%)")
        ax.set_title("Average Engagement by Topic")
        ax.tick_params(axis="x", labelrotation=45)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        st.dataframe(
            topic_engagement.rename("Average engagement rate (%)")
            .reset_index(),
            use_container_width=True
        )

    st.subheader("Views, Likes and Comments")
    count_cols = [
        col for col in ["view_count", "like_count", "comment_count"]
        if col in filtered.columns
    ]

    if "topic" in filtered.columns and count_cols:
        counts = filtered.groupby("topic")[count_cols].sum()
        st.bar_chart(counts)

with tab2:
    st.subheader("Audience Sentiment")

    sentiment_cols = [
        col for col in [
            "positive_comments", "neutral_comments", "negative_comments"
        ] if col in filtered.columns
    ]

    if sentiment_cols:
        sentiment_totals = filtered[sentiment_cols].fillna(0).sum()
        labels = [
            col.replace("_comments", "").capitalize()
            for col in sentiment_cols
        ]

        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie(
            sentiment_totals.values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90
        )
        ax.set_title("Comment Sentiment Distribution")
        st.pyplot(fig)
        plt.close(fig)

        st.dataframe(
            pd.DataFrame({
                "Sentiment": labels,
                "Comment count": sentiment_totals.values.astype(int)
            }),
            use_container_width=True
        )
    else:
        st.info("Comment sentiment columns were not found in this dataset.")

    if {"topic", "positive_pct"}.issubset(filtered.columns):
        st.subheader("Positive Sentiment by Topic")
        sentiment_by_topic = (
            filtered.groupby("topic")["positive_pct"]
            .mean()
            .sort_values(ascending=False)
        )
        st.bar_chart(sentiment_by_topic)

with tab3:
    st.subheader("Explore Videos")

    search_text = st.text_input("Search video titles or channels")

    videos = filtered.copy()
    if search_text:
        mask = pd.Series(False, index=videos.index)
        for col in ["title", "channel_title"]:
            if col in videos.columns:
                mask |= videos[col].fillna("").astype(str).str.contains(
                    search_text, case=False, regex=False
                )
        videos = videos[mask]

    preferred_cols = [
        "title", "channel_title", "topic", "view_count",
        "like_count", "comment_count", "engagement_rate_pct",
        "positive_pct"
    ]
    display_cols = [col for col in preferred_cols if col in videos.columns]

    st.write(f"Matching videos: {len(videos):,}")
    st.dataframe(
        videos[display_cols],
        use_container_width=True,
        hide_index=True
    )

with tab4:
    st.subheader("Download Project Data")

    st.download_button(
        "Download filtered video analysis (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="filtered_video_analysis.csv",
        mime="text/csv"
    )

    for filename in [
        "topic_recommendations.csv",
        "engagement_recommendations.csv",
        "topic_metrics.csv",
        "topic_pairwise_tests.csv",
        "topic_sentiment_comparison.csv"
    ]:
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, "rb") as file:
                st.download_button(
                    f"Download {filename}",
                    data=file.read(),
                    file_name=filename,
                    mime="text/csv",
                    key=filename
                )

st.divider()
st.caption(
    "Academic project dashboard. Sentiment labels and engagement patterns "
    "are estimates from the collected YouTube sample, not causal conclusions."
)
