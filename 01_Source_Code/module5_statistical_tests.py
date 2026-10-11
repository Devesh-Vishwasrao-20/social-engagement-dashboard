"""Module 5: Statistical tests."""


# ---- Extracted from notebook cell 28 ----
import pandas as pd
import numpy as np
from scipy.stats import kruskal

df_analysis = pd.read_csv(
    "/content/youtube_complete_analysis.csv"
)

# Use valid engagement values and require at least 3 videos per topic
valid = df_analysis.dropna(
    subset=["topic", "engagement_rate_pct"]
).copy()

groups = [
    group["engagement_rate_pct"].values
    for _, group in valid.groupby("topic")
    if len(group) >= 3
]

topic_sizes = valid.groupby("topic").size()

print("Videos per topic:")
display(topic_sizes.sort_values(ascending=False).to_frame("video_count"))

if len(groups) >= 2:
    statistic, p_value = kruskal(*groups)

    print(f"Kruskal-Wallis statistic: {statistic:.4f}")
    print(f"P-value: {p_value:.6f}")

    if p_value < 0.05:
        print("Result: At least one topic's engagement distribution differs.")
    else:
        print("Result: No statistically significant difference detected.")
else:
    print("Not enough topic groups with at least 3 videos each.")


# ---- Extracted from notebook cell 31 ----
from itertools import combinations
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests

eligible_topics = (
    topic_recommendations.loc[
        topic_recommendations["video_count"] >= 5,
        "topic"
    ].tolist()
)

pair_results = []

for topic_a, topic_b in combinations(eligible_topics, 2):
    a = df.loc[
        df["topic"] == topic_a, "engagement_rate_pct"
    ].dropna()

    b = df.loc[
        df["topic"] == topic_b, "engagement_rate_pct"
    ].dropna()

    if len(a) >= 5 and len(b) >= 5:
        result = mannwhitneyu(
            a, b, alternative="two-sided"
        )

        pair_results.append({
            "topic_a": topic_a,
            "topic_b": topic_b,
            "median_a": a.median(),
            "median_b": b.median(),
            "raw_p_value": result.pvalue
        })

pairwise_df = pd.DataFrame(pair_results)

if not pairwise_df.empty:
    pairwise_df["adjusted_p_value"] = multipletests(
        pairwise_df["raw_p_value"],
        method="bonferroni"
    )[1]

    pairwise_df["significant_at_0_05"] = (
        pairwise_df["adjusted_p_value"] < 0.05
    )

    display(
        pairwise_df.sort_values("adjusted_p_value").head(20)
    )

    pairwise_df.to_csv(
        "/content/topic_pairwise_tests.csv",
        index=False
    )
else:
    print(
        "Not enough topic groups with at least five videos "
        "for pairwise comparisons."
    )

