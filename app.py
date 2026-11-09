"""Management Dashboard — a clean presentation layer over your cleaned Excel data.

Run with:  streamlit run app.py
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

import charts as C
import data as D
from styling import fmt_value, inject_css, kpi_card

st.set_page_config(page_title="Management Dashboard", page_icon="📊", layout="wide")
inject_css()

# --------------------------------------------------------------------------- #
# Load data
# --------------------------------------------------------------------------- #
df, schema, source_label, is_demo = D.load_data()
date_col = schema["date"]
measures = [m for m in schema["measures"] if m in df.columns]
dims = [d for d in schema["dimensions"] if d in df.columns]

if date_col is None or not measures:
    st.error(
        "Could not find a date column and numeric measures in the data. "
        "Check that your sheet has a date field and at least one numeric column."
    )
    st.stop()

min_d = df[date_col].min().normalize()
max_d = df[date_col].max().normalize()

# --------------------------------------------------------------------------- #
# Header
# --------------------------------------------------------------------------- #
st.markdown(
    f"""
    <div class="dash-header">
      <div>
        <p class="dash-title">Management Dashboard</p>
        <p class="dash-sub">Performance overview · {min_d:%d %b %Y} – {max_d:%d %b %Y}</p>
      </div>
      <div class="dash-stamp">
        Data as of {max_d:%d %b %Y}<br>{len(df):,} records · {source_label}
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
if is_demo:
    st.info(
        "Showing a **sample dataset** so you can preview the dashboard. "
        "Drop your cleaned `.xlsx` into the project folder and refresh to use your own data.",
        icon="ℹ️",
    )

# --------------------------------------------------------------------------- #
# Global filters
# --------------------------------------------------------------------------- #
PRESETS = ["Last 30 days", "Last 90 days", "Last 180 days", "Last 365 days", "Year to date", "All time", "Custom"]
KEYS = ["date_preset", "custom_range", "metric", "group_by"] + [f"dim_{i}" for i in range(len(dims))]

with st.container(border=True):
    r1 = st.columns([1.4, 1.3, 1.3, 0.7])
    preset = r1[0].selectbox("Date range", PRESETS, index=0, key="date_preset")
    if preset == "Custom":
        custom = r1[1].date_input(
            "Custom period", value=(min_d.date(), max_d.date()), key="custom_range"
        )
    else:
        custom = None
        r1[1].write("")

    if preset == "Custom":
        metric = r1[2].selectbox("Metric", measures, key="metric")
    else:
        metric = r1[2].selectbox("Metric", measures, key="metric")

    group_by = r1[3].selectbox("Group by", dims, key="group_by") if dims else None
    if r1[3].button("Reset", width="stretch"):
        for k in KEYS:
            st.session_state.pop(k, None)
        st.rerun()

    if dims:
        filter_cols = st.columns(min(len(dims), 4))
        for i, dim in enumerate(dims[:4]):
            options = sorted(df[dim].dropna().astype(str).unique().tolist())
            filter_cols[i].multiselect(dim, options, placeholder="All", key=f"dim_{i}")


def resolve_range(preset: str, min_d: pd.Timestamp, max_d: pd.Timestamp, custom):
    if preset == "Custom":
        if isinstance(custom, (tuple, list)) and len(custom) == 2:
            return pd.Timestamp(custom[0]), pd.Timestamp(custom[1])
        return min_d, max_d
    if preset == "All time":
        return min_d, max_d
    if preset == "Year to date":
        return pd.Timestamp(max_d.year, 1, 1), max_d
    days = {"Last 30 days": 30, "Last 90 days": 90, "Last 180 days": 180, "Last 365 days": 365}[preset]
    return max_d - pd.Timedelta(days=days), max_d


start, end = resolve_range(preset, min_d, max_d, custom)

mask = (df[date_col] >= start) & (df[date_col] <= end)
for i, dim in enumerate(dims[:4]):
    chosen = st.session_state.get(f"dim_{i}") or []
    if chosen:
        mask &= df[dim].astype(str).isin(chosen)

fdf = df[mask]

if fdf.empty:
    st.warning("No records match these filters. Widen the date range or clear a filter.")
    st.stop()

# Prior period of equal length, immediately before the current window.
span = end - start
prev_end = start - pd.Timedelta(days=1)
prev_start = prev_end - span
pmask = (df[date_col] >= prev_start) & (df[date_col] <= prev_end)
for i, dim in enumerate(dims[:4]):
    chosen = st.session_state.get(f"dim_{i}") or []
    if chosen:
        pmask &= df[dim].astype(str).isin(chosen)
pdf = df[pmask]

# --------------------------------------------------------------------------- #
# KPI strip
# --------------------------------------------------------------------------- #
kpi_measures = [metric] + [m for m in measures if m != metric]
kpi_measures = kpi_measures[:5]

cols = st.columns(len(kpi_measures), gap="medium")
for col, m in zip(cols, kpi_measures):
    cur = float(fdf[m].sum())
    prev = float(pdf[m].sum()) if len(pdf) else 0.0
    delta = ((cur - prev) / prev * 100) if prev not in (0, None) else None
    with col:
        st.markdown(kpi_card(m, fmt_value(cur, m), delta), unsafe_allow_html=True)

st.write("")

# --------------------------------------------------------------------------- #
# Charts
# --------------------------------------------------------------------------- #
freq = C.pick_freq(start, end)
cur_total = float(fdf[metric].sum())
prev_total = float(pdf[metric].sum()) if len(pdf) else 0.0
change = ((cur_total - prev_total) / prev_total * 100) if prev_total else None

row1 = st.columns([1.6, 1], gap="medium")
with row1[0]:
    st.markdown('<p class="section-title">Trend</p>', unsafe_allow_html=True)
    trend_note = (
        f"{metric} is {'up' if (change or 0) >= 0 else 'down'} "
        f"{abs(change):.1f}% versus the prior period."
        if change is not None
        else f"{metric} over the selected period."
    )
    st.markdown(f'<p class="insight">{trend_note}</p>', unsafe_allow_html=True)
    st.plotly_chart(
        C.trend_fig(fdf, pdf, date_col, metric, freq),
        width="stretch", config={"displayModeBar": False},
    )

with row1[1]:
    split_dim = group_by or dims[0]
    st.markdown(f'<p class="section-title">Share by {split_dim}</p>', unsafe_allow_html=True)
    g = fdf.groupby(split_dim)[metric].sum().sort_values(ascending=False)
    top_share = (g.iloc[0] / g.sum() * 100) if g.sum() else 0
    st.markdown(
        f'<p class="insight">{g.index[0]} leads with {top_share:.0f}% of {metric.lower()}.</p>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(
        C.donut_fig(fdf, split_dim, metric),
        width="stretch", config={"displayModeBar": False},
    )

row2 = st.columns(2, gap="medium")
with row2[0]:
    rank_dim = next((d for d in dims if d != split_dim), split_dim)
    st.markdown(f'<p class="section-title">Top {rank_dim}</p>', unsafe_allow_html=True)
    gr = fdf.groupby(rank_dim)[metric].sum().sort_values(ascending=False)
    st.markdown(
        f'<p class="insight">Highest: <b>{gr.index[0]}</b> · {fmt_value(gr.iloc[0], metric)}.</p>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(
        C.bar_fig(fdf, rank_dim, metric),
        width="stretch", config={"displayModeBar": False},
    )

with row2[1]:
    st.markdown(f'<p class="section-title">{metric} by {split_dim} over time</p>', unsafe_allow_html=True)
    st.markdown('<p class="insight">Darker cells indicate higher values.</p>', unsafe_allow_html=True)
    st.plotly_chart(
        C.heatmap_fig(fdf, split_dim, metric, date_col, freq),
        width="stretch", config={"displayModeBar": False},
    )

# --------------------------------------------------------------------------- #
# Detail table + export
# --------------------------------------------------------------------------- #
st.markdown('<p class="section-title">Detail records</p>', unsafe_allow_html=True)
st.markdown(
    f'<p class="insight">Showing {len(fdf):,} of {len(df):,} records for the current filters.</p>',
    unsafe_allow_html=True,
)

display = fdf.sort_values(date_col, ascending=False)
st.dataframe(
    display,
    width="stretch",
    hide_index=True,
    height=420,
    column_config={
        date_col: st.column_config.DateColumn(date_col, format="YYYY-MM-DD"),
    },
)

st.download_button(
    "Download filtered data (CSV)",
    data=display.to_csv(index=False).encode("utf-8-sig"),
    file_name="dashboard_export.csv",
    mime="text/csv",
)

st.markdown(
    f'<p class="insight" style="margin-top:18px">Source: {source_label} · '
    f'Generated {datetime.now():%d %b %Y %H:%M} · '
    f'{start:%d %b %Y} – {end:%d %b %Y}</p>',
    unsafe_allow_html=True,
)
