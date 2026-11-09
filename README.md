# Retail Sales Analytics Dashboard

**Interactive business intelligence dashboard built with Python, Streamlit, Pandas, and Plotly.**

Explore retail performance through configurable KPIs, time trends, category breakdowns, interactive filters, and downloadable transaction-level results. The app analyzes a cleaned Excel or CSV dataset directly; it does **not** depend on Excel PivotTables or charts.

**Repository:** [Retail-Sales-Analytics-Dashboard](https://github.com/nvtharindukothalawala-tech/Retail-Sales-Analytics-Dashboard)

## Dashboard screenshots

Add screenshots of the running application to a `screenshots/` folder in the repository. Suggested image names:

| Dashboard view | Screenshot file to add |
| --- | --- |
| Overview, KPIs, and filters | `screenshots/dashboard-overview.png` |
| Trend and category breakdown | `screenshots/sales-charts.png` |
| Detailed records and CSV export | `screenshots/detail-and-export.png` |

<!-- Uncomment these image lines AFTER adding the actual screenshot files:
![Retail analytics overview](screenshots/dashboard-overview.png)
![Sales trends and breakdowns](screenshots/sales-charts.png)
![Detailed records and export](screenshots/detail-and-export.png)
-->

## Key features

- **Interactive KPI cards:** Display selected numerical measures and compare performance with the previous equivalent period, when prior-period data exists.
- **Global filtering:** Choose a date range, reporting metric, grouping dimension, and up to four categorical filters.
- **Date controls:** Last 30/90/180/365 days, year to date, all time, and a custom date range.
- **Visual analytics:** Plotly time-series trend, doughnut chart, ranked bar chart, and time-by-category heatmap.
- **Data exploration:** Review filtered transaction records in a searchable, interactive Streamlit data table.
- **CSV export:** Download the current filtered dataset as a UTF-8 CSV file.
- **Flexible input:** Read Excel (`.xlsx`, `.xlsm`) or CSV files, with sheet and column-role configuration.
- **Demo mode:** Uses generated sample data when no source dataset is found.

## Technology stack

| Technology | Purpose |
| --- | --- |
| **Python** | Dashboard logic and data processing |
| **Streamlit** | Interactive web application |
| **Pandas** | Cleaning, filtering, grouping, and calculations |
| **NumPy** | Numerical operations and sample-data generation |
| **Plotly** | Interactive charts |
| **OpenPyXL** | Excel workbook reading support |
| **HTML/CSS** | Customized dashboard appearance |

Dependency versions are maintained in [`requirements.txt`](requirements.txt).

## Getting started

### Prerequisites

- Python installed on your computer, available through the `python` command
- Git (for cloning the repository)
- Internet access for the first dependency installation

### Option A — Quick start on Windows

1. Download or clone this repository.
2. Open the project folder.
3. Double-click **`run.bat`**.

On its first run, the script creates a `.venv` environment and installs the dependencies. It then starts the Streamlit app. If you already created `.venv` but dependencies are missing, follow Option B to install them.

### Option B — Run manually (Windows PowerShell)

```powershell
git clone https://github.com/nvtharindukothalawala-tech/Retail-Sales-Analytics-Dashboard.git
cd Retail-Sales-Analytics-Dashboard
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m streamlit run app.py
```

Open **http://localhost:8501** in a browser if it does not open automatically.

### macOS or Linux

```bash
git clone https://github.com/nvtharindukothalawala-tech/Retail-Sales-Analytics-Dashboard.git
cd Retail-Sales-Analytics-Dashboard
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

To stop the app, press **Ctrl + C** in its terminal.

## Using your own retail data

1. Place a **non-confidential** cleaned `.xlsx`, `.xlsm`, or `.csv` file in the repository folder or the `data/` subfolder.
2. Use one row per sales record, with a usable date field and numeric business measures.
3. Start or refresh the Streamlit application.
4. Select **All time** in the Date range filter to see the full dataset (the app otherwise starts with Last 30 days).
5. Change metrics, filters, and chart grouping to explore the data.

The repository includes [`dashboard_config.json`](dashboard_config.json), which identifies the workbook sheet and preferred analytical fields:

- Sheet: `Cleaned Sales Data`
- Date field: `Date`
- Measures: `Net Sales`, `Gross Sales`, `Gross Profit`, `Quantity`, `Cost of Sales`
- Dimensions: `Category`, `Outlet`, `Sales Channel`, `Brand`, `Discount Band`, `Margin Classification`

For a different dataset, update those settings to match the new column names. If some configured fields are unavailable, the data loader also supports automatic schema detection. The program can derive Gross Profit when suitable revenue and cost columns exist and a Gross Profit field is absent.

> **Data privacy:** Do not publish actual customer details, personal identifiers, or confidential business records. Use synthetic, anonymized, or explicitly approved example datasets when sharing the repository or deploying the application publicly. Review any data already committed to Git history.

## Project structure

```text
Retail-Sales-Analytics-Dashboard/
├── .streamlit/
│   └── config.toml        # Streamlit theme settings
├── data/                  # Input workbook(s) — check sharing permissions
├── app.py                 # Main page, KPIs, filters, visuals, details, export
├── charts.py              # Plotly chart builders
├── data.py                # File loading, schema detection, demo data
├── styling.py             # Custom CSS, KPI cards, formatting
├── dashboard_config.json # Preferred sheet and field mapping
├── requirements.txt       # Python packages
├── run.bat                # Windows launcher
├── .gitignore             # Local files excluded from version control
└── README.md              # Project documentation
```

## How the analysis works

1. **Load** a workbook/CSV or create a demo dataset if none is available.
2. **Detect** or configure the date field, numerical measures, and grouping dimensions.
3. **Filter** the data by selected dates and categories.
4. **Calculate** KPI totals and previous-period comparisons from the filtered records.
5. **Visualize** the same filtered records in interactive Plotly charts.
6. **Export** the filtered data for further analysis.

The results depend on the columns and reporting period in the selected dataset. Profit and margin interpretations should be checked against the input data's accounting definitions.

## Customization

- **Dataset field mapping:** Edit `dashboard_config.json`.
- **Theme:** Edit `.streamlit/config.toml`.
- **KPI cards and number formatting:** Edit `styling.py`.
- **Chart behavior and styling:** Edit `charts.py`.
- **Layout and filter controls:** Edit `app.py`.

## Author

**Tharindu Kothalawala**  
GitHub: [@nvtharindukothalawala-tech](https://github.com/nvtharindukothalawala-tech)

## Project status

The repository contains a runnable local Streamlit application. A public hosted deployment link has not been included; the application can be started using the instructions above.
