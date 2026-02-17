# Space Missions Dashboard

An interactive dashboard for exploring and analyzing historical space mission data from 1957 onwards, built with Python and Streamlit.

## Tech Stack
- I used python for data processing and application logic
- I chose to use Streamlit for its native support for interactive data apps, built-in widgets so there is no need to write any front end code
- I used pandas  library for tabular data manipulation, filtering, and aggregation
- I used altair which is a declarative charting library that pairs well with DataFrames and renders interactive web-ready visualizations.

## Setup & Run

```bash
# Clone the repository
git clone https://github.com/Raunaq-Mokha/space-missions-dashboard.git
cd space-missions-dashboard

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## Features

- **Interactive filters** — filter by date range, company, mission status, and rocket status
- **Summary statistics** — total missions, success rate, number of companies, and active rockets (dynamically updated based on filters)
- **4 visualizations** — each chosen to answer a different question about the data
- **Data explorer** — sortable, searchable table of all mission records
- **8 programmatically testable functions** — located in `functions.py` with full input validation and edge case handling

## Visualization Choices

**1. Area Chart — Missions Over Time**
Shows the volume and trend of space launches across decades. The filled area makes growth and decline immediately visible, highlighting boom periods like the Space Race (1960s–70s) and the recent commercial space era (2020s). An area chart was chosen over a bar chart to avoid clutter across 60+ years of data.

**2. Donut Chart — Mission Status Distribution**
A part-to-whole chart that instantly communicates what proportion of missions succeeded vs. failed. With only 4 status categories, a donut chart stays clean and readable.

**3. Horizontal Bar Chart — Top 10 Companies by Mission Count**
Ranks the most active launch organizations. The horizontal orientation was chosen specifically because company names (e.g., "RVSN USSR", "Arianespace") are long — vertical bars would require rotated labels. Sorted descending so the top company appears first.

**4. Line Chart — Success Rate Over Time**
Tracks how mission reliability has evolved over decades. A single summary statistic like "89.89% success rate" hides the story — early missions had roughly 50% success rates, while modern launches exceed 95%. The line chart reveals this trend, with tooltips showing total missions per year for context.
