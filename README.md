# Management Dashboard

A clean, professional presentation layer for your cleaned Excel data. It reads your
workbook directly and builds the KPIs, trends and breakdowns itself — your pivot
tables and dashboard stay untouched.

## Quick start

1. Double-click **`run.bat`** (installs dependencies on first run), or:
   ```bat
   .venv\Scripts\python -m streamlit run app.py
   ```
2. The browser opens at `http://localhost:8501`.

## Use your own data

- Drop your cleaned **`.xlsx` / `.xlsm` / `.csv`** into this folder (or into a `data\` subfolder).
- The app picks the first sheet whose name looks like detail data
  (`data`, `raw`, `clean`, `sales`, `detail`, `source`), otherwise the first sheet.
- Keep it as a **flat, tidy table** (one row per record, a date column, numeric
  measure columns, and low-cardinality category columns). Pivot sheets are ignored
  on purpose — the app builds its own aggregations.
- Refresh the browser. Columns are detected automatically:
  - **Date** — a datetime column or a name containing `date/day/month/period/time`.
  - **Measures** — numeric columns (a `Gross Profit` column is derived when both
    revenue-like and cost-like columns exist).
  - **Dimensions** — text columns with 2–60 distinct values.

Until a file is present, a realistic **sample dataset** is shown.

## Project layout

| File | Purpose |
| --- | --- |
| `app.py` | Page: header, filters, KPIs, charts, table, export |
| `data.py` | File loading, schema detection, sample data |
| `charts.py` | Plotly builders (trend, donut, ranked bar, heatmap) |
| `styling.py` | Design system, KPI cards, number formatting |
| `.streamlit/config.toml` | Theme (colors, font, layout) |
| `requirements.txt` | Python dependencies |

## Notes

- Filters are global and drive every visual from one filtered dataframe.
- `Download filtered data (CSV)` exports exactly what is on screen (Excel-friendly UTF-8).
- To change the accent colour, edit `ACCENT` in `styling.py` and `primaryColor` in
  `.streamlit/config.toml`.
