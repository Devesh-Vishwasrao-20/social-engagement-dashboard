"""Module 4: Virality model."""



# ---- Extracted from notebook cell 23 ----
import pandas as pd
import numpy as np
import re

from datetime import datetime, timezone

df_model = pd.read_csv("/content/youtube_complete_analysis.csv")

# Convert YouTube ISO 8601 durations, e.g. PT4M20S, to seconds
def duration_to_seconds(value):
    if pd.isna(value):
        return np.nan

    value = str(value)
    match = re.fullmatch(
        r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?",
        value
    )

    if not match:
        return np.nan

    hours = float(match.group(1) or 0)
    minutes = float(match.group(2) or 0)
    seconds = float(match.group(3) or 0)

    return hours * 3600 + minutes * 60 + seconds


df_model["duration_seconds"] = (
    df_model["duration"].apply(duration_to_seconds)
)

published = pd.to_datetime(
    df_model["published_at"], errors="coerce", utc=True
)

df_model["published_month"] = published.dt.month
df_model["published_dayofweek"] = published.dt.dayofweek

collection_time = pd.Timestamp.now(tz="UTC")
df_model["video_age_days"] = (
    (collection_time - published).dt.total_seconds() / 86400
).clip(lower=0)

df_model["title_length"] = (
    df_model["title"].fillna("").str.len()
)

df_model["description_length"] = (
    df_model["description"].fillna("").str.len()
)

df_model["tag_count"] = (
    df_model["tags"].fillna("").apply(
        lambda x: 0 if not x.strip() else len(x.split(","))
    )
)

df_model["category_id"] = (
    df_model["category_id"].fillna("Unknown").astype(str)
)

df_model["topic"] = (
    df_model["topic"].fillna("Unknown").astype(str)
)

TARGET = "engagement_rate_pct"

features = [
    "topic",
    "category_id",
    "duration_seconds",
    "published_month",
    "published_dayofweek",
    "video_age_days",
    "title_length",
    "description_length",
    "tag_count"
]

# Keep rows with a valid target and essential metadata
df_model = df_model.replace([np.inf, -np.inf], np.nan)
df_model = df_model.dropna(subset=[TARGET])

# Extremely large rates can occur for videos with very few views.
# Keep them for now; inspect their distribution before interpreting results.
print("Usable videos:", len(df_model))
print("Unique videos:", df_model["video_id"].nunique())
print("\nEngagement-rate summary:")
display(df_model[TARGET].describe().to_frame())

display(df_model[["title", TARGET] + features].head())


# ---- Extracted from notebook cell 24 ----
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

categorical_features = ["topic", "category_id"]

numeric_features = [
    col for col in features
    if col not in categorical_features
]

X = df_model[features].copy()
y = df_model[TARGET].astype(float)

# A random split evaluates performance on held-out videos.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore"))
            ]),
            categorical_features
        ),
        (
            "numeric",
            SimpleImputer(strategy="median"),
            numeric_features
        )
    ]
)

model = Pipeline([
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(
        n_estimators=300,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    ))
])

baseline = DummyRegressor(strategy="mean")

baseline.fit(X_train, y_train)
model.fit(X_train, y_train)

predictions = model.predict(X_test)
baseline_predictions = baseline.predict(X_test)

results = pd.DataFrame({
    "Model": ["Mean baseline", "Random Forest"],
    "MAE": [
        mean_absolute_error(y_test, baseline_predictions),
        mean_absolute_error(y_test, predictions)
    ],
    "RMSE": [
        np.sqrt(mean_squared_error(y_test, baseline_predictions)),
        np.sqrt(mean_squared_error(y_test, predictions))
    ],
    "R2": [
        r2_score(y_test, baseline_predictions),
        r2_score(y_test, predictions)
    ]
})

display(results.round(4))

print("Test videos:", len(y_test))
print("Lower MAE and RMSE are better.")
print("R² can be negative if predictions are worse than the test-set mean.")


# ---- Extracted from notebook cell 25 ----
import matplotlib.pyplot as plt

plt.figure(figsize=(8, 6))
plt.scatter(y_test, predictions, alpha=0.7)

lower = min(y_test.min(), predictions.min())
upper = max(y_test.max(), predictions.max())

plt.plot([lower, upper], [lower, upper], linestyle="--")
plt.xlabel("Actual engagement rate (%)")
plt.ylabel("Predicted engagement rate (%)")
plt.title("Actual vs Predicted YouTube Engagement")
plt.tight_layout()
plt.savefig("/content/virality_prediction.png", dpi=150)
plt.show()


# ---- Extracted from notebook cell 26 ----
fitted_preprocessor = model.named_steps["preprocessor"]
feature_names = fitted_preprocessor.get_feature_names_out()

importances = model.named_steps["regressor"].feature_importances_

feature_importance = (
    pd.DataFrame({
        "feature": feature_names,
        "importance": importances
    })
    .sort_values("importance", ascending=False)
)

display(feature_importance.head(15))

feature_importance.head(15).sort_values(
    "importance"
).plot(
    x="feature",
    y="importance",
    kind="barh",
    legend=False,
    figsize=(10, 6)
)

plt.title("Most Influential Features in the Virality Model")
plt.xlabel("Random Forest feature importance")
plt.tight_layout()
plt.savefig("/content/feature_importance.png", dpi=150)
plt.show()


# ---- Extracted from notebook cell 27 ----
import joblib
import json

joblib.dump(model, "/content/virality_model.joblib")

prediction_output = df_model.loc[
    X_test.index, ["video_id", "title", "topic", TARGET]
].copy()

prediction_output["predicted_engagement_rate_pct"] = predictions

prediction_output.to_csv(
    "/content/virality_test_predictions.csv",
    index=False
)

with open("/content/virality_model_metrics.json", "w") as f:
    json.dump(results.to_dict(orient="records"), f, indent=2)

print("Saved model, test predictions, and evaluation metrics.")


# ---- Extracted from notebook cell 29 ----
import json

evaluation = {
    "model": "Random Forest Regressor",
    "test_videos": 40,
    "mae": 1.0726,
    "rmse": 1.3649,
    "r2": 0.1748,
    "interpretation": (
        "Modest predictive performance on one held-out test split. "
        "Further validation is needed."
    )
}

with open("/content/model_evaluation_summary.json", "w") as f:
    json.dump(evaluation, f, indent=2)

print("Model evaluation summary saved.")

