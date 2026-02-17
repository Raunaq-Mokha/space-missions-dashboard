import streamlit as st
import pandas as pd
import altair as alt
from functions import _load_data

st.set_page_config(
    page_title="Space Missions Dashboard",
    page_icon="\U0001F680",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    return _load_data().copy()

df = load_data()

# --- RESET LOGIC ---
if "reset_counter" not in st.session_state:
    st.session_state.reset_counter = 0

rc = st.session_state.reset_counter

def reset_filters():
    st.session_state.reset_counter += 1

# --- HEADER ---
st.markdown(
    "<h1 style='margin-bottom: 0; text-align: center;'>Space Missions Dashboard</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: gray;'>Explore and analyze historical space mission data from 1957 onwards.</p>",
    unsafe_allow_html=True,
)
st.markdown("")

# --- TOP SECTION: Filters (left) + Main Chart (right) ---
filter_col, chart_col = st.columns([1, 2.5], gap="large")

with filter_col:
    # --- Filters Card ---
    with st.container(border=True):
        st.markdown("**Filters**")

        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()
        date_range = st.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key=f"date_range_{rc}",
        )

        companies = sorted(df['Company'].unique().tolist())
        selected_companies = st.multiselect(
            "Companies", options=companies, default=[], key=f"companies_{rc}"
        )

        statuses = sorted(df['MissionStatus'].dropna().unique().tolist())
        selected_statuses = st.multiselect(
            "Mission status", options=statuses, default=[], key=f"statuses_{rc}"
        )

        rocket_status = st.radio(
            "Rocket status",
            options=["All", "Active", "Retired"],
            horizontal=True,
            key=f"rocket_status_{rc}",
        )

        st.button("Reset Filters", on_click=reset_filters, width="stretch")

    # --- APPLY FILTERS ---
    filtered_df = df.copy()

    if isinstance(date_range, tuple) and len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['Date'].dt.date >= date_range[0])
            & (filtered_df['Date'].dt.date <= date_range[1])
        ]

    if selected_companies:
        filtered_df = filtered_df[filtered_df['Company'].isin(selected_companies)]

    if selected_statuses:
        filtered_df = filtered_df[filtered_df['MissionStatus'].isin(selected_statuses)]

    if rocket_status != "All":
        filtered_df = filtered_df[filtered_df['RocketStatus'] == rocket_status]

    # --- Summary Stats Card ---
    with st.container(border=True):
        if len(filtered_df) > 0:
            success_count = filtered_df[filtered_df['MissionStatus'] == 'Success'].shape[0]
            rate = round((success_count / len(filtered_df)) * 100, 2)
        else:
            rate = 0.0

        m1, m2 = st.columns(2)
        with m1:
            st.markdown("**Total Missions**")
            st.markdown(f"<h2 style='margin-top: -10px;'>{len(filtered_df):,}</h2>", unsafe_allow_html=True)
        with m2:
            st.markdown("**Success Rate**")
            st.markdown(f"<h2 style='margin-top: -10px;'>{rate}%</h2>", unsafe_allow_html=True)

        m3, m4 = st.columns(2)
        with m3:
            st.markdown("**Companies**")
            st.markdown(
                f"<h2 style='margin-top: -10px;'>{filtered_df['Company'].nunique()}</h2>",
                unsafe_allow_html=True,
            )
        with m4:
            st.markdown("**Active Rockets**")
            st.markdown(
                f"<h2 style='margin-top: -10px;'>"
                f"{filtered_df[filtered_df['RocketStatus'] == 'Active']['Rocket'].nunique()}</h2>",
                unsafe_allow_html=True,
            )

with chart_col:
    # --- CHART 1: Missions Over Time (Area Chart) ---
    with st.container(border=True):
        st.markdown("**Missions Over Time**")
        st.caption(
            "**Why this chart:** An area chart reveals the overall trend and volume of "
            "space launches across decades. The filled area emphasizes cumulative growth, "
            "making it easy to identify boom periods like the Space Race and the recent "
            "commercial space era."
        )

        yearly = (
            filtered_df.groupby(filtered_df['Date'].dt.year)
            .size()
            .reset_index(name='Missions')
        )
        yearly.columns = ['Year', 'Missions']

        base = alt.Chart(yearly).encode(
            x=alt.X('Year:Q', title='Year', axis=alt.Axis(format='d')),
            y=alt.Y('Missions:Q', title='Number of Missions',
                     axis=alt.Axis(format='d'),
                     scale=alt.Scale(domain=[0, max(yearly['Missions'].max(), 1)])),
            tooltip=[
                alt.Tooltip('Year:Q', format='d'),
                alt.Tooltip('Missions:Q'),
            ],
        )

        area_layer = base.mark_area(
            opacity=0.6,
            line=True,
            color=alt.Gradient(
                gradient='linear',
                stops=[
                    alt.GradientStop(color='#6C63FF', offset=0),
                    alt.GradientStop(color='#3B82F6', offset=1),
                ],
                x1=1, x2=1, y1=1, y2=0,
            ),
        )

        point_layer = base.mark_circle(size=60, color='#6C63FF')

        area_chart = (
            (area_layer + point_layer)
            .properties(height=420)
            .interactive()
        )

        st.altair_chart(area_chart, width="stretch")

# --- SECTION 2: Side-by-side charts ---
st.markdown("")
st.markdown("### Mission Breakdown")
st.caption("Detailed analysis of mission outcomes and top launch organizations.")

col_left, col_right = st.columns(2, gap="large")

with col_left:
    with st.container(border=True):
        st.markdown("**Mission Status Distribution**")
        st.caption(
            "**Why this chart:** A donut chart is ideal for part-to-whole relationships. "
            "It instantly communicates what proportion of missions succeeded vs. failed — "
            "the most fundamental metric in space launch analysis."
        )

        status_data = filtered_df['MissionStatus'].value_counts().reset_index()
        status_data.columns = ['Status', 'Count']

        donut = (
            alt.Chart(status_data)
            .mark_arc(innerRadius=70, outerRadius=130)
            .encode(
                theta=alt.Theta('Count:Q'),
                color=alt.Color(
                    'Status:N',
                    scale=alt.Scale(
                        domain=['Success', 'Failure', 'Partial Failure', 'Prelaunch Failure'],
                        range=['#2ecc71', '#e74c3c', '#f39c12', '#9b59b6'],
                    ),
                    legend=alt.Legend(title="Status"),
                ),
                tooltip=['Status:N', 'Count:Q'],
            )
            .properties(height=350)
        )

        st.altair_chart(donut, width="stretch")

with col_right:
    with st.container(border=True):
        st.markdown("**Top 10 Companies by Mission Count**")
        st.caption(
            "**Why this chart:** A horizontal bar chart ranks organizations clearly. "
            "The horizontal orientation keeps long company names fully readable "
            "without text rotation, making comparisons easy."
        )

        company_counts = filtered_df['Company'].value_counts().head(10).reset_index()
        company_counts.columns = ['Company', 'Missions']

        bar_chart = (
            alt.Chart(company_counts)
            .mark_bar(
                cornerRadiusTopRight=4,
                cornerRadiusBottomRight=4,
                color=alt.Gradient(
                    gradient='linear',
                    stops=[
                        alt.GradientStop(color='#6C63FF', offset=0),
                        alt.GradientStop(color='#3B82F6', offset=1),
                    ],
                    x1=0, x2=1, y1=0, y2=0,
                ),
            )
            .encode(
                x=alt.X('Missions:Q', title='Number of Missions'),
                y=alt.Y('Company:N', sort='-x', title=''),
                tooltip=['Company:N', 'Missions:Q'],
            )
            .properties(height=350)
        )

        st.altair_chart(bar_chart, width="stretch")

# --- SECTION 3: Success Rate Over Time ---
with st.container(border=True):
    st.markdown("**Success Rate Over Time**")
    st.caption(
        "**Why this chart:** A line chart tracks how mission reliability has evolved "
        "over decades. It reveals whether the space industry has become more reliable "
        "and highlights periods of regression — a story that static summary statistics "
        "cannot tell. Tooltips include total missions for context."
    )

    yearly_success = filtered_df.copy()
    yearly_success['Year'] = yearly_success['Date'].dt.year
    yearly_agg = (
        yearly_success.groupby('Year')
        .agg(
            SuccessRate=('MissionStatus', lambda g: round((g == 'Success').sum() / len(g) * 100, 2)),
            TotalMissions=('MissionStatus', 'size'),
        )
        .reset_index()
    )

    line = (
        alt.Chart(yearly_agg)
        .mark_line(point=alt.OverlayMarkDef(size=40), strokeWidth=2)
        .encode(
            x=alt.X('Year:Q', title='Year', axis=alt.Axis(format='d')),
            y=alt.Y('SuccessRate:Q', title='Success Rate (%)', scale=alt.Scale(domain=[0, 100])),
            color=alt.value('#2ecc71'),
            tooltip=[
                alt.Tooltip('Year:Q', format='d'),
                alt.Tooltip('SuccessRate:Q', title='Success Rate (%)'),
                alt.Tooltip('TotalMissions:Q', title='Total Missions'),
            ],
        )
        .properties(height=350)
        .interactive()
    )

    st.altair_chart(line, width="stretch")

# --- SECTION 4: Data Explorer ---
st.markdown("")
st.markdown("### Data Explorer")
st.caption(f"Showing {len(filtered_df):,} of {len(df):,} missions. Click column headers to sort.")

with st.container(border=True):
    display_df = filtered_df.copy()
    display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')

    st.dataframe(
        display_df,
        width="stretch",
        height=500,
        column_config={
            "Price": st.column_config.NumberColumn("Price (Millions $)", format="$%.1f"),
        },
    )
