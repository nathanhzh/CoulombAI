import streamlit as st
import pandas as pd
import altair as alt
from generate_plot import generate_plot

# Page Setup
st.set_page_config(
    page_title="Coulomb AI",
    page_icon="🏂", # We should change this one
    layout="wide",
    initial_sidebar_state="expanded")
alt.themes.enable("dark")
# --------------

tab1, tab2 = st.tabs(["Metrics", "Spreadsheet"])

################## Notes #####################

# Colors = #47fff4, #9d9fff, #6d72f6, #f3d94e
##############################################

coulomb_partner_cost = 250000 # TODO: Figure out how much initial cost to partner with coulomb is

# Function to calculate annual revenue
def get_annual_revenue(battery_issues, software_issues, hourly_delivery_2w, num_vans_2w, hourly_delivery_3w, num_vans_3w, work_hours,
                        delivery_rev, work_days):
    missed_deliveries_percentage = (battery_issues + software_issues) / 100 # Lost Revenue
    daily_deliveries_2w = hourly_delivery_2w * work_hours * num_vans_2w
    daily_deliveries_3w = hourly_delivery_3w * work_hours * num_vans_3w # Daily Revenue
    annual_revenue = (
        (daily_deliveries_2w + daily_deliveries_3w) * (1 - missed_deliveries_percentage) * work_days * delivery_rev
    )
    return annual_revenue

# Function to calculate annual cost
def get_annual_cost(daily_average_miles_2w, num_vans_2w, daily_average_miles_3w, num_vans_3w, electricity_cost_per_km,
                    work_hours, work_days, annual_maintenance_cost, battery_replacement_cost_2w, battery_replacement_cost_3w,
                    driver_wage_2w, driver_wage_3w, battery_issues, software_issues, annual_revenue):
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
    return annual_costs

with tab1:
    col = st.columns((1.7, 4.5, 1.8), gap='medium')

    with col[0]:
        # Inputs
        fleet_type = st.radio("Type of fleet", ["Captive Fleet", "Contracted Fleet", "DCO Fleet"])
        operational_years = st.number_input("Years of operation", min_value=4, value=5)
        if fleet_type == "Captive Fleet": 
            st.markdown("##### Inputs for owning fleet")
            vaqui_cost_ev2w = st.number_input("Vehicle Acquisition - 2W (Thousands)", min_value=0, value=80)
            vaqui_cost_ev3w = st.number_input("Vehicle Acquisition - 3W (Thousands)", min_value=0, value=335)
            gov_subsidy_ev2w = st.number_input("Government Subsidy - 2W (Thousands)", min_value=0, value=15)
            gov_subsidy_ev3w = st.number_input("Government Subsidy - 3W (Thousands)", min_value=0, value=10)
            state_incentive_ev2w = st.number_input("State-level Incentive - 2W (Thousands)", min_value=0, value=30)
            state_incentive_ev3w = st.number_input("State-level Incentive - 3W (Thousands)", min_value=0, value=30)

        elif fleet_type == "Contracted Fleet":
            st.markdown("##### Contract Logistics")
            contract_period = st.number_input("Contract Period (Months)", min_value=0, value= operational_years * 12)
            contract_cost_ev2w = st.number_input("Contract Cost - 2W (per month)(Thousands)", min_value=0, value= 1 ) 
            contract_cost_ev3w = st.number_input("Contract Cost - 3W (per month)(Thousands)", min_value=0, value= 4 )

        elif fleet_type == "DCO Fleet":
            st.markdown("##### DCO Logistics")
            management_fee_percentage = st.number_input("Management Ownership (%)", min_value=0, max_value=100, value=90)
            driver_share_percentage = 100 - management_fee_percentage # Driver's share of gross revenue
            platform_operational_cost = st.number_input("Annual Platform Operational Cost (Thousands)", min_value=0, value=100) # Annual operational cost for managing the platform, such as support systems, customer service, etc.
            training_cost_per_driver = st.number_input("Training Cost per Driver (Thousands)", min_value=0, value=5) # Cost for training each driver, covering onboarding and skill development
            vehicle_inspection_cost = st.number_input("Annual Vehicle Inspection Cost per Vehicle (Thousands)", min_value=0, value=2) # Annual cost for regular vehicle inspections to ensure safety and compliance

        # Additional Logistics for all types of fleets
        basic_insurance_2w = st.number_input("Basic Insurance (Thousands)", min_value=0, value=5)
        basic_insurance_3w = st.number_input("Basic Insurance (Thousands)", min_value=0, value=15)
        annual_maintenance_cost = st.number_input("Annual Maintenance/Van (Thousands)", min_value=0, value=14)
        battery_replacement_cost_2w = st.number_input("Annual Battery Replacement - 2W (Thousands)", min_value=0, value=2)
        battery_replacement_cost_3w = st.number_input("Annual Battery Replacement - 3W (Thousands)", min_value=0, value=10)

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
        hourly_delivery_3w = st.number_input("Deliveries per Hour - 3W", min_value=0, value=6)
        work_hours = st.number_input("Work hours per day", min_value=0, value=8)
        work_days = st.number_input("Work days per year", min_value=0, value=300)

        # Downtime costs/percentages
        st.markdown("##### Downtime Percentages")
        battery_issues = st.number_input("Percentage of battery problems", min_value=0, max_value=100, value=5)
        software_issues = st.number_input("Percentage of software problems", min_value=0, max_value=100, value=6)

    with col[2]:
        # Calculating costs
        if fleet_type == "Captive Fleet":
            # st.metric(label="Revenue", value=Revenue, delta="_", delta_color="normal")
            # Cost of new vehicles
            on_road_price_ev2w = vaqui_cost_ev2w - gov_subsidy_ev2w - state_incentive_ev2w
            on_road_price_ev3w = vaqui_cost_ev3w - gov_subsidy_ev3w - state_incentive_ev3w
            init_cost = (on_road_price_ev2w * num_vans_2w + on_road_price_ev3w * num_vans_3w) * 1000
            coulomb_init_cost = init_cost + coulomb_partner_cost

            # Get annual revenue
            annual_revenue = get_annual_revenue(battery_issues, software_issues, hourly_delivery_2w, num_vans_2w, hourly_delivery_3w, num_vans_3w, work_hours, delivery_rev, work_days)
            coulomb_annual_revenue = get_annual_revenue(battery_issues * 0.5, software_issues * 0.5, hourly_delivery_2w, num_vans_2w, hourly_delivery_3w, num_vans_3w, work_hours, delivery_rev, work_days)

            # Get annual costs
            annual_costs = get_annual_cost(daily_average_miles_2w, num_vans_2w, daily_average_miles_3w, num_vans_3w, electricity_cost_per_km,
                    work_hours, work_days, annual_maintenance_cost, battery_replacement_cost_2w, battery_replacement_cost_3w,
                    driver_wage_2w, driver_wage_3w, battery_issues, software_issues, annual_revenue) + basic_insurance_2w + basic_insurance_3w
            coulomb_annual_costs = get_annual_cost(daily_average_miles_2w, num_vans_2w, daily_average_miles_3w, num_vans_3w, electricity_cost_per_km,
                    work_hours, work_days, annual_maintenance_cost * 0.75, battery_replacement_cost_2w * 0.75, battery_replacement_cost_3w * 0.75,
                    driver_wage_2w, driver_wage_3w, battery_issues * 0.5, software_issues * 0.5, coulomb_annual_revenue) + basic_insurance_2w + basic_insurance_3w
        elif fleet_type == "DCO Fleet":
            # Calculate Initial Costs
            init_cost = training_cost_per_driver * (num_vans_2w + num_vans_3w) * 1000 + vehicle_inspection_cost * (num_vans_2w + num_vans_3w) * 1000 + platform_operational_cost * 1000
            coulomb_init_cost = init_cost + coulomb_partner_cost

            # Calculate Revenue
            annual_revenue_gross = get_annual_revenue(battery_issues, software_issues, hourly_delivery_2w, num_vans_2w, hourly_delivery_3w, num_vans_3w, work_hours, delivery_rev, work_days)
            annual_revenue = annual_revenue_gross * (management_fee_percentage / 100)   # Company revenue after driver share
            coulomb_annual_revenue_gross = get_annual_revenue(battery_issues * 0.5, software_issues * 0.5, hourly_delivery_2w, num_vans_2w, hourly_delivery_3w, num_vans_3w, work_hours, delivery_rev, work_days)
            coulomb_annual_revenue = coulomb_annual_revenue_gross * (management_fee_percentage / 100)  # Company revenue after driver share

            # Calculate Annual Cost
            annual_costs = (
                get_annual_cost(daily_average_miles_2w, num_vans_2w, daily_average_miles_3w, num_vans_3w, electricity_cost_per_km,
                    work_hours, work_days, annual_maintenance_cost, battery_replacement_cost_2w, battery_replacement_cost_3w,
                    driver_wage_2w, driver_wage_3w, battery_issues, software_issues, annual_revenue_gross)
        	        + platform_operational_cost * 1000 # Platform operational cost (e.g., scheduling, system, customer service)
                    + vehicle_inspection_cost * (num_vans_2w + num_vans_3w) * 1000  # Regular vehicle inspection cost
            )
            coulomb_annual_costs = (
                get_annual_cost(daily_average_miles_2w, num_vans_2w, daily_average_miles_3w, num_vans_3w, electricity_cost_per_km,
                    work_hours, work_days, annual_maintenance_cost * 0.75, battery_replacement_cost_2w * 0.75, battery_replacement_cost_3w * 0.75,
                    driver_wage_2w, driver_wage_3w, battery_issues * 0.5, software_issues * 0.5, coulomb_annual_revenue)
                    + platform_operational_cost * 1000 # Platform operational cost (e.g., scheduling, system, customer service)
                    + vehicle_inspection_cost * (num_vans_2w + num_vans_3w) * 1000  # Regular vehicle inspection cost
            )
        elif fleet_type == "Contracted Fleet":
            # Cost of contracted vehicles
            on_road_price_ev2w = contract_cost_ev2w * 12 + basic_insurance_2w
            on_road_price_ev3w = contract_cost_ev3w * 12 + basic_insurance_3w
            init_cost = (on_road_price_ev2w * num_vans_2w + on_road_price_ev3w * num_vans_3w) * 1000
            coulomb_init_cost = init_cost + coulomb_partner_cost

            # Calculate total revenue accounting for missed_deliveries
            annual_revenue = get_annual_revenue(battery_issues, software_issues, hourly_delivery_2w, num_vans_2w, hourly_delivery_3w, num_vans_3w, work_hours, delivery_rev, work_days)
            coulomb_annual_revenue = get_annual_revenue(battery_issues * 0.5, software_issues * 0.5, hourly_delivery_2w, num_vans_2w, hourly_delivery_3w, num_vans_3w, work_hours, delivery_rev, work_days)

            # Calculate costs
            annual_costs = get_annual_cost(daily_average_miles_2w, num_vans_2w, daily_average_miles_3w, num_vans_3w, electricity_cost_per_km,
                    work_hours, work_days, annual_maintenance_cost, battery_replacement_cost_2w, battery_replacement_cost_3w,
                    driver_wage_2w, driver_wage_3w, battery_issues, software_issues, annual_revenue) + init_cost
            coulomb_annual_costs = get_annual_cost(daily_average_miles_2w, num_vans_2w, daily_average_miles_3w, num_vans_3w, electricity_cost_per_km,
                    work_hours, work_days, annual_maintenance_cost * 0.75, battery_replacement_cost_2w * 0.75, battery_replacement_cost_3w * 0.75,
                    driver_wage_2w, driver_wage_3w, battery_issues * 0.5, software_issues * 0.5, coulomb_annual_revenue) + init_cost

        # Calculating data for revenue, costs, profits, and payback_period
        years = list(range(operational_years + 1))
        revenues = [0]
        costs = [init_cost]
        profits = [-init_cost]
        payback_period = None
        coulomb_revenues = [0]
        coulomb_costs = [coulomb_init_cost]
        coulomb_profits = [-coulomb_init_cost]
        coulomb_payback_period = None

        # Calculating data for the graphs
        for year in range(1, operational_years + 1):
            previous_profit = profits[-1]
            previous_coulomb_profit = coulomb_profits[-1]
            yearly_profit = previous_profit + annual_revenue - annual_costs
            coulomb_yearly_profit = previous_coulomb_profit + coulomb_annual_revenue - coulomb_annual_costs

            revenues.append(annual_revenue)
            coulomb_revenues.append(coulomb_annual_revenue)
            costs.append(annual_costs)
            coulomb_costs.append(coulomb_annual_costs)
            profits.append(yearly_profit)
            coulomb_profits.append(coulomb_yearly_profit)
            if previous_profit < 0 < yearly_profit:
                payback_period = year - 1 - previous_profit / (yearly_profit - previous_profit)
            if previous_coulomb_profit < 0 < coulomb_yearly_profit:
                coulomb_payback_period = year - 1 - previous_coulomb_profit / (coulomb_yearly_profit - previous_coulomb_profit)
        
        # Create DataFrame
        profits_data = pd.DataFrame({
            "Year": range(0, operational_years + 1),
            "Revenue (Thousands)": revenues,
            "Cost (Thousands)": costs,
            "Cumulative Profit (Thousands)": profits,
        })
        coulomb_profits_data = pd.DataFrame({
            "Year": range(0, operational_years + 1),
            "Revenue (Thousands)": coulomb_revenues,
            "Cost (Thousands)": coulomb_costs,
            "Cumulative Profit (Thousands)": coulomb_profits,
        })

        # Calculate ROI
        final_profit = profits[-1]  # Last year's cumulative profit
        coulomb_final_profit = coulomb_profits[-1]
        roi = (final_profit / init_cost) * 100 if init_cost > 0 else 0
        coulomb_roi = (coulomb_final_profit / coulomb_init_cost) * 100 if coulomb_init_cost > 0 else 0

        # Calculate cost savings
        total_cost = sum(costs)
        coulomb_total_cost = sum(coulomb_costs)

        # Fleet utilization
        total_possible_hours = 8 * 300
        total_hours = work_hours * work_days * (1 - (battery_issues + software_issues) / 100)
        coulomb_total_hours = work_hours * work_days * (1 - (battery_issues + software_issues) * 0.5 / 100)
        fleet_utilization = total_hours / total_possible_hours
        coulomb_fleet_utilization = coulomb_total_hours / total_possible_hours

        using_coulomb = st.toggle("Using Coulomb", value=True)
        # Display Metrics
        if using_coulomb:
            st.metric(label="Return on Investment (ROI)", value=f"{coulomb_roi:.2f}%", delta=f"{coulomb_roi - 100:.2f}%", delta_color="normal")
            if payback_period:
                st.metric(label="Payback Period (Years)", value=f"{coulomb_payback_period:.2f}", delta=f"{coulomb_payback_period - payback_period:.2f}", delta_color="inverse")
            else:
                st.metric(label="Payback Period (Years)", value=f"Cannot with given years of operation")
            st.metric(label="Fleet Utilization", value=f"{coulomb_fleet_utilization:,.2f}", delta=f"{coulomb_fleet_utilization - fleet_utilization:.2f}", delta_color="normal")
            st.metric(label="Cost Savings", value=f"{total_cost - coulomb_total_cost:,.2f}", delta=f"{total_cost - coulomb_total_cost:,.2f}", delta_color="normal")
        else:
            st.metric(label="Return on Investment (ROI)", value=f"{roi:.2f}%", delta=f"{roi - 100:.2f}%", delta_color="normal")
            if payback_period:
                st.metric(label="Payback Period (Years)", value=f"{payback_period:.2f}", delta=f"{payback_period - coulomb_payback_period:.2f}", delta_color="inverse")
            else:
                st.metric(label="Payback Period (Years)", value=f"Cannot with given years of operation")
            st.metric(label="Fleet Utilization", value=f"{fleet_utilization:,.2f}", delta=f"{fleet_utilization - coulomb_fleet_utilization:.2f}", delta_color="normal")
            st.metric(label="Cost Savings", value=f"0", delta=f"{coulomb_total_cost - total_cost:,.2f}", delta_color="normal")

    
    with col[1]:
        st.title("Coulomb AI Metrics")
        
        # Testing something
        data = {
            "Category": ["A", "B", "C", "D", "E"],
            "Values": [10, 20, 15, 30, 25],
        }

        df = pd.DataFrame(data)

        st.markdown("### Cumulative Net Profits")
        generate_plot(profits_data, payback_period)
        st.markdown("### Coulomb Benefits")
        st.text("By using Coulomb, operational costs (maintenance and battery) can be lowered by at least 25%")
        st.text("It also decreases the chance of battery/software issues by 50%, decreasing missed deliveries")
        st.text("Below, you can see the cumulative net profits if you were using Coulomb")
        st.markdown("### Cumulative Net Profits w/Coulomb")
        generate_plot(coulomb_profits_data, coulomb_payback_period)

with tab2:
    st.markdown("### Spreadsheet")
    st.text("Here is our spreadsheet of the costs and calculations.")
    st.text("In each tab on the bottom, you can manipulate the inputs for a given year to change see how cost, revenue, and profits will change.")
    st.text("On the Yearly Revenue tab, all operational inputs and downtime costs are displayed. We assume the values will not change over the years.")
    st.text("We also provide a tab for sunk costs, including additional information for different types of fleets.")
    st.text("We provide clear references for our number estimations in the references tab.")
    st.text("As of now, our spreadsheet only models the first 5 years. However, the Metrics tab allows for more variability for inputs and logistics.")
    url = "https://docs.google.com/spreadsheets/d/1o2Z9GmpwzgQJ2hTYIkDM3LvWJkwGQQFH7ETarsZGHK4/edit?usp=sharing"
    st.markdown("Here is the [link to the spreadsheet](%s)" % url)