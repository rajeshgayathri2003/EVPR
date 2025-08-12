# This code is based on the algorithm proposed by Abbasi et al in "A Coupled Game Theory and Lyapunov Optimization Approach to Electric Vehicle Charging at Fast Charging Stations"
# to achieve the Nash Equilibrium 

from helper_funs1 import energy_requirement_of_customers, profit_of_kth_station_at_time_t, calculate_energy_n, calculate_base_sensitivity, calculate_alpha, calculate_behavioural_response, calculate_utility
import numpy as np
from datetime import datetime
import argparse
import copy
import matplotlib.pyplot as plt
import random
from csv_plots import write_to_csv
import csv
import os

def assign_vehicle_details(Cn, cs_sell_price, lambda_sell, initial_soc, final_soc, station, n):
    try:
        with open('EVdata.csv', 'r') as file:
            csv_file = csv.reader(file)
            
            for i, lines in enumerate(csv_file):
                if i >= n:  # Ensure we don't exceed the number of vehicles
                    break
                    
                lambda_sell[i, station] = cs_sell_price
                Cn[i, station] = float(lines[1])
                initial_soc[i, station] = float(lines[2])
                final_soc[i, station] = float(lines[3])
    except FileNotFoundError:
        print("EVdata.csv not found. Using random values instead.")
        for i in range(n):
            lambda_sell[i, station] = cs_sell_price
            Cn[i, station] = random.uniform(30, 60)  # Random battery capacity
            initial_soc[i, station] = random.uniform(0.1, 0.4)  # Random initial SOC
            final_soc[i, station] = random.uniform(0.7, 0.9)  # Random final SOC

def combined_plot_price(profit_variation, omega_variation, cs_sell_price_variation, demand_variation, nash, station):
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Convert all inputs to numpy arrays if they aren't already
    profit_variation = np.array(profit_variation)
    omega_variation = np.array(omega_variation)
    demand_variation = np.array(demand_variation)
    cs_sell_price_variation = np.array(cs_sell_price_variation)

    # Calculate averages properly based on array dimensions
    if profit_variation.ndim == 1:
        avg_profit = profit_variation
    elif profit_variation.ndim == 2:
        avg_profit = np.mean(profit_variation, axis=1)
    else:
        avg_profit = np.mean(profit_variation, axis=(1, 2))

    if omega_variation.ndim == 1:
        avg_omega = omega_variation
    elif omega_variation.ndim == 2:
        avg_omega = np.mean(omega_variation, axis=1)
    else:
        avg_omega = np.mean(omega_variation, axis=(1, 2))

    if demand_variation.ndim == 1:
        avg_demand = demand_variation
    elif demand_variation.ndim == 2:
        avg_demand = np.mean(demand_variation, axis=1)
    else:
        avg_demand = np.mean(demand_variation, axis=(1, 2))
    
    # Get price points (remove the initial duplicate)
    if cs_sell_price_variation.ndim == 1:
        price_plot = cs_sell_price_variation[1:]
    elif cs_sell_price_variation.ndim == 2:
        price_plot = cs_sell_price_variation[1:, 0]
    else:
        price_plot = cs_sell_price_variation[1:, 0, 0]

    # Plot individual vehicle curves with transparency (only if we have vehicle-level data)
    if omega_variation.ndim > 1:
        try:
            for v in range(min(5, omega_variation.shape[1])):  # Plot first 5 vehicles for clarity
                if omega_variation.ndim == 2:
                    ax1.plot(price_plot, omega_variation[:, v], color='r', alpha=0.2, linewidth=0.5)
                    ax2.plot(price_plot, demand_variation[:, v], color='g', alpha=0.2, linewidth=0.5)
                else:
                    ax1.plot(price_plot, omega_variation[:, v, 0], color='r', alpha=0.2, linewidth=0.5)
                    ax2.plot(price_plot, demand_variation[:, v, 0], color='g', alpha=0.2, linewidth=0.5)
        except Exception as e:
            print(f"Warning: Could not plot individual vehicle curves - {str(e)}")

    # Primary y-axis (Profit & Utility)
    ax1.plot(price_plot, avg_profit, label="Average Profit to Station", color='b', linewidth=2)
    ax1.plot(price_plot, avg_omega, label="Average Utility of EVs", color='r', linestyle='--', linewidth=2)
    ax1.axvline(x=nash, color='m', linestyle='dotted', linewidth=3, label=f'Nash Eq: {nash:.2f}¢')
    
    ax1.set_xlabel("Selling Price of Electricity to EVs (¢)", fontsize=12)
    ax1.set_ylabel("Value (¢)", fontsize=12)
    ax1.tick_params(axis='y', labelsize=10)
    ax1.tick_params(axis='x', labelsize=10)

    # Secondary y-axis (Demand)
    ax2 = ax1.twinx()
    ax2.plot(price_plot, avg_demand, label="Average EV Demand", linestyle='-.', color='g', linewidth=2)
    ax2.set_ylabel("Average Demand (kWh)", color='g', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='g', labelsize=10)

    # Title and grid
    plt.title(f"Station {station + 1} - Nash Equilibrium Analysis", fontsize=14, pad=20)
    ax1.grid(True, linestyle='--', alpha=0.7)

    # Combine legends
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper center', 
              bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize=10)

    plt.tight_layout()
    plt.savefig(f'station_{station+1}_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def find_nash_equilibrium(grid_price, 
                         cs_sell_price, 
                         lambda_sell, 
                         lambda_purchase, 
                         vehicles, 
                         stations, 
                         Cn, 
                         initial_soc, 
                         final_soc, 
                         E_n_t,
                         lambda_max,
                         lambda_b,
                         delta_lambda=2):
    
    n = vehicles
    k = stations
    
    for station in range(stations):
        prev_profit = 0
        current_cs_sell_price = grid_price
        cs_sell_price_variation = [current_cs_sell_price * np.ones((n, k))]
        demand_variation = []
        omega_variation = []
        profit_variation = []
        sensitivity_variation = [] 
        
        print(f"\n=== Processing Station {station + 1} ===")
        print(f"Initial price: {current_cs_sell_price}¢")
        
        max_iterations = 20
        iteration_count = 0
        
        while iteration_count < max_iterations:
            iteration_count += 1
            current_cs_sell_price += delta_lambda
            
            print(f"\nIteration {iteration_count}: Testing price {current_cs_sell_price}¢")
        
            assign_vehicle_details(Cn, current_cs_sell_price, lambda_sell, initial_soc, final_soc, station, n)
            
            lambda_sell_append = copy.deepcopy(lambda_sell)
            cs_sell_price_variation.append(lambda_sell_append)
            
            # Station-specific data
            station_lambda_max = lambda_max[:, station:station+1]
            station_lambda_b = lambda_b[:, station:station+1]
            station_Cn = Cn[:, station:station+1]
            station_initial_soc = initial_soc[:, station:station+1]
            station_final_soc = final_soc[:, station:station+1]
            
            S_b = calculate_base_sensitivity(station_lambda_max, station_lambda_b, station_Cn)
            alpha = calculate_alpha(lambda_sell[:, station:station+1], station_lambda_b, station_lambda_max)
            B_n_t = calculate_behavioural_response(alpha, type_="medium")
            B_n_t_dash = B_n_t
            
            # Avoid division by zero
            soc_diff = station_final_soc - station_initial_soc
            soc_diff[soc_diff == 0] = 0.001
            S_n_t = np.divide(S_b, soc_diff * B_n_t)
            
            # Calculate energy demand
            E_n_t[:, station:station+1][B_n_t_dash == 0] = 0
            mask = B_n_t_dash != 1
            E_n_t[:, station:station+1][mask] = calculate_energy_n(
                station_lambda_max[mask], 
                lambda_sell[:, station:station+1][mask], 
                S_n_t[mask]
            )
            E_n_t[:, station:station+1][B_n_t_dash == 1] = energy_requirement_of_customers(
                station_final_soc[B_n_t_dash == 1], 
                station_initial_soc[B_n_t_dash == 1], 
                station_Cn[B_n_t_dash == 1]
            )
            
            omega = calculate_utility(S_n_t, E_n_t[:, station:station+1], station_lambda_max, lambda_sell[:, station:station+1])
            omega_variation.append(copy.deepcopy(omega))
            
            demand_variation.append(copy.deepcopy(E_n_t[:, station:station+1]))
            sensitivity_variation.append(copy.deepcopy(S_n_t))
            
            profit = profit_of_kth_station_at_time_t(
                lambda_sell[:, station:station+1], 
                lambda_purchase[:, station:station+1], 
                E_n_t[:, station:station+1]
            )
            profit_variation.append(profit)
        
            print(f"Current profit: {profit/100:.2f}¢")
            
            if profit < prev_profit or iteration_count >= max_iterations:
                nash_price = current_cs_sell_price - delta_lambda
                print(f"\nNash Equilibrium found for Station {station + 1} at {nash_price}¢")
                print(f"Final profit: {prev_profit/100:.2f}¢")
                break
                
            prev_profit = profit
            
        # Convert lists to numpy arrays
        cs_sell_price_variation = np.array(cs_sell_price_variation)
        demand_variation = np.array(demand_variation)
        profit_variation = np.array(profit_variation)
        omega_variation = np.array(omega_variation)
        sensitivity_variation = np.array(sensitivity_variation)
        
        # Plot results for this station
        combined_plot_price(profit_variation, omega_variation, cs_sell_price_variation, 
                          demand_variation, nash_price, station)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EV Charging Station Nash Equilibrium Analysis")
    parser.add_argument("--vehicles", type=int, default=40, help="Number of electric vehicles")
    parser.add_argument("--stations", type=int, default=3, help="Number of charging stations")
        
    args = parser.parse_args()
    n = args.vehicles
    k = args.stations
        
    current_hour = datetime.now().hour
    print(f"\nStarting analysis at hour {current_hour}")
    print(f"Configuration: {n} vehicles, {k} stations\n")
        
    # Initialize with random prices (in cents)
    if (6<=current_hour and current_hour<9) or (18<=current_hour and current_hour<22):
        grid_price = cs_sell_price = 9
    
    elif (9<=current_hour and current_hour<16):
        grid_price = cs_sell_price = 6
        
    else:
        grid_price = cs_sell_price = 7.5
            
    delta_lambda = 0.5
            
    # Initialize arrays
    lambda_sell = np.ones((n, k)) * grid_price
    lambda_purchase = np.ones((n, k)) * grid_price
    initial_soc = np.zeros((n, k))
    final_soc = np.zeros((n, k))
    Cn = np.zeros((n, k))
    E_n_t = np.zeros((n, k))
        
    # Price sensitivity parameters
    lambda_max = np.random.randint(16, 20, size=(n, k))  # Max price users will accept
    lambda_b = np.random.randint(8, 12, size=(n, k))    # Price where users become sensitive
    
    find_nash_equilibrium(
        grid_price=grid_price,
        cs_sell_price=cs_sell_price,
        lambda_sell=lambda_sell,
        lambda_purchase=lambda_purchase,
        vehicles=n,
        stations=k,
        Cn=Cn,
        initial_soc=initial_soc,
        final_soc=final_soc,
        E_n_t=E_n_t,
        lambda_max=lambda_max,
        lambda_b=lambda_b,
        delta_lambda=delta_lambda
    )