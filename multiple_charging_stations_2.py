import numpy as np
from datetime import datetime
import argparse
import copy
import random

from helper_funs1 import (
    energy_requirement_of_customers, 
    profit_of_kth_station_at_time_t, 
    calculate_energy_n, 
    calculate_base_sensitivity, 
    calculate_alpha, 
    calculate_behavioural_response, 
    calculate_utility
)

def assign_vehicle_details(Cn, cs_sell_price, lambda_sell, initial_soc, final_soc, station, n):
    for i in range(n):
        lambda_sell[i, station] = cs_sell_price
        Cn[i, station] = 40
        initial_soc[i, station] = 0.1
        final_soc[i, station] = 0.9

def find_nash_equilibrium(cs_sell_price, lambda_sell, lambda_purchase, vehicles, stations, Cn, initial_soc, final_soc, E_n_t, lambda_max, lambda_b, delta_lambda=2):
    # Initialize lists to track variations
    cs_sell_price_variation = [cs_sell_price * np.ones((vehicles, stations))]
    demand_variation = []
    omega_variation = []
    profit_variation = []
    sensitivity_variation = []

    for station in range(stations):
        prev_profit = 0
        
        while True:
            cs_sell_price += delta_lambda
            
            print(f"The present selling price is {cs_sell_price}")
        
            assign_vehicle_details(Cn, cs_sell_price, lambda_sell, initial_soc, final_soc, station, n=vehicles)
            
            lambda_sell_append = copy.deepcopy(lambda_sell)
            cs_sell_price_variation.append(lambda_sell_append)
            
            # Ensure we're working with the current station's data
            station_data = {
                'lambda_max': lambda_max[:, station],
                'lambda_b': lambda_b[:, station],
                'Cn': Cn[:, station],
                'lambda_sell': lambda_sell[:, station],
            }
            
            S_b = calculate_base_sensitivity(
                station_data['lambda_max'][:, np.newaxis], 
                station_data['lambda_b'][:, np.newaxis], 
                station_data['Cn'][:, np.newaxis]
            )
            
            alpha = calculate_alpha(
                station_data['lambda_sell'][:, np.newaxis], 
                station_data['lambda_b'][:, np.newaxis], 
                station_data['lambda_max'][:, np.newaxis]
            )
            
            B_n_t = calculate_behavioural_response(alpha, type_="medium")
            B_n_t_dash = B_n_t.copy()
            
            # Ensure we handle division by zero and different scenarios
            with np.errstate(divide='ignore', invalid='ignore'):
                S_n_t = np.divide(
                    S_b, 
                    (final_soc[:, station] - initial_soc[:, station])[:, np.newaxis] * B_n_t
                )
                S_n_t = np.nan_to_num(S_n_t, 0)  # Replace NaN with 0
            
            # Reset energy for the current station
            E_n_t[:, station] = 0
            
            # Calculate energy based on behavioral responses
            zero_mask = B_n_t_dash == 0
            one_mask = B_n_t_dash == 1
            other_mask = ~(zero_mask | one_mask)
            
            # Handle zero behavior
            if np.any(zero_mask):
                E_n_t[zero_mask, station] = 0
            
            # Handle full charging behavior
            if np.any(one_mask):
                E_n_t[one_mask, station] = energy_requirement_of_customers(
                    final_soc[one_mask, station], 
                    initial_soc[one_mask, station], 
                    Cn[one_mask, station]
                )
            
            # Handle partial charging behavior
            if np.any(other_mask):
                E_n_t[other_mask, station] = calculate_energy_n(
                    station_data['lambda_max'][other_mask][:, np.newaxis], 
                    station_data['lambda_sell'][other_mask][:, np.newaxis], 
                    S_n_t[other_mask, :]
                )
            
            print("The energy demand for the vehicles is", E_n_t[:, station])
            
            # Calculate utility and tracking metrics
            omega = calculate_utility(
                S_n_t, 
                E_n_t[:, station][:, np.newaxis], 
                station_data['lambda_max'][:, np.newaxis], 
                station_data['lambda_sell'][:, np.newaxis]
            )
            omega_append = copy.deepcopy(omega)
            omega_variation.append(omega_append)
            
            demand_variation.append(copy.deepcopy(E_n_t[:, station]))
            sensitivity_variation.append(copy.deepcopy(S_n_t))
            
            # Calculate profit
            profit = profit_of_kth_station_at_time_t(
                lambda_sell[:, station][:, np.newaxis], 
                lambda_purchase[:, station][:, np.newaxis], 
                E_n_t[:, station][:, np.newaxis]
            )
            profit_variation.append(copy.deepcopy(profit))
        
            print(f"The profit is {profit/100}")
            print(f"the profits are {profit}")
            
            if profit < prev_profit:
                print(f"Nash Equilibrium price for station {station} is {cs_sell_price-delta_lambda}")
                break
                
            prev_profit = profit

def main():
    parser = argparse.ArgumentParser(description="Electric Vehicle Charging Station Nash Equilibrium Simulation")
    parser.add_argument("--vehicles", type=int, default=6, help="Total number of vehicles")
    parser.add_argument("--stations", type=int, default=2, help="Total number of charging stations")
        
    args = parser.parse_args()
    n = args.vehicles
    k = args.stations
        
    current_hour = datetime.now().hour
    print(f"The current hour is {current_hour}")
     
    # Initialize parameters
    grid_price = random.randint(10, 18)
    cs_sell_price = grid_price
    print(f"The present grid purchase price is {grid_price}")
            
    delta_lambda = 2
            
    lambda_sell = np.ones((n, k))
    lambda_purchase = np.ones((n, k)) * grid_price
    initial_soc = np.ones((n, k))
    final_soc = np.ones((n, k))
    Cn = np.ones((n, k))
    E_n_t = np.ones((n, k))
        
    # Generate random lambda_max and lambda_b
    lambda_max = np.random.randint(25, 30, size=(n, k))
    lambda_b = np.random.randint(10, 15, size=(n, k))
    
    print("Lambda Max:")
    print(lambda_max)
    print("Lambda B:")
    print(lambda_b)
    
    # Pass lambda_max and lambda_b as parameters
    find_nash_equilibrium(
        cs_sell_price, lambda_sell, lambda_purchase, 
        n, k, Cn, initial_soc, final_soc, E_n_t, 
        lambda_max, lambda_b, delta_lambda=2
    )

if __name__ == "__main__":
    main()