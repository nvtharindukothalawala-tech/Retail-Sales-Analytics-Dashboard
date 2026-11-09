"""Data loading, schema detection and sample data for the management dashboard.

The app works with whatever cleaned table you drop in the project folder
(``*.xlsx`` / ``*.xlsm`` / ``*.csv``). Column roles (date, measures,
dimensions) are detected automatically, so the dashboard adapts to your
dataset instead of hard-coding column names.
"""

from __future__ import annotations

import glob
import json
import os

import numpy as np
import pandas as pd
import streamlit as st

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(APP_DIR, "data")

DATE_HINTS = ("date", "day", "month", "period", "time", "created", "ordered")
REVENUE_HINTS = ("revenue", "sales", "amount", "turnover", "income")
COST_HINTS = ("cost", "expense", "cogs", "spend")

CONFIG_PATH = os.path.join(APP_DIR, "dashboard_config.json")


def load_config() -> dict:
    """Optional per-workbook overrides (sheet, date, measures, dimensions)."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, ValueError):
            return {}
    return {}


# --------------------------------------------------------------------------- #
# Source discovery
# --------------------------------------------------------------------------- #
def find_source_file() -> str | None:
    """Return the first usable data file in /data or the project root."""
    for folder in (DATA_DIR, APP_DIR):
        for pattern in ("*.xlsx", "*.xlsm", "*.csv"):
            for path in sorted(glob.glob(os.path.join(folder, pattern))):
                if not os.path.basename(path).startswith("~$"):
                    return path
    return None


def _clean_sheet(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.dropna(how="all").dropna(axis=1, how="all")


def _score_sheet(name: str, frame: pd.DataFrame) -> int:
    """Rank a sheet by how much it looks like clean, detail-level data."""
    if frame.empty or frame.shape[1] < 2:
        return -1
    schema = detect_schema(frame)
    if schema["date"] is None or len(schema["measures"]) < 2:
        return -1
    low = name.lower()
    score = min(frame.shape[1], 30)
    if "clean" in low:
        score += 40
    if any(k in low for k in ("detail", "source")):
        score += 15
    if any(k in low for k in ("sales", "data")):
        score += 10
    if "raw" in low:
        score -= 2
    return score


def _read_file(path: str, sheet: str | None = None) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(path)

    # Explicit sheet from the config wins.
    if sheet:
        try:
            return _clean_sheet(pd.read_excel(path, sheet_name=sheet))
        except ValueError:
            pass

    book = pd.read_excel(path, sheet_name=None)
    best_df: pd.DataFrame | None = None
    best_score = -1
    for name, frame in book.items():
        frame = _clean_sheet(frame)
        score = _score_sheet(name, frame)
        if score > best_score:
            best_df, best_score = frame, score

    if best_df is not None and best_score >= 0:
        return best_df

    # Fallback: first non-empty sheet.
    for frame in book.values():
        frame = _clean_sheet(frame)
        if not frame.empty:
            return frame
    return pd.DataFrame()


# --------------------------------------------------------------------------- #
# Sample data (used until a real workbook is added)
# --------------------------------------------------------------------------- #
def _make_demo() -> pd.DataFrame:
    rng = np.random.default_rng(7)
    end = pd.Timestamp.today().normalize()
    start = end - pd.Timedelta(days=540)

    regions = ["North", "South", "East", "West"]
    categories = ["Electronics", "Apparel", "Home", "Sports", "Beauty"]
    channels = ["Online", "Retail", "Partner"]
    price = {"Electronics": 240, "Apparel": 65, "Home": 120, "Sports": 90, "Beauty": 45}

    dates = pd.date_range(start, end, freq="D")
    weights = np.linspace(0.85, 1.25, len(dates))  # gentle upward trend
    rows = []
    for _ in range(1600):
        day = rng.choice(dates, p=weights / weights.sum())
        cat = rng.choice(categories)
        units = int(rng.integers(1, 22))
        revenue = units * price[cat] * float(rng.uniform(0.9, 1.15))
        cost = revenue * float(rng.uniform(0.52, 0.79))
        rows.append(
            {
                "Order Date": pd.Timestamp(day),
                "Region": rng.choice(regions),
                "Category": cat,
                "Channel": rng.choice(channels),
                "Units": units,
                "Revenue": round(revenue, 2),
                "Cost": round(cost, 2),
            }
        )
    return pd.DataFrame(rows).sort_values("Order Date").reset_index(drop=True)


# --------------------------------------------------------------------------- #
# Schema detection
# --------------------------------------------------------------------------- #
def _looks_like_date(series: pd.Series, name: str) -> bool:
    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    low = str(name).lower()
    if not any(h in low for h in DATE_HINTS):
        return False
    parsed = pd.to_datetime(series, errors="coerce")
    return parsed.notna().mean() > 0.8


def detect_schema(df: pd.DataFrame) -> dict:
    """Split columns into a date column, numeric measures and dimensions."""
    date_col = None
    for col in df.columns:
        if _looks_like_date(df[col], col):
            date_col = col
            break

    measures: list[str] = []
    dimensions: list[str] = []
    n = max(len(df), 1)

    for col in df.columns:
        if col == date_col:
            continue
        series = df[col]
        if pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series):
            if not str(col).strip().endswith("%"):  # ratios are not additive
                measures.append(col)
            continue
        if pd.api.types.is_datetime64_any_dtype(series):
            continue
        nunique = series.nunique(dropna=True)
        if 2 <= nunique <= 60 and nunique / n < 0.6:
            dimensions.append(col)

    return {"date": date_col, "measures": measures, "dimensions": dimensions}


def _apply_config(df: pd.DataFrame, schema: dict, cfg: dict) -> dict:
    """Use explicit column roles from dashboard_config.json when provided."""
    if not cfg:
        return schema
    cols = set(df.columns)
    if cfg.get("date") in cols:
        schema["date"] = cfg["date"]
    if cfg.get("measures"):
        found = [m for m in cfg["measures"] if m in cols]
        if found:
            schema["measures"] = found
    if cfg.get("dimensions"):
        found = [d for d in cfg["dimensions"] if d in cols]
        if found:
            schema["dimensions"] = found
    return schema


def _add_derived(df: pd.DataFrame, schema: dict) -> dict:
    """Add Gross Profit when both a revenue-like and cost-like column exist."""
    measures = schema["measures"]
    rev = next((m for m in measures if any(h in str(m).lower() for h in REVENUE_HINTS)), None)
    cost = next((m for m in measures if any(h in str(m).lower() for h in COST_HINTS)), None)
    if rev and cost and rev != cost and "Gross Profit" not in df.columns:
        df["Gross Profit"] = df[rev] - df[cost]
        if "Gross Profit" not in schema["measures"]:
            schema["measures"].append("Gross Profit")
    return schema


# --------------------------------------------------------------------------- #
# Public loader
# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner=False)
def load_data(path: str | None = None):
    """Return (dataframe, schema, source_label, is_demo)."""
    cfg = load_config()
    source = path or find_source_file()
    if source:
        df = _read_file(source, sheet=cfg.get("sheet"))
        label = os.path.basename(source)
        is_demo = False
    else:
        df = _make_demo()
        cfg = {}
        label = "Sample dataset"
        is_demo = True

    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(how="all").dropna(axis=1, how="all").reset_index(drop=True)

    schema = detect_schema(df)
    schema = _apply_config(df, schema, cfg)
    schema = _add_derived(df, schema)

    if schema["date"] is not None:
        df[schema["date"]] = pd.to_datetime(df[schema["date"]], errors="coerce")
        df = df.dropna(subset=[schema["date"]]).reset_index(drop=True)

    return df, schema, label, is_demo
