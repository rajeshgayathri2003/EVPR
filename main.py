#This code is based on the algorithm proposed by Abbasi et al in "A Coupled Game Theory and Lyapunov Optimization Approach to Electric Vehicle Charging at Fast Charging Stations"
# to achieve the Nash Equilibrium 

from helper_funs1 import energy_requirement_of_customers, profit_of_kth_station_at_time_t, calculate_energy_n, calculate_base_sensitivity, calculate_alpha, calculate_behavioural_response
import numpy as np
from datetime import datetime
import argparse

if __name__ == "__main__":
    
    #Add the number of vehicles and the number of charging stations
    parser = argparse.ArgumentParser(description="Add the number of vehicels and the number of charging stations")
    parser.add_argument("--vehicles", type=int, default=100, help="Enter the total number of vehicles we are taking into account for the given system")
    parser.add_argument("--stations", type=int, default=20, help="Enter the total number of charging stations in the network")
    
    args = parser.parse_args()
    n = args.vehicles
    k = args.stations
    
    current_hour = datetime.now().hour
    print("The current hour is", current_hour)
    
    #Note: all the grid_prices are given in paise
    
    if (6<=current_hour and current_hour<9) or (18<=current_hour and current_hour<22):
        grid_price = cs_sell_price = 900
    
    elif (9<=current_hour and current_hour<16):
        grid_price = cs_sell_price = 600
        
    else:
        grid_price = cs_sell_price = 750
        
    #Change in price is denoted by delta_lambda
    #Let us assume that initially we sell at the same price as the grid
    delta_lambda = 10
    
    lambda_max = np.ones((n,1))
    lambda_b =  np.ones((n,1))
    lambda_sell = np.ones((n,1))
    lambda_purchase = np.ones((n,1))*grid_price
    Cn = np.ones((n,1))
    
    while True:
        
        #increase the price by 10 paise
        cs_sell_price+=delta_lambda
    
        #Assuming optimal user behaviour we set En,t = En,t*
        lambda_max = 2000*lambda_max
        
        #Minimum price at which the user starts becoming sensitive to the price
        lambda_b = 1500*lambda_b
        
        #Assume EV battery capacity of 40KW
        Cn = 40*Cn
        
        S_b = calculate_base_sensitivity(lambda_max, lambda_b, Cn)
        
        alpha = calculate_alpha(lambda_sell*cs_sell_price, lambda_b, lambda_max)
        
        B_n_t = calculate_behavioural_response(alpha, type_="high")
        
        initial_soc = 0.1*np.ones((n,1))
        final_soc = 0.9*np.ones((n,1))
        
        S_n_t = np.divide(S_b,(final_soc-initial_soc)*B_n_t)
        
        E_n_t = calculate_energy_n(lambda_max, lambda_sell, S_n_t)
        
        profit = profit_of_kth_station_at_time_t(lambda_sell, lambda_purchase, E_n_t)