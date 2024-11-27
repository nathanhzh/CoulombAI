import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt

# Page Setup
st.set_page_config(
    page_title="Coulomb AI",
    page_icon="🏂", # We should change this one
    layout="wide",
    initial_sidebar_state="expanded")
alt.themes.enable("dark")
# --------------

tab1, tab2, tab3 = st.tabs(["ROI Calculation", "Revenue", "Other"])

############## Notes ###############

# Colors = #47fff4, #9d9fff, #6d72f6
#####################################

with tab1:
    col = st.columns((1.7, 4.5, 1.8), gap='medium')

    with col[0]:
        # Inputs
        vaqui_cost_ev2w = st.number_input("Vehicle Acquisition - 2W (Thousands)", min_value=0, value=80)
        vaqui_cost_ev3w = st.number_input("Vehicle Acquisition - 3W (Thousands)", min_value=0, value=335)
        electricity_cost = st.number_input("Cost per km", min_value=0.0, value=2.58)
        maintenance_cost = st.number_input("Annual Maintenance/Van (Thousands)", min_value=0, value=14)
        battery_replacement_cost_2w = st.number_input("Annual Battery Replacement - 2W", min_value=0, value=2)
        battery_replacement_cost_3w = st.number_input("Annual Battery Replacement - 3W", min_value=0, value=10)
        average_miles_2w = st.number_input("Average Daily Miles - 2W", min_value=0, value=65)
        average_miles_3w = st.number_input("Average Daily Miles - 3W", min_value=0, value=90)
        driver_wage = st.number_input("Hourly Driver Wage", min_value=0, value=87)
        hourly_delivery_2w = st.number_input("Deliveries per Hour - 2W", min_value=0, value=3)
        hourly_delivery_3w = st.number_input("Deliveries per Hour - 3W", min_value=0, value=5)
        num_vans_2w = st.number_input("Number of Vans - 2W", min_value=0, value=3)
        num_vans_3w = st.number_input("Number of Vans - 3W", min_value=0, value=3)
        work_hours = st.number_input("Work hours per day", min_value=0, value=8)
        work_days = st.number_input("Work days per year", min_value=0, value=300)
        delivery_rev = st.number_input("Revenue per Delivery", min_value=0, value=220)
        battery_issues = st.number_input("Percentage of battery problems", min_value=0, max_value=100, value=5)
        software_issues = st.number_input("Percentage of software problems", min_value=0, max_value=100, value=6)

    with col[1]:
        st.title("Coulomb AI ROI")
        
        # Testing something
        data = {
            "Category": ["A", "B", "C", "D", "E"],
            "Values": [10, 20, 15, 30, 25],
        }

        df = pd.DataFrame(data)
        st.bar_chart(df, color=["#9d9fff", "#6d72f6"])

    with col[2]:
        missed_deliveries = (battery_issues + software_issues) / 100

        # Calculate total revenue
        daily_deliveries_2w = hourly_delivery_2w * work_hours * num_vans_2w
        daily_deliveries_3w = hourly_delivery_3w * work_hours * num_vans_3w
        annual_revenue = (
            (daily_deliveries_2w + daily_deliveries_3w) * (1 - missed_deliveries) * work_days * delivery_rev
        )

        # Calculate costs
        annual_costs = (
            (average_miles_2w * num_vans_2w + average_miles_3w * num_vans_3w)
            * electricity_cost
            * work_days
            + maintenance_cost * (num_vans_2w + num_vans_3w)
            + battery_replacement_cost_2w * num_vans_2w
            + battery_replacement_cost_3w * num_vans_3w
            + driver_wage * work_hours * work_days * (num_vans_2w + num_vans_3w)
            + (battery_issues + software_issues) / 100 * annual_revenue
        )

        vehicle_cost = (vaqui_cost_ev2w * num_vans_2w + vaqui_cost_ev3w * num_vans_3w)

        # Generate 5-year data
        years = list(range(1, 6))
        revenues = [annual_revenue] * 5
        costs = [annual_costs] * 5
        costs[1] += vehicle_cost
        profits = [r - c for r, c in zip(revenues, costs)]

        # Create DataFrame
        data = pd.DataFrame({
            "Year": years,
            "Revenue (Thousands)": revenues,
            "Cost (Thousands)": costs,
            "Profit (Thousands)": profits,
        })

        # Plot the graph
        plt.figure(figsize=(10, 6))
        plt.plot(data["Year"], data["Revenue (Thousands)"], label="Revenue", marker="o")
        plt.plot(data["Year"], data["Cost (Thousands)"], label="Cost", marker="o")
        plt.plot(data["Year"], data["Profit (Thousands)"], label="Profit", marker="o")
        plt.title("5-Year Revenue, Cost, and Profit Analysis")
        plt.xlabel("Year")
        plt.ylabel("Amount (Thousands)")
        plt.legend()
        plt.grid()
        plt.tight_layout()
    

        # Display the plot in Streamlit
        st.pyplot(plt)