from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Social Engagement Analytics", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
ROOT = Path(__file__).resolve().parent

st.markdown("""
<style>
.stApp{background:#0b1020;color:#eef3fb}.block-container{max-width:1500px;padding-top:1.4rem}
[data-testid="stSidebar"]{background:#111827;border-right:1px solid #29374d}
div[data-testid="stMetric"]{background:linear-gradient(145deg,#172238,#101827);border:1px solid #2b3951;padding:14px;border-radius:14px}
div[data-testid="stMetricLabel"] p{color:#aab8cc}div[data-testid="stMetricValue"]{color:#f3f6fc}
.hero{padding:1.2rem 1.5rem;border-radius:18px;background:linear-gradient(120deg,#16223b,#142a36 60%,#211b3c);border:1px solid #30435d;margin-bottom:1rem}
.hero p{color:#b8c6da;margin-bottom:.2rem}.muted{color:#9caec5;font-size:.88rem}
</style>
<div class="hero"><h1>📊 Social Media Engagement Analytics</h1><p><b>The Data-Driven Social Engagement Initiative</b></p><p>Video performance · Topic comparison · Audience sentiment · Existing model outputs</p></div>
""", unsafe_allow_html=True)
st.caption("Descriptive analytics based on supplied project data. Associations do not prove causation; predictions and sentiment labels are estimates produced upstream.")


def num(s):
    return pd.to_numeric(s, errors="coerce")


def fmt_count(x):
    if pd.isna(x): return "N/A"
    x=float(x); a=abs(x)
    if a>=1e9: return f"{x/1e9:.2f}B"
    if a>=1e6: return f"{x/1e6:.2f}M"
    if a>=1e4: return f"{x/1e3:.1f}K"
    return f"{x:,.0f}"


def mean_safe(s):
    s=num(s).replace([np.inf,-np.inf],np.nan).dropna()
    return float(s.mean()) if not s.empty else np.nan


def theme(ax):
    ax.set_facecolor("#111827"); ax.tick_params(colors="#c7d2e2",labelsize=9)
    ax.xaxis.label.set_color("#c7d2e2"); ax.yaxis.label.set_color("#c7d2e2"); ax.title.set_color("#f3f6fc")
    for sp in ax.spines.values(): sp.set_color("#344258")
    ax.grid(axis="y",color="#2b3951",alpha=.55); ax.set_axisbelow(True)


@st.cache_data(show_spinner=False)
def read_csv(path):
    try:
        df=pd.read_csv(path,low_memory=False); df.columns=[str(c).strip() for c in df.columns]; return df
    except Exception:
        return None

# Prefer the same primary datasets as the existing app; fallback only if unavailable.
main_path=next((ROOT/n for n in ["complete_video_analysis.csv","youtube_complete_analysis.csv","youtube_videos.csv"] if (ROOT/n).exists()),None)
if main_path is None:
    st.error("Main video CSV not found. Put complete_video_analysis.csv or youtube_complete_analysis.csv beside app.py in the GitHub repository.")
    st.stop()
data=read_csv(main_path)
if data is None or data.empty:
    st.error(f"Could not read {main_path.name}, or it contains no data rows.")
    st.stop()

# Normalise only known fields. Optional fields remain optional and are never fabricated.
for c in ["view_count","like_count","comment_count","engagement_rate_pct","like_rate_pct","comment_rate_pct","positive_pct","average_sentiment_score","positive_comments","neutral_comments","negative_comments","analyzed_comments","duration_seconds","video_age_days","title_length","description_length","tag_count"]:
    if c in data.columns: data[c]=num(data[c])
for c,default in [("topic","Unknown"),("title","Untitled"),("channel_title","Unknown"),("video_id","Unknown")]:
    if c not in data.columns: data[c]=default
    data[c]=data[c].fillna(default).astype(str)
for c in ["view_count","like_count","comment_count","engagement_rate_pct"]:
    if c not in data.columns: data[c]=np.nan
if "engagement_rate_pct" in data.columns:
    missing=data["engagement_rate_pct"].isna()
    if all(c in data.columns for c in ["view_count","like_count","comment_count"]):
        valid=missing & data["view_count"].gt(0)
        data.loc[valid,"engagement_rate_pct"]=(data.loc[valid,"like_count"]+data.loc[valid,"comment_count"])/data.loc[valid,"view_count"]*100
    data["engagement_rate_pct"]=data["engagement_rate_pct"].replace([np.inf,-np.inf],np.nan)
if "published_at" in data.columns: data["published_at"]=pd.to_datetime(data["published_at"],errors="coerce",utc=True)

# Sidebar controls
st.sidebar.title("🎛️ Explore the data")
st.sidebar.caption(f"Source: {main_path.name} · {len(data):,} rows")
topics=sorted(data.topic.dropna().unique().tolist()); channels=sorted(data.channel_title.dropna().unique().tolist())
sel_topics=st.sidebar.multiselect("Topics",topics,default=topics)
sel_channels=st.sidebar.multiselect("Channels",channels,default=channels)
filtered=data[data.topic.isin(sel_topics)&data.channel_title.isin(sel_channels)].copy()
if "published_at" in data.columns and data.published_at.notna().any():
    d=data.published_at.dropna(); lo=d.min().date(); hi=d.max().date()
    dates=st.sidebar.date_input("Publication date range",value=(lo,hi),min_value=lo,max_value=hi)
    if isinstance(dates,(tuple,list)) and len(dates)==2:
        fd=filtered.published_at.dt.date
        filtered=filtered[fd.isna()|((fd>=dates[0])&(fd<=dates[1]))]
st.sidebar.caption(f"Showing {len(filtered):,} of {len(data):,} rows")
if filtered.empty: st.warning("No rows match these filters. Select more topics or channels."); st.stop()

# KPI summary
st.subheader("At a glance")
a,b,c,d,e=st.columns(5)
a.metric("Videos",f"{len(filtered):,}")
views=num(filtered.view_count).sum(min_count=1); likes=num(filtered.like_count).sum(min_count=1); comments=num(filtered.comment_count).sum(min_count=1)
avg=mean_safe(filtered.engagement_rate_pct); med=num(filtered.engagement_rate_pct).median()
b.metric("Total views",fmt_count(views)); c.metric("Total likes",fmt_count(likes)); d.metric("Total comments",fmt_count(comments)); e.metric("Avg. engagement",f"{avg:.2f}%" if pd.notna(avg) else "N/A")
a,b,c=st.columns(3); a.metric("Median engagement",f"{med:.2f}%" if pd.notna(med) else "N/A"); b.metric("Topics",f"{filtered.topic.nunique():,}"); c.metric("Channels",f"{filtered.channel_title.nunique():,}")
st.caption("Engagement rate = (likes + comments) ÷ views × 100 when the supplied rate is missing and views are positive. This proxy excludes shares, saves, and watch-time retention.")

overview,topic_tab,video_tab,sentiment_tab,models_tab,quality_tab=st.tabs(["📈 Overview","🧭 Topic comparison","🎬 Video explorer","💬 Sentiment","🧪 Model outputs","🗂️ Data quality"])
with overview:
    left,right=st.columns(2)
    topic_perf=filtered.groupby("topic").agg(videos=("video_id","count"),avg_engagement=("engagement_rate_pct","mean")).dropna(subset=["avg_engagement"]).sort_values("avg_engagement")
    with left:
        st.markdown("#### Average engagement by topic")
        if not topic_perf.empty:
            fig,ax=plt.subplots(figsize=(8,4.5)); ax.barh(topic_perf.index,topic_perf.avg_engagement,color="#4f9cf9"); ax.set_xlabel("Average engagement rate (%)"); ax.set_title("Average engagement by topic"); theme(ax); fig.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close(fig)
        else: st.info("No valid engagement rates available for this chart.")
    with right:
        st.markdown("#### Views vs. engagement")
        sc=filtered[["view_count","engagement_rate_pct"]].replace([np.inf,-np.inf],np.nan).dropna(); sc=sc[sc.view_count>0]
        if not sc.empty:
            fig,ax=plt.subplots(figsize=(8,4.5)); ax.scatter(sc.view_count,sc.engagement_rate_pct,alpha=.7,color="#35c9a5",edgecolors="none"); ax.set_xscale("log"); ax.set_xlabel("Views (log scale)"); ax.set_ylabel("Engagement rate (%)"); ax.set_title("Observed views and engagement"); theme(ax); fig.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close(fig)
            corr=sc.view_count.corr(sc.engagement_rate_pct,method="spearman")
            if pd.notna(corr): st.caption(f"Spearman rank correlation: {corr:.3f}. Association is not causation.")
        else: st.info("Not enough positive views and engagement values for a scatter plot.")
    vals=num(filtered.engagement_rate_pct).replace([np.inf,-np.inf],np.nan).dropna()
    st.markdown("#### Engagement distribution")
    if len(vals):
        fig,ax=plt.subplots(figsize=(10,3.3)); ax.hist(vals,bins=min(25,max(5,int(np.sqrt(len(vals)))),),color="#a78bfa",edgecolor="#111827"); ax.set_xlabel("Engagement rate (%)"); ax.set_ylabel("Videos"); ax.set_title("Distribution of engagement rate"); theme(ax); fig.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close(fig)
    else: st.info("No engagement-rate values available.")
    if "published_at" in filtered.columns and filtered.published_at.notna().any():
        dated=filtered.dropna(subset=["published_at"]).copy(); dated["month"]=dated.published_at.dt.to_period("M").astype(str); trend=dated.groupby("month").engagement_rate_pct.mean()
        st.markdown("#### Publication-month trend")
        fig,ax=plt.subplots(figsize=(10,3.3)); ax.plot(trend.index,trend.values,marker="o",color="#f59e0b"); ax.tick_params(axis="x",rotation=35); ax.set_xlabel("Publication month"); ax.set_ylabel("Average engagement (%)"); ax.set_title("Average engagement by publication month"); theme(ax); fig.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close(fig)
        st.caption("Monthly averages are descriptive and depend on which videos are present in each month.")

with topic_tab:
    st.markdown("#### Topic performance table")
    tt=filtered.groupby("topic",dropna=False).agg(videos=("video_id","count"),avg_views=("view_count","mean"),median_views=("view_count","median"),avg_likes=("like_count","mean"),avg_comments=("comment_count","mean"),avg_engagement_pct=("engagement_rate_pct","mean"),median_engagement_pct=("engagement_rate_pct","median")).reset_index().sort_values("avg_engagement_pct",ascending=False,na_position="last")
    st.dataframe(tt.round(3),use_container_width=True,hide_index=True)
    st.download_button("⬇️ Download topic comparison CSV",tt.to_csv(index=False).encode(),"topic_comparison.csv","text/csv")
    corr_cols=[x for x in ["view_count","like_count","comment_count","engagement_rate_pct","duration_seconds","video_age_days","title_length","tag_count"] if x in filtered.columns and num(filtered[x]).notna().sum()>1]
    if len(corr_cols)>=2:
        st.markdown("#### Correlation matrix (available numeric fields)")
        cm=filtered[corr_cols].apply(num).corr(method="spearman")
        fig,ax=plt.subplots(figsize=(8,5)); im=ax.imshow(cm.values,cmap="coolwarm",vmin=-1,vmax=1,aspect="auto"); ax.set_xticks(range(len(cm.columns)),cm.columns,rotation=40,ha="right"); ax.set_yticks(range(len(cm.index)),cm.index); ax.set_title("Spearman correlation")
        for i in range(len(cm.index)):
            for j in range(len(cm.columns)):
                v=cm.iloc[i,j]
                if pd.notna(v): ax.text(j,i,f"{v:.2f}",ha="center",va="center",fontsize=8,color="black" if abs(v)>.55 else "white")
        fig.colorbar(im,ax=ax,fraction=.035,pad=.04); fig.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close(fig)
        st.caption("Correlations do not prove causation; some measures may share a formula.")

with video_tab:
    st.markdown("#### Search, sort, and inspect videos")
    query=st.text_input("Search title, channel, topic, or video ID",placeholder="Enter a keyword")
    res=filtered.copy()
    if query.strip():
        q=query.strip().casefold(); mask=False
        for col in ["title","channel_title","topic","video_id"]: mask=mask | res[col].astype(str).str.casefold().str.contains(q,regex=False,na=False)
        res=res[mask]
    sort_cols=[x for x in ["engagement_rate_pct","view_count","like_count","comment_count","published_at","title"] if x in res.columns]
    sort_col=st.selectbox("Sort results by",sort_cols) if sort_cols else None
    desc=st.checkbox("Highest / newest first",value=True)
    if sort_col: res=res.sort_values(sort_col,ascending=not desc,na_position="last")
    st.write(f"**{len(res):,}** matching videos")
    show_cols=[x for x in ["title","channel_title","topic","view_count","like_count","comment_count","engagement_rate_pct","positive_pct","published_at","video_id"] if x in res.columns]
    st.dataframe(res[show_cols].round(3),use_container_width=True,hide_index=True,height=420)
    st.download_button("⬇️ Download filtered videos CSV",res.to_csv(index=False).encode(),"filtered_video_analysis.csv","text/csv")
    if not res.empty:
        ids=res.index.tolist(); selected=st.selectbox("Inspect a video row",ids,format_func=lambda i:f"{res.loc[i,'title'][:80]} — {res.loc[i,'channel_title']}")
        with st.expander("Selected video details"):
            row=res.loc[selected]; st.json({str(k):(v.isoformat() if isinstance(v,pd.Timestamp) else (v.item() if isinstance(v,np.generic) else v)) for k,v in row.items() if pd.notna(v)})

with sentiment_tab:
    st.markdown("#### Supplied comment sentiment")
    scols=["positive_comments","neutral_comments","negative_comments"]
    if all(x in filtered.columns for x in scols):
        totals=filtered[scols].apply(num).sum(min_count=1).fillna(0).clip(lower=0)
        if totals.sum()>0:
            l,r=st.columns(2)
            with l:
                fig,ax=plt.subplots(figsize=(6,4.5)); ax.pie(totals.values,labels=["Positive","Neutral","Negative"],autopct="%1.1f%%",startangle=90,textprops={"color":"white"}); ax.set_title("Supplied sentiment class counts",color="#f3f6fc"); fig.patch.set_facecolor("#0b1020"); ax.set_facecolor("#0b1020"); st.pyplot(fig,use_container_width=True); plt.close(fig)
            with r:
                st.metric("Classified comments (sum)",fmt_count(totals.sum())); st.metric("Positive share",f"{totals['positive_comments']/totals.sum()*100:.2f}%"); st.metric("Negative share",f"{totals['negative_comments']/totals.sum()*100:.2f}%")
            st.caption("Uses existing class-count columns; this dashboard does not reclassify comments.")
        else: st.info("Sentiment columns exist, but no positive counts are available in this filtered selection.")
    elif "positive_pct" in filtered.columns:
        p=num(filtered.positive_pct).dropna()
        if not p.empty:
            st.metric("Mean supplied positive percentage",f"{p.mean():.2f}%")
            st.caption("Only positive_pct exists here; neutral and negative shares are not inferred.")
            by_topic=filtered.groupby("topic").positive_pct.apply(mean_safe).dropna().sort_values(ascending=False)
            if not by_topic.empty: st.bar_chart(by_topic)
        else: st.info("positive_pct is present but has no numeric values.")
    else: st.info("No recognized sentiment summary columns were found in the main dataset.")
    if "average_sentiment_score" in filtered.columns:
        score=filtered.groupby("topic").average_sentiment_score.apply(mean_safe).dropna().sort_values(ascending=False)
        if not score.empty: st.markdown("#### Average sentiment score by topic"); st.bar_chart(score); st.caption("Interpretation depends on the upstream sentiment method.")
    comments=read_csv(ROOT/"youtube_comments_sentiment.csv") if (ROOT/"youtube_comments_sentiment.csv").exists() else None
    if comments is not None:
        st.markdown("#### Comment-level results"); st.caption(f"youtube_comments_sentiment.csv · {len(comments):,} rows"); st.dataframe(comments.head(100),use_container_width=True,hide_index=True); st.download_button("⬇️ Download comment sentiment data",comments.to_csv(index=False).encode(),"youtube_comments_sentiment.csv","text/csv")

with models_tab:
    st.markdown("#### Existing project model and recommendation outputs")
    files=[("Topic recommendations","topic_recommendations.csv"),("Engagement recommendations","engagement_recommendations.csv"),("Virality test predictions","virality_test_predictions.csv"),("Topic pairwise tests","topic_pairwise_tests.csv"),("Topic sentiment comparison","topic_sentiment_comparison.csv"),("Topic metrics","topic_metrics.csv")]
    found=False
    for label,name in files:
        path=ROOT/name
        if path.exists():
            df=read_csv(path)
            if df is not None:
                found=True
                with st.expander(f"{label} · {len(df):,} rows",expanded=(name=="engagement_recommendations.csv")):
                    st.caption(f"Source: {name}. These are existing project outputs, not generated by this dashboard.")
                    st.dataframe(df.head(500),use_container_width=True,hide_index=True)
                    st.download_button(f"⬇️ Download {name}",df.to_csv(index=False).encode(),name,"text/csv",key=f"dl_{name}")
    if not found: st.info("No optional result CSVs found. Add existing output files beside app.py to display them.")

with quality_tab:
    st.markdown("#### Main dataset quality report")
    q1,q2,q3=st.columns(3); q1.metric("Rows",f"{len(data):,}"); q2.metric("Columns",f"{len(data.columns):,}"); q3.metric("Duplicate rows",f"{int(data.duplicated().sum()):,}")
    schema=pd.DataFrame({"column":data.columns,"dtype":[str(data[c].dtype) for c in data.columns],"non_null":[int(data[c].notna().sum()) for c in data.columns],"missing_%":[round(float(data[c].isna().mean()*100),2) for c in data.columns],"unique_values":[int(data[c].nunique(dropna=True)) for c in data.columns]})
    st.dataframe(schema,use_container_width=True,hide_index=True,height=420)
    st.download_button("⬇️ Download data quality report",schema.to_csv(index=False).encode(),"data_quality_report.csv","text/csv")
    missing=schema[schema["missing_%"]>0].sort_values("missing_%",ascending=False)
    if not missing.empty: st.markdown("#### Columns with missing values"); st.dataframe(missing,use_container_width=True,hide_index=True)
    st.markdown("#### CSV files beside app.py")
    csvs=sorted(p.name for p in ROOT.glob("*.csv"))
    st.write("\n".join(f"- `{n}`" for n in csvs) if csvs else "No CSV files found beside app.py.")

st.divider()
st.markdown('<p class="muted">Social Media Unlox Major Project · YouTube Data API v3 · Streamlit. Metrics reflect the files included with this deployment.</p>',unsafe_allow_html=True)
