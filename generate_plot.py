import streamlit as st
import pandas as pd
import altair as alt

def generate_plot(profits_data, payback_period):
    melted_data = profits_data.melt(id_vars=["Year"], var_name="Metric", value_name="Value")

    # Create base chart
    base = alt.Chart(melted_data).encode(
        x=alt.X(
            "Year:Q",
            scale=alt.Scale(domain=(0, profits_data["Year"].max())),
            axis=alt.Axis(title="Year", grid=True, tickCount=6),
        ),
        y=alt.Y(
            "Value:Q",
            axis=alt.Axis(title="Value (Thousands)", grid=True),
        ),
        color=alt.Color(
            "Metric:N",
            scale=alt.Scale(
                domain=["Revenue (Thousands)", "Cost (Thousands)", "Cumulative Profit (Thousands)"],
                range=["#9d9fff", "#f3d94e", "#6d72f6"]
            ),
            title="Metric",
        ),
        tooltip=["Year:Q", "Metric:N", "Value:Q"],
        strokeDash="Metric:N"
    ).properties(
        width=700,
        height=400,
        title="Revenue, Cost, and Cumulative Profit Over Time"
    )

    # Line chart
    lines = base.mark_line()
    final_chart = lines

    # Add a labeled point at the payback period
    if payback_period:
        payback_point = alt.Chart(pd.DataFrame({
            "Year": [payback_period],
            "Value": [0],
            "Label": ["Payback Period"]
        })).mark_point(filled=True, size=100, color="red").encode(
            x="Year:Q",
            y="Value:Q",
        ) + alt.Chart(pd.DataFrame({
            "Year": [payback_period],
            "Value": [0],
            "Label": ["Payback Period"]
        })).mark_text(
            align="left",
            dx=-60,
            dy=-15,
            fontSize=12,
            color="red"
        ).encode(
            x="Year:Q",
            y="Value:Q",
            text="Label"
        )
        # Combine charts
        final_chart = lines + payback_point

    # Display the chart in Streamlit
    st.altair_chart(final_chart, use_container_width=True)