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

tab1, tab2 = st.tabs(["Metrics", "Other"])

################## Notes #####################

# Colors = #47fff4, #9d9fff, #6d72f6, #f3d94e
##############################################

conversion_rate = 82

if "currency" not in st.session_state:
    st.session_state.currency = "₹"
if "inputs" not in st.session_state:
    # Default values
    st.session_state.inputs = {
        "coulomb_partner_cost": 1800,
        "vaqui_cost_ev2w": 80 * 1000,
        "vaqui_cost_ev3w": 350 * 1000,
        "gov_subsidy_ev2w": 15 * 1000,
        "gov_subsidy_ev3w": 40 * 1000,
        "state_incentive_ev2w": 0 * 1000,
        "state_incentive_ev3w": 0 * 1000,
        "contract_cost_ev2w": 1 * 1000,
        "contract_cost_ev3w": 4 * 1000,
        "platform_operational_cost": 0 * 1000,
        "vehicle_inspection_cost": 0 * 1000,
        "basic_insurance_2w": 5 * 1000,
        "basic_insurance_3w": 15 * 1000,
        "annual_maintenance_cost": 5 * 1000,
        "battery_replacement_cost_2w": 0 * 1000,
        "battery_replacement_cost_3w": 0 * 1000,
        "electricity_cost_per_km": 0.90,
        "rev_km": 30.0,
        "driver_wage_2w": 87.0,
        "driver_wage_3w": 100.0
    }

# Function to convert values between currencies
def convert_currency(value, from_currency, to_currency):
    if from_currency == to_currency:
        return value
    if from_currency == "₹" and to_currency == "$":
        return value / conversion_rate
    if from_currency == "$" and to_currency == "₹":
        return value * conversion_rate

# Function to calculate annual revenue
def get_annual_revenue(battery_issues, software_issues, num_vans_2w, num_vans_3w,
                        rev_km, work_days, daily_average_km_2w, daily_average_km_3w):
    missed_km_percentage = (battery_issues + software_issues) / 100 # Lost Revenue
    daily_km_2w = daily_average_km_2w * num_vans_2w
    daily_km_3w = daily_average_km_3w * num_vans_3w # Daily Revenue
    annual_revenue = (
        (daily_km_2w + daily_km_3w) * (1 - missed_km_percentage) * work_days * rev_km
    )
    return annual_revenue

# Function to calculate annual cost
def get_annual_cost(daily_average_km_2w, num_vans_2w, daily_average_km_3w, num_vans_3w, electricity_cost_per_km,
                    work_hours, work_days, annual_maintenance_cost, battery_replacement_cost_2w, battery_replacement_cost_3w,
                    driver_wage_2w, driver_wage_3w, battery_issues, software_issues, annual_revenue, amortization_cost,
                    basic_insurance_2w, basic_insurance_3w):
    annual_electricity = (daily_average_km_2w * num_vans_2w + daily_average_km_3w * num_vans_3w) * electricity_cost_per_km * work_days
    annual_maintenance = annual_maintenance_cost * (num_vans_2w + num_vans_3w)
    annual_battery = battery_replacement_cost_2w * num_vans_2w + battery_replacement_cost_3w * num_vans_3w
    annual_driver = (driver_wage_2w * num_vans_2w + driver_wage_3w * num_vans_3w) * work_hours * work_days
    annual_downtime = (battery_issues + software_issues) / 100 * annual_revenue
    annual_insurance = (basic_insurance_2w * num_vans_2w + basic_insurance_3w * num_vans_3w)
    annual_costs = annual_electricity + annual_maintenance + annual_battery + annual_driver + annual_downtime + amortization_cost + annual_insurance
    return annual_costs

with tab1:
    col = st.columns((1.7, 4.5, 1.8), gap='medium')

    with col[0]:
        new_currency = st.selectbox("What kind of currency unit?", ["₹", "$"], index=0 if st.session_state.currency == "₹" else 1)

        # If currency changes, convert all stored input values
        if new_currency != st.session_state.currency:
            for key, value in st.session_state.inputs.items():
                st.session_state.inputs[key] = convert_currency(value, st.session_state.currency, new_currency)
            st.session_state.currency = new_currency
        coulomb_partner_cost = st.session_state.inputs["coulomb_partner_cost"]
        
        # Inputs
        fleet_type = st.radio("Type of fleet", ["Captive Fleet", "Contracted Fleet", "DCO Fleet"])
        operational_years = st.number_input("Years of operation", min_value=1, value=5)
        # Inputs specific for type of fleet
        if fleet_type == "Captive Fleet": 
            st.markdown("##### Inputs for owning fleet")
            vaqui_cost_ev2w = st.number_input("Vehicle Acquisition - 2W (Thousands)", min_value=0.0, value=st.session_state.inputs["vaqui_cost_ev2w"] / 1000) * 1000
            st.session_state.inputs["vaqui_cost_ev2w"] = vaqui_cost_ev2w
            vaqui_cost_ev3w = st.number_input("Vehicle Acquisition - 3W (Thousands)", min_value=0.0, value=st.session_state.inputs["vaqui_cost_ev3w"] / 1000) * 1000
            st.session_state.inputs["vaqui_cost_ev3w"] = vaqui_cost_ev3w
            gov_subsidy_ev2w = st.number_input("Government Subsidy - 2W (Thousands)", min_value=0.0, value=st.session_state.inputs["gov_subsidy_ev2w"] / 1000) * 1000
            st.session_state.inputs["gov_subsidy_ev2w"] = gov_subsidy_ev2w
            gov_subsidy_ev3w = st.number_input("Government Subsidy - 3W (Thousands)", min_value=0.0, value=st.session_state.inputs["gov_subsidy_ev3w"] / 1000) * 1000
            st.session_state.inputs["gov_subsidy_ev3w"] = gov_subsidy_ev3w
            state_incentive_ev2w = st.number_input("State-level Incentive - 2W (Thousands)", min_value=0.0, value=st.session_state.inputs["state_incentive_ev2w"] / 1000) * 1000
            st.session_state.inputs["state_incentive_ev2w"] = state_incentive_ev2w
            state_incentive_ev3w = st.number_input("State-level Incentive - 3W (Thousands)", min_value=0.0, value=st.session_state.inputs["state_incentive_ev3w"] / 1000) * 1000
            st.session_state.inputs["state_incentive_ev3w"] = state_incentive_ev3w

        elif fleet_type == "Contracted Fleet":
            st.markdown("##### Contract Logistics")
            contract_period = st.number_input("Contract Period (Months)", min_value=0, value= operational_years * 12)
            contract_cost_ev2w = st.number_input("Contract Cost - 2W (per month)(Thousands)", min_value=0.0, value=st.session_state.inputs["contract_cost_ev2w"] / 1000) * 1000
            st.session_state.inputs["contract_cost_ev2w"] = contract_cost_ev2w
            contract_cost_ev3w = st.number_input("Contract Cost - 3W (per month)(Thousands)", min_value=0.0, value=st.session_state.inputs["contract_cost_ev3w"] / 1000) * 1000
            st.session_state.inputs["contract_cost_ev3w"] = contract_cost_ev3w

        elif fleet_type == "DCO Fleet":
            st.markdown("##### DCO Logistics")
            vaqui_cost_ev2w = st.number_input("Vehicle Acquisition - 2W (Thousands)", min_value=0.0, value=st.session_state.inputs["vaqui_cost_ev2w"] / 1000) * 1000
            st.session_state.inputs["vaqui_cost_ev2w"] = vaqui_cost_ev2w
            vaqui_cost_ev3w = st.number_input("Vehicle Acquisition - 3W (Thousands)", min_value=0.0, value=st.session_state.inputs["vaqui_cost_ev3w"] / 1000) * 1000
            st.session_state.inputs["vaqui_cost_ev3w"] = vaqui_cost_ev3w
            gov_subsidy_ev2w = st.number_input("Government Subsidy - 2W (Thousands)", min_value=0.0, value=st.session_state.inputs["gov_subsidy_ev2w"] / 1000) * 1000
            st.session_state.inputs["gov_subsidy_ev2w"] = gov_subsidy_ev2w
            gov_subsidy_ev3w = st.number_input("Government Subsidy - 3W (Thousands)", min_value=0.0, value=st.session_state.inputs["gov_subsidy_ev3w"] / 1000) * 1000
            st.session_state.inputs["gov_subsidy_ev3w"] = gov_subsidy_ev3w
            state_incentive_ev2w = st.number_input("State-level Incentive - 2W (Thousands)", min_value=0.0, value=st.session_state.inputs["state_incentive_ev2w"] / 1000) * 1000
            st.session_state.inputs["state_incentive_ev2w"] = state_incentive_ev2w
            state_incentive_ev3w = st.number_input("State-level Incentive - 3W (Thousands)", min_value=0.0, value=st.session_state.inputs["state_incentive_ev3w"] / 1000) * 1000
            st.session_state.inputs["state_incentive_ev3w"] = state_incentive_ev3w

        # Additional Logistics consistent across all types of fleets
        basic_insurance_2w = st.number_input("Basic Insurance - 2W (Thousands)", min_value=0.0, value=st.session_state.inputs["basic_insurance_2w"] / 1000) * 1000
        st.session_state.inputs["basic_insurance_2w"] = basic_insurance_2w
        basic_insurance_3w = st.number_input("Basic Insurance - 3W (Thousands)", min_value=0.0, value=st.session_state.inputs["basic_insurance_3w"] / 1000) * 1000
        st.session_state.inputs["basic_insurance_3w"] = basic_insurance_3w
        annual_maintenance_cost = st.number_input("Annual Maintenance/Van (Thousands)", min_value=0.0, value=st.session_state.inputs["annual_maintenance_cost"] / 1000) * 1000
        st.session_state.inputs["annual_maintenance_cost"] = annual_maintenance_cost
        battery_replacement_cost_2w = st.number_input("Annual Battery Replacement - 2W (Thousands)", min_value=0.0, value=st.session_state.inputs["battery_replacement_cost_2w"] / 1000) * 1000
        st.session_state.inputs["battery_replacement_cost_2w"] = battery_replacement_cost_2w
        battery_replacement_cost_3w = st.number_input("Annual Battery Replacement - 3W (Thousands)", min_value=0.0, value=st.session_state.inputs["battery_replacement_cost_3w"] / 1000) * 1000
        st.session_state.inputs["battery_replacement_cost_3w"] = battery_replacement_cost_3w

        # Delivery Logistics
        st.markdown("##### Delivery Logistics")
        num_vans_2w = st.number_input("Number of Vans - 2W", min_value=0, value=0)
        num_vans_3w = st.number_input("Number of Vans - 3W", min_value=0, value=1)
        daily_average_km_2w = st.number_input("Average Daily km - 2W", min_value=0, value=65)
        daily_average_km_3w = st.number_input("Average Daily km - 3W", min_value=0, value=90)
        electricity_cost_per_km = st.number_input("Electricity Cost per km", min_value=0.0, value=st.session_state.inputs["electricity_cost_per_km"])
        st.session_state.inputs["electricity_cost_per_km"] = electricity_cost_per_km

        # Worker Logistics
        st.markdown("##### Worker Logistics")
        rev_km = st.number_input("Revenue per km", min_value=0.0, value=st.session_state.inputs["rev_km"])
        st.session_state.inputs["rev_km"] = rev_km
        driver_wage_2w = st.number_input("Hourly Driver Wage - 2W", min_value=0.0, value=st.session_state.inputs["driver_wage_2w"])
        st.session_state.inputs["driver_wage_2w"] = driver_wage_2w
        driver_wage_3w = st.number_input("Hourly Driver Wage - 3W", min_value=0.0, value=st.session_state.inputs["driver_wage_3w"])
        st.session_state.inputs["driver_wage_3w"] = driver_wage_3w
        work_hours = st.number_input("Work hours per day", min_value=0, value=10)
        work_days = st.number_input("Work days per year", min_value=0, value=300)

        # Downtime costs/percentages
        st.markdown("##### Downtime Percentages")
        battery_issues = st.number_input("Percentage of battery problems faced per year", min_value=0, max_value=100, value=2)
        software_issues = st.number_input("Percentage of software problems faced per year", min_value=0, max_value=100, value=3)

    with col[2]:
        # Calculating costs
        if fleet_type == "Captive Fleet":
            # Cost of new vehicles (Initial Costs)
            on_road_price_ev2w = vaqui_cost_ev2w - gov_subsidy_ev2w - state_incentive_ev2w
            on_road_price_ev3w = vaqui_cost_ev3w - gov_subsidy_ev3w - state_incentive_ev3w
            init_cost = (on_road_price_ev2w * num_vans_2w + on_road_price_ev3w * num_vans_3w)
            coulomb_init_cost = init_cost

            # Get annual revenue
            annual_revenue = get_annual_revenue(battery_issues, software_issues, num_vans_2w, num_vans_3w, rev_km, work_days, daily_average_km_2w, daily_average_km_3w)
            coulomb_annual_revenue = get_annual_revenue(battery_issues * 0.5, software_issues * 0.5, num_vans_2w, num_vans_3w, rev_km, work_days, daily_average_km_2w, daily_average_km_3w)

            # Get annual costs
            amortization_cost = (on_road_price_ev2w * num_vans_2w + on_road_price_ev3w + num_vans_3w) / operational_years
            annual_costs = get_annual_cost(daily_average_km_2w, num_vans_2w, daily_average_km_3w, num_vans_3w, electricity_cost_per_km,
                    work_hours, work_days, annual_maintenance_cost, battery_replacement_cost_2w, battery_replacement_cost_3w,
                    driver_wage_2w, driver_wage_3w, battery_issues, software_issues, annual_revenue, amortization_cost, basic_insurance_2w, basic_insurance_3w)
            coulomb_annual_costs = get_annual_cost(daily_average_km_2w, num_vans_2w, daily_average_km_3w, num_vans_3w, electricity_cost_per_km,
                    work_hours, work_days, annual_maintenance_cost * 0.75, battery_replacement_cost_2w * 0.75, battery_replacement_cost_3w * 0.75,
                    driver_wage_2w, driver_wage_3w, battery_issues * 0.5, software_issues * 0.5, coulomb_annual_revenue, amortization_cost, basic_insurance_2w, basic_insurance_3w) + coulomb_partner_cost * (num_vans_2w + num_vans_3w)
        elif fleet_type == "DCO Fleet":
            # Calculate Initial Costs
            on_road_price_ev2w = vaqui_cost_ev2w - gov_subsidy_ev2w - state_incentive_ev2w
            on_road_price_ev3w = vaqui_cost_ev3w - gov_subsidy_ev3w - state_incentive_ev3w
            init_cost = (on_road_price_ev2w * num_vans_2w + on_road_price_ev3w * num_vans_3w)
            coulomb_init_cost = init_cost

            # Calculate Revenue
            annual_revenue = get_annual_revenue(battery_issues, software_issues, num_vans_2w, num_vans_3w, rev_km, work_days, daily_average_km_2w, daily_average_km_3w)
            coulomb_annual_revenue = get_annual_revenue(battery_issues * 0.5, software_issues * 0.5, num_vans_2w, num_vans_3w, rev_km, work_days, daily_average_km_2w, daily_average_km_3w)

            # Calculate Annual Cost
            amortization_cost = (on_road_price_ev2w * num_vans_2w + on_road_price_ev3w + num_vans_3w) / operational_years
            annual_costs = get_annual_cost(daily_average_km_2w, num_vans_2w, daily_average_km_3w, num_vans_3w, electricity_cost_per_km,
                    work_hours, work_days, annual_maintenance_cost, battery_replacement_cost_2w, battery_replacement_cost_3w,
                    driver_wage_2w, driver_wage_3w, battery_issues, software_issues, annual_revenue, amortization_cost, basic_insurance_2w, basic_insurance_3w)
            coulomb_annual_costs = get_annual_cost(daily_average_km_2w, num_vans_2w, daily_average_km_3w, num_vans_3w, electricity_cost_per_km,
                    work_hours, work_days, annual_maintenance_cost * 0.75, battery_replacement_cost_2w * 0.75, battery_replacement_cost_3w * 0.75,
                    driver_wage_2w, driver_wage_3w, battery_issues * 0.5, software_issues * 0.5, coulomb_annual_revenue, amortization_cost, basic_insurance_2w, basic_insurance_3w) + coulomb_partner_cost * (num_vans_2w + num_vans_3w)
        elif fleet_type == "Contracted Fleet":
            # Cost of contracted vehicles (Initial Costs)
            on_road_price_ev2w = contract_cost_ev2w * 12
            on_road_price_ev3w = contract_cost_ev3w * 12
            init_cost = (on_road_price_ev2w * num_vans_2w + on_road_price_ev3w * num_vans_3w)
            coulomb_init_cost = init_cost

            # Calculate total revenue accounting for missed_deliveries
            annual_revenue = get_annual_revenue(battery_issues, software_issues, num_vans_2w, num_vans_3w, rev_km, work_days, daily_average_km_2w, daily_average_km_3w)
            coulomb_annual_revenue = get_annual_revenue(battery_issues * 0.5, software_issues * 0.5, num_vans_2w, num_vans_3w, rev_km, work_days, daily_average_km_2w, daily_average_km_3w)

            # Calculate costs
            annual_costs = get_annual_cost(daily_average_km_2w, num_vans_2w, daily_average_km_3w, num_vans_3w, electricity_cost_per_km,
                    work_hours, work_days, annual_maintenance_cost, battery_replacement_cost_2w, battery_replacement_cost_3w,
                    driver_wage_2w, driver_wage_3w, battery_issues, software_issues, annual_revenue, 0, basic_insurance_2w, basic_insurance_3w) + init_cost
            coulomb_annual_costs = get_annual_cost(daily_average_km_2w, num_vans_2w, daily_average_km_3w, num_vans_3w, electricity_cost_per_km,
                    work_hours, work_days, annual_maintenance_cost * 0.75, battery_replacement_cost_2w * 0.75, battery_replacement_cost_3w * 0.75,
                    driver_wage_2w, driver_wage_3w, battery_issues * 0.5, software_issues * 0.5, coulomb_annual_revenue, 0, basic_insurance_2w, basic_insurance_3w) + init_cost + coulomb_partner_cost * (num_vans_2w + num_vans_3w)

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
            "Revenue": revenues,
            "Cost": costs,
            "Cumulative Profit": profits,
        })
        coulomb_profits_data = pd.DataFrame({
            "Year": range(0, operational_years + 1),
            "Revenue": coulomb_revenues,
            "Cost": coulomb_costs,
            "Cumulative Profit": coulomb_profits,
        })
        
        # Calculate cost savings
        total_cost = sum(costs)
        coulomb_total_cost = sum(coulomb_costs)

        # Calculate ROI
        final_profit = profits[-1]  # Last year's cumulative profit
        coulomb_final_profit = coulomb_profits[-1]
        roi = (final_profit / total_cost) * 100 if total_cost > 0 else 0
        coulomb_roi = (coulomb_final_profit / coulomb_total_cost) * 100 if coulomb_total_cost > 0 else 0

        # Fleet utilization
        total_possible_hours = 10 * 300
        total_hours = work_hours * work_days * (1 - (battery_issues + software_issues) / 100)
        coulomb_total_hours = work_hours * work_days * (1 - (battery_issues + software_issues) * 0.5 / 100)
        fleet_utilization = total_hours / total_possible_hours
        coulomb_fleet_utilization = coulomb_total_hours / total_possible_hours

        using_coulomb = st.toggle("Using Coulomb", value=True)
        # Display Metrics
        if using_coulomb:
            st.metric(label="Return on Investment (ROI)", value=f"{coulomb_roi:.2f}%", delta=f"{coulomb_roi - 100:.2f}%", delta_color="normal")
            if coulomb_payback_period and payback_period:
                st.metric(label="Payback Period (Years)", value=f"{coulomb_payback_period:.2f}", delta=f"{coulomb_payback_period - payback_period:.2f}", delta_color="inverse")
            elif coulomb_payback_period:
                st.metric(label="Payback Period (Years)", value=f"{coulomb_payback_period:.2f}")
            else:
                st.metric(label="Payback Period (Years)", value=f"Cannot with given years of operation")
            st.metric(label="Fleet Utilization", value=f"{coulomb_fleet_utilization:,.2f}", delta=f"{coulomb_fleet_utilization - fleet_utilization:.2f}", delta_color="normal")
            st.metric(label="Cost Savings", value=f"{new_currency}{total_cost - coulomb_total_cost:,.2f}", delta=f"{total_cost - coulomb_total_cost:,.2f}", delta_color="normal")
        else:
            st.metric(label="Return on Investment (ROI)", value=f"{roi:.2f}%", delta=f"{roi - 100:.2f}%", delta_color="normal")
            if coulomb_payback_period and payback_period:
                st.metric(label="Payback Period (Years)", value=f"{payback_period:.2f}", delta=f"{payback_period - coulomb_payback_period:.2f}", delta_color="inverse")
            elif payback_period:
                st.metric(label="Payback Period (Years)", value=f"{payback_period:.2f}")
            else:
                st.metric(label="Payback Period (Years)", value=f"Cannot with given years of operation")
            st.metric(label="Fleet Utilization", value=f"{fleet_utilization:,.2f}", delta=f"{fleet_utilization - coulomb_fleet_utilization:.2f}", delta_color="normal")
            st.metric(label="Cost Savings", value=f"{new_currency}0", delta=f"{coulomb_total_cost - total_cost:,.2f}", delta_color="normal")

    
    with col[1]:
        st.title("Coulomb AI Metrics")
        
        # Testing something
        data = {
            "Category": ["A", "B", "C", "D", "E"],
            "Values": [10, 20, 15, 30, 25],
        }

        df = pd.DataFrame(data)

        st.markdown("### Cumulative Net Profits")
        generate_plot(profits_data, payback_period, new_currency)
        st.markdown("### Coulomb Benefits")
        st.text("By using Coulomb, operational costs (maintenance and battery) can be lowered by at least 25%")
        st.text("It also decreases the chance of battery/software issues by 50%, decreasing missed deliveries")
        st.text("Below, you can see the cumulative net profits if you were using Coulomb")
        st.markdown("### Cumulative Net Profits w/Coulomb")
        generate_plot(coulomb_profits_data, coulomb_payback_period, new_currency)