# 📊 Social Engagement Dashboard

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-ML-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Charts-11557c?style=for-the-badge)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=for-the-badge&logo=jupyter&logoColor=white)

**A data-driven analytics project for evaluating YouTube video engagement, topic trends, sentiment, and virality patterns.**

[Dashboard](#-dashboard) · [Quick Start](#-quick-start) · [Project Structure](#-project-structure) · [Key Insights](#-key-insights)

</div>

---

## 🧭 Overview

This repository contains a complete end-to-end social media engagement analytics workflow. It analyzes YouTube video performance using engagement metrics, topic-based comparisons, sentiment evaluation, virality prediction, and statistical testing to uncover what drives audience interaction and content performance.

The project combines:
- video metadata and engagement metrics
- topic-level comparative analysis
- sentiment classification from comments
- virality prediction using ML models
- statistical significance testing
- downloadable recommendation outputs
- an interactive Streamlit dashboard

> The objective is to turn raw content performance data into actionable insights for creators, brands, and social media strategists.

---

## 🏗️ Architecture

The project is organized into seven processing modules and a dashboard layer.

```
┌───────────────────────────────────────────────────────────────────┐
│              SOCIAL ENGAGEMENT DASHBOARD PIPELINE                 │
├──────────────┬──────────────┬──────────────┬──────────────┬──────┤
│ MODULE 1     │ MODULE 2     │ MODULE 3     │ MODULE 4     │ MOD  │
│ Data         │ Cleaning &   │ Engagement  │ Virality     │ STAT │
│ Extraction   │ Sentiment    │ Analysis     │ Modeling     │ TEST │
├──────────────┴──────────────┴──────────────┴──────────────┴──────┤
│ MODULE 6 — Recommendations  │ MODULE 7 — Visualizations          │
├───────────────────────────────────────────────────────────────────┤
│                     STREAMLIT DASHBOARD / ANALYTICS               │
└───────────────────────────────────────────────────────────────────┘
```

| Module | Purpose | Key Output |
|---|---|---|
| `module1_data_extraction.py` | Extracts YouTube/video dataset information | Raw video records |
| `module2_cleaning_sentiment.py` | Cleans data and prepares sentiment signals | Processed sentiment dataset |
| `module3_engagement_analysis.py` | Computes engagement statistics | Engagement summaries |
| `module4_virality_model.py` | Builds virality prediction models | Virality prediction outputs |
| `module5_statistical_tests.py` | Runs significance testing across topics | Test result tables |
| `module6_recommendations.py` | Generates topic and engagement recommendations | Recommendation CSVs |
| `module7_visualizations.py` | Produces charts and visual summaries | PNG charts |

---

## 📊 Dashboard

The dashboard is implemented as a Streamlit app and is available here:

- `04_Dashboard/app.py`
- root-level `app.py`

Run it locally with:

```bash
streamlit run 04_Dashboard/app.py
```

The dashboard includes:
- topic comparison tables
- engagement rate analysis
- video-level exploration
- sentiment overview
- model output previews
- dataset quality checks

---

## 📁 Project Structure

```text
social-engagement-dashboard/
│
├── .gitignore
├── app.py
├── requirements.txt
├── README.md
├── complete_video_analysis.csv
├── engagement_recommendations.csv
├── topic_metrics.csv
├── topic_pairwise_tests.csv
├── topic_recommendations.csv
├── topic_sentiment_comparison.csv
├── youtube_complete_analysis.csv
├── youtube_videos.csv
├── youtube_comments.csv
├── youtube_comments_sentiment.csv
│
├── 01_Source_Code/
│   ├── main_pipeline.py
│   ├── module1_data_extraction.py
│   ├── module2_cleaning_sentiment.py
│   ├── module3_engagement_analysis.py
│   ├── module4_virality_model.py
│   ├── module5_statistical_tests.py
│   ├── module6_recommendations.py
│   └── module7_visualizations.py
│
├── 02_Datasets/
│   ├── complete_video_analysis.csv
│   ├── engagement_recommendations.csv
│   ├── topic_metrics.csv
│   ├── topic_pairwise_tests.csv
│   ├── topic_recommendations.csv
│   ├── topic_sentiment_comparison.csv
│   ├── virality_test_predictions.csv
│   ├── youtube_comments.csv
│   ├── youtube_comments_sentiment.csv
│   ├── youtube_complete_analysis.csv
│   └── youtube_videos.csv
│
├── 03_Charts/
│   ├── engagement_analysis.png
│   ├── sentiment_analysis.png
│   ├── topic_analysis.png
│   └── virality_analysis.png
│
├── 04_Dashboard/
│   └── app.py
│
├── 05_Report/
│   ├── project_report.docx
│   └── project_report.pdf
│
├── 06_Notebook/
│   └── Social_Engagement_Initiative_Organized.ipynb
│
├── 07_Models_JSON/
│   ├── analysis_summary.json
│   └── model_metrics.json
│
└── .github/
```

---

## ⚡ Quick Start

### 1) Clone the repository

```bash
git clone https://github.com/Devesh-Vishwasrao-20/social-engagement-dashboard.git
cd social-engagement-dashboard
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Run the Streamlit dashboard

```bash
streamlit run 04_Dashboard/app.py
```

### 4) Run the full pipeline (optional)

```bash
python 01_Source_Code/main_pipeline.py
```

---

## 🧪 Data Sources and Outputs

This project uses YouTube video and comment data for social engagement analysis. The main data files include:

- `youtube_videos.csv` — video metadata and summary statistics
- `youtube_complete_analysis.csv` — enriched full analysis dataset
- `youtube_comments.csv` — raw comment data
- `youtube_comments_sentiment.csv` — sentiment-tagged comment results
- `complete_video_analysis.csv` — combined analysis dataset
- `topic_metrics.csv` — topic-level engagement metrics
- `topic_pairwise_tests.csv` — pairwise statistical test results
- `topic_recommendations.csv` — suggested content themes
- `engagement_recommendations.csv` — engagement recommendations
- `virality_test_predictions.csv` — virality model outputs

---

## 🔍 Key Insights

The analysis focuses on identifying which content characteristics influence audience engagement and growth. The project evaluates:

- topic-level performance differences
- engagement rate patterns by content type and theme
- sentiment distributions across comments
- virality signals from video metrics
- statistical significance between topic groups
- recommendation outputs for future content strategy

Example areas studied:
- video views vs engagement relationship
- topic-based audience response
- comment sentiment patterns
- statistical significance of topic differences
- recommendation generation for future content scheduling and positioning

---

## 📈 Methodology

The workflow follows a standard analytics pipeline:

1. Data extraction from YouTube-related sources
2. Data cleaning and normalization
3. Engagement metric derivation
4. Sentiment analysis on comments
5. Topic comparison and statistical testing
6. Virality model generation and evaluation
7. Recommendation generation
8. Visualization and dashboard presentation

This project combines descriptive analytics and predictive modeling to support content performance understanding.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Data Processing | Python, Pandas, NumPy |
| Visualization | Matplotlib, Seaborn, Plotly |
| Dashboard | Streamlit |
| Modeling | Scikit-learn |
| Statistics | SciPy |
| Notebook | Jupyter |
| Reporting | Word/PDF export |

---

## 📦 Model and Recommendation Files

The repository also stores the final model/analysis outputs in the `07_Models_JSON` folder:

- `analysis_summary.json`
- `model_metrics.json`

These files summarize the analytical findings and quantitative model results used in the evaluation workflow.

---

## ✅ Deliverables

This project includes the following outputs:

- interactive Streamlit dashboard
- topic and engagement recommendation CSVs
- visual charts in `03_Charts/`
- notebook in `06_Notebook/`
- PDF/DOCX project report in `05_Report/`
- JSON model summaries in `07_Models_JSON/`

---

## 📄 License

This project is intended for educational, research, and portfolio use.

---

<div align="center">

Built with ❤️ using Python · Streamlit · Pandas · Scikit-learn · Matplotlib

⭐ If this project helped you, give it a star on GitHub. ⭐

</div>
