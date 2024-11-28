import streamlit as st
import pandas as pd
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

################## Notes #####################

# Colors = #47fff4, #9d9fff, #6d72f6, #f3d94e
##############################################

with tab1:
    col = st.columns((1.7, 4.5, 1.8), gap='medium')

    with col[0]:
        # Inputs
        fleet_type = st.radio("Type of fleet", ["Captive Fleet", "Contracted Fleet", "DCO FLeet"])
        if fleet_type == "Captive Fleet": 
            st.markdown("##### Inputs for owning fleet")
            vaqui_cost_ev2w = st.number_input("Vehicle Acquisition - 2W (Thousands)", min_value=0, value=80)
            vaqui_cost_ev3w = st.number_input("Vehicle Acquisition - 3W (Thousands)", min_value=0, value=335)
            annual_maintenance_cost = st.number_input("Annual Maintenance/Van (Thousands)", min_value=0, value=14)
            battery_replacement_cost_2w = st.number_input("Annual Battery Replacement - 2W (Thousands)", min_value=0, value=2)
            battery_replacement_cost_3w = st.number_input("Annual Battery Replacement - 3W (Thousands)", min_value=0, value=10)
        elif fleet_type == "Contracted Fleet":
            st.markdown("##### Contract Logistics")
            contract_period = st.number_input("Contract Period (Months)", min_value=0, value=60) # Default 5 years
            contract_cost = st.number_input("Contract Cost (per month)", min_value=0, value=100) # TODO: change default value
        # if fleet_type == "DCO Fleet":
            # TODO: add any additional costs/variables necessary for DCO fleet here

        # Costs for all fleet types
        st.markdown("##### Delivery Logistics")
        num_vans_2w = st.number_input("Number of Vans - 2W", min_value=0, value=3)
        num_vans_3w = st.number_input("Number of Vans - 3W", min_value=0, value=3)
        daily_average_miles_2w = st.number_input("Average Daily Miles - 2W", min_value=0, value=65)
        daily_average_miles_3w = st.number_input("Average Daily Miles - 3W", min_value=0, value=90)
        electricity_cost_per_km = st.number_input("Electricity Cost per km", min_value=0.0, value=2.58)

        # Hour wages
        st.markdown("##### Worker Logistics")
        delivery_rev = st.number_input("Revenue per Delivery", min_value=0, value=50)
        driver_wage_2w = st.number_input("Hourly Driver Wage - 2W", min_value=0, value=87)
        driver_wage_3w = st.number_input("Hourly Driver Wage - 3W", min_value=0, value=107)
        hourly_delivery_2w = st.number_input("Deliveries per Hour - 2W", min_value=0, value=3)
        hourly_delivery_3w = st.number_input("Deliveries per Hour - 3W", min_value=0, value=5)
        work_hours = st.number_input("Work hours per day", min_value=0, value=8)
        work_days = st.number_input("Work days per year", min_value=0, value=300)

        # Downtime costs/percentages
        st.markdown("##### Downtime Percentages")
        battery_issues = st.number_input("Percentage of battery problems", min_value=0, max_value=100, value=5)
        software_issues = st.number_input("Percentage of software problems", min_value=0, max_value=100, value=6)

    with col[2]:
        if fleet_type == "Captive Fleet":
            # st.metric(label="Revenue", value=Revenue, delta="_", delta_color="normal")
            # Cost of new vehicles
            iniital_vehicle_cost = (vaqui_cost_ev2w * num_vans_2w + vaqui_cost_ev3w * num_vans_3w) * 1000

            # Calculate total revenue accounting for missed_deliveries
            missed_deliveries_percentage = (battery_issues + software_issues) / 100 # Lost Revenue
            daily_deliveries_2w = hourly_delivery_2w * work_hours * num_vans_2w
            daily_deliveries_3w = hourly_delivery_3w * work_hours * num_vans_3w # Daily Revenue
            annual_revenue = (
                (daily_deliveries_2w + daily_deliveries_3w) * (1 - missed_deliveries_percentage) * work_days * delivery_rev
            )

            # Calculate costs
            annual_costs = (
                (daily_average_miles_2w * num_vans_2w + daily_average_miles_3w * num_vans_3w)
                * electricity_cost_per_km
                * work_days # Annual Electricity Cost
                + annual_maintenance_cost * (num_vans_2w + num_vans_3w) * 1000 # Annual Maintenance Cost
                + battery_replacement_cost_2w * num_vans_2w * 1000
                + battery_replacement_cost_3w * num_vans_3w * 1000 # Annual Battery Cost
                + driver_wage_2w * work_hours * work_days * num_vans_2w
                + driver_wage_3w * work_hours * work_days * num_vans_3w # Annual Driver Cost
                + (battery_issues + software_issues) / 100 * annual_revenue # Software + Battery Maintenance Costs
            )

            # Generate 5-year data
            years = list(range(6))
            revenues = [0]
            costs = [iniital_vehicle_cost]
            profits = [-iniital_vehicle_cost]
            payback_period = None

            # Calculate costs, revenue, and profits for each year
            for year in range(1, 6):
                previous_profit = profits[-1]
                yearly_profit = previous_profit + annual_revenue - annual_costs

                revenues.append(annual_revenue)
                costs.append(annual_costs)
                profits.append(yearly_profit)
                if previous_profit < 0 < yearly_profit:
                    payback_period = year - 1 - previous_profit / (yearly_profit - previous_profit)

            # Create DataFrame
            profits_data = pd.DataFrame({
                "Revenue (Thousands)": revenues,
                "Cost (Thousands)": costs,
                "Cumulative Profit (Thousands)": profits,
            })

            final_profit = profits[-1]  # Last year's cumulative profit
            roi = (final_profit / iniital_vehicle_cost) * 100 if iniital_vehicle_cost > 0 else 0

            # Display ROI
            # st.markdown("### ROI Calculation")
            roi_inc = roi - 100
            st.metric(label="Return on Investment (ROI)", value=f"{roi:.2f}%", delta=f"{roi_inc:.2f}%", delta_color="normal")
            st.metric(label="Payback Period (Years)", value=f"{payback_period:.2f}", delta="_", delta_color="normal")
        elif fleet_type == "DCO Fleet":
            # Calculate Costs

            # Calculate Revenue

            # Calculate Profits

            # Display Metrics
            st.write("hi1")
        elif fleet_type == "Contracted Fleet":
            # Calculate Costs

            # Calculate Revenue

            # Calculate Profits

            # Display Metrics
            st.write("hi2")


    with col[1]:
        st.title("Coulomb AI Metrics")
        
        # Testing something
        data = {
            "Category": ["A", "B", "C", "D", "E"],
            "Values": [10, 20, 15, 30, 25],
        }

        df = pd.DataFrame(data)
        # st.bar_chart(df, color=["#9d9fff", "#6d72f6"])

        st.markdown("### Cumulative Net Profits")
        st.line_chart(profits_data, color=["#9d9fff", "#f3d94e", "#6d72f6"])

        