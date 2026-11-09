"""Visual design system: theme, KPI cards and number formatting."""

from __future__ import annotations

import streamlit as st

ACCENT = "#1F4E79"
ACCENT_2 = "#2E75B6"
TEXT = "#111827"
MUTED = "#6B7280"
BORDER = "#E5E7EB"
POSITIVE = "#15803D"
NEGATIVE = "#B91C1C"
SURFACE = "#FFFFFF"
CANVAS = "#F3F6FA"

PALETTE = [
    "#1F4E79", "#2E75B6", "#5B9BD5", "#9DC3E6",
    "#C55A11", "#ED7D31", "#F4B183",
    "#548235", "#A9D18E", "#7F7F7F",
]

_CSS = f"""
<style>
  .block-container {{ padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1500px; }}
  #MainMenu, footer {{ visibility: hidden; }}

  .dash-header {{
      display: flex; justify-content: space-between; align-items: flex-end;
      border-bottom: 1px solid {BORDER}; padding-bottom: 14px; margin-bottom: 8px;
  }}
  .dash-title {{ font-size: 26px; font-weight: 700; color: {TEXT}; margin: 0; letter-spacing: -0.4px; }}
  .dash-sub {{ font-size: 13px; color: {MUTED}; margin: 4px 0 0 0; }}
  .dash-stamp {{ font-size: 12px; color: {MUTED}; text-align: right; }}

  .kpi {{
      background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 10px;
      padding: 16px 18px; height: 100%; box-shadow: 0 1px 2px rgba(16,24,40,.04);
  }}
  .kpi-label {{ font-size: 11px; font-weight: 600; letter-spacing: .06em;
                text-transform: uppercase; color: {MUTED}; margin-bottom: 6px; }}
  .kpi-value {{ font-size: 27px; font-weight: 700; color: {TEXT}; line-height: 1.1; }}
  .kpi-delta {{ font-size: 12px; font-weight: 600; margin-top: 8px; }}
  .kpi-delta span {{ color: {MUTED}; font-weight: 500; }}

  .section-title {{ font-size: 15px; font-weight: 700; color: {TEXT}; margin: 4px 0 2px 0; }}
  .insight {{ font-size: 12px; color: {MUTED}; margin: 2px 0 10px 0; }}

  div[data-testid="stMetric"] {{ display: none; }}
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def kpi_card(label: str, value: str, delta: float | None) -> str:
    if delta is None:
        delta_html = f'<div class="kpi-delta"><span>no prior period</span></div>'
    else:
        up = delta >= 0
        color = POSITIVE if up else NEGATIVE
        arrow = "▲" if up else "▼"
        delta_html = (
            f'<div class="kpi-delta" style="color:{color}">{arrow} {abs(delta):.1f}%'
            f' <span>vs prior period</span></div>'
        )
    return (
        f'<div class="kpi"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>{delta_html}</div>'
    )


# --------------------------------------------------------------------------- #
# Number formatting
# --------------------------------------------------------------------------- #
def _is_currency(measure: str) -> bool:
    low = str(measure).lower()
    return any(k in low for k in ("revenue", "sales", "amount", "cost", "profit", "price", "income", "turnover"))


def _is_count(measure: str) -> bool:
    low = str(measure).lower()
    return any(k in low for k in ("unit", "qty", "quantity", "order", "count", "customer", "items"))


def fmt_value(value: float, measure: str) -> str:
    if value is None or (isinstance(value, float) and value != value):
        return "—"
    if _is_currency(measure):
        return "$" + _abbrev(value)
    if _is_count(measure):
        return f"{value:,.0f}"
    return _abbrev(value)


def _abbrev(value: float) -> str:
    sign = "-" if value < 0 else ""
    v = abs(value)
    if v >= 1_000_000_000:
        return f"{sign}{v / 1_000_000_000:,.2f}B"
    if v >= 1_000_000:
        return f"{sign}{v / 1_000_000:,.2f}M"
    if v >= 10_000:
        return f"{sign}{v / 1_000:,.1f}K"
    return f"{value:,.0f}"


def fmt_axis(value: float) -> str:
    v = abs(value)
    sign = "-" if value < 0 else ""
    if v >= 1_000_000_000:
        return f"{sign}{v / 1_000_000_000:.1f}B"
    if v >= 1_000_000:
        return f"{sign}{v / 1_000_000:.1f}M"
    if v >= 1_000:
        return f"{sign}{v / 1_000:.0f}K"
    return f"{value:,.0f}"
