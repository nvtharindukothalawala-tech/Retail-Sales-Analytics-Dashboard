"""Plotly chart builders. All figures share one visual language."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from styling import ACCENT, BORDER, MUTED, PALETTE, TEXT, fmt_axis, fmt_value

FONT = dict(family="Inter, Segoe UI, sans-serif", color=TEXT, size=12)


def _base_layout(height: int = 330) -> dict:
    return dict(
        height=height,
        margin=dict(l=8, r=8, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=FONT,
        hoverlabel=dict(bgcolor="white", bordercolor=BORDER, font=FONT),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=11)),
    )


def _axis(show_grid: bool = True) -> dict:
    return dict(
        showgrid=show_grid,
        gridcolor=BORDER,
        zeroline=False,
        linecolor=BORDER,
        tickfont=dict(size=11, color=MUTED),
    )


def period_series(df: pd.DataFrame, date_col: str, measure: str, freq: str) -> pd.Series:
    d = df[[date_col, measure]].dropna(subset=[date_col]).copy()
    d["_p"] = d[date_col].dt.to_period(freq)
    return d.groupby("_p")[measure].sum().sort_index()


def pick_freq(start: pd.Timestamp, end: pd.Timestamp) -> str:
    days = (end - start).days
    if days > 420:
        return "M"
    if days > 90:
        return "W"
    return "D"


def trend_fig(cur: pd.DataFrame, prev: pd.DataFrame, date_col: str, measure: str, freq: str) -> go.Figure:
    cur_s = period_series(cur, date_col, measure, freq)
    prev_s = period_series(prev, date_col, measure, freq) if len(prev) else pd.Series(dtype=float)
    x = [str(p) for p in cur_s.index]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x, y=cur_s.values, mode="lines+markers", name="Current period",
            line=dict(color=ACCENT, width=3), marker=dict(size=5),
            fill="tozeroy", fillcolor="rgba(31,78,121,0.07)",
            hovertemplate="%{x}<br><b>%{y:,.0f}</b><extra></extra>",
        )
    )
    if len(prev_s):
        y = list(prev_s.values)
        if len(y) > len(x):
            y = y[-len(x):]
        else:
            y = [None] * (len(x) - len(y)) + y
        fig.add_trace(
            go.Scatter(
                x=x, y=y, mode="lines", name="Prior period",
                line=dict(color="#B0B7C3", width=2, dash="dash"),
                hovertemplate="%{x}<br>prior: <b>%{y:,.0f}</b><extra></extra>",
            )
        )

    fig.update_layout(**_base_layout(340))
    fig.update_xaxes(**_axis(False))
    fig.update_yaxes(**_axis(True), tickformat=",.")
    return fig


def donut_fig(df: pd.DataFrame, dim: str, measure: str) -> go.Figure:
    g = df.groupby(dim)[measure].sum().sort_values(ascending=False)
    if len(g) > 8:
        head = g.head(8)
        other = pd.Series({"Other": g.iloc[8:].sum()})
        g = pd.concat([head, other])

    total = float(g.sum())
    fig = go.Figure(
        go.Pie(
            labels=[str(i) for i in g.index],
            values=g.values,
            hole=0.62,
            sort=False,
            marker=dict(colors=[PALETTE[i % len(PALETTE)] for i in range(len(g))],
                        line=dict(color="white", width=2)),
            textinfo="percent",
            textfont=dict(size=11, color="white"),
            hovertemplate="%{label}<br><b>%{value:,.0f}</b> (%{percent})<extra></extra>",
        )
    )
    fig.update_layout(**_base_layout(340), showlegend=True)
    fig.add_annotation(
        text=f"<b>{fmt_value(total, measure)}</b><br><span style='font-size:10px;color:{MUTED}'>total</span>",
        showarrow=False, font=dict(size=15, color=TEXT),
    )
    return fig


def bar_fig(df: pd.DataFrame, dim: str, measure: str, top_n: int = 10) -> go.Figure:
    g = df.groupby(dim)[measure].sum().sort_values(ascending=True).tail(top_n)
    labels = [str(i) for i in g.index]
    texts = [fmt_value(v, measure) for v in g.values]
    fig = go.Figure(
        go.Bar(
            x=g.values, y=labels, orientation="h",
            marker=dict(color=ACCENT, cornerradius=4),
            text=texts, textposition="outside",
            textfont=dict(size=11, color=MUTED),
            hovertemplate="%{y}<br><b>%{x:,.0f}</b><extra></extra>",
        )
    )
    fig.update_layout(**_base_layout(340), showlegend=False)
    fig.update_xaxes(**_axis(True), tickformat=",.", showticklabels=False)
    fig.update_yaxes(**_axis(False))
    fig.update_layout(margin=dict(l=8, r=48, t=8, b=8))
    return fig


def heatmap_fig(df: pd.DataFrame, dim: str, measure: str, date_col: str, freq: str) -> go.Figure:
    d = df[[date_col, dim, measure]].dropna(subset=[date_col]).copy()
    d["_p"] = d[date_col].dt.to_period(freq).astype(str)
    top = d.groupby(dim)[measure].sum().sort_values(ascending=False).head(6).index
    pivot = (
        d[d[dim].isin(top)]
        .pivot_table(index=dim, columns="_p", values=measure, aggfunc="sum")
        .reindex(top)
    )
    fig = go.Figure(
        go.Heatmap(
            z=pivot.values,
            x=[str(c) for c in pivot.columns],
            y=[str(i) for i in pivot.index],
            colorscale=[[0, "#EEF3F9"], [0.5, "#5B9BD5"], [1, ACCENT]],
            showscale=False,
            hovertemplate="%{y} · %{x}<br><b>%{z:,.0f}</b><extra></extra>",
        )
    )
    fig.update_layout(**_base_layout(340), showlegend=False)
    fig.update_xaxes(**_axis(False))
    fig.update_yaxes(**_axis(False))
    return fig
