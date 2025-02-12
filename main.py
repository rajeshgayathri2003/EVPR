#This code is based on the algorithm proposed by Abbasi et al in "A Coupled Game Theory and Lyapunov Optimization Approach to Electric Vehicle Charging at Fast Charging Stations"
# to achieve the Nash Equilibrium 

from helper_funs1 import energy_requirement_of_customers, profit_of_kth_station_at_time_t, calculate_energy_n, calculate_base_sensitivity, calculate_alpha, calculate_behavioural_response, calculate_utility
import numpy as np
from datetime import datetime
import argparse
from plots import plot_gridpurchase_sell_n, plot_gridpurchase_sell_single, plot_price_demand, plot_nash_equilibrium, plot_nash_equilibrium_2, combined_plot_price
import copy
import matplotlib.pyplot as plt


if __name__ == "__main__":
    
    #Add the number of vehicles and the number of charging stations
    parser = argparse.ArgumentParser(description="Add the number of vehicels and the number of charging stations")
    parser.add_argument("--vehicles", type=int, default=5, help="Enter the total number of vehicles we are taking into account for the given system")
    parser.add_argument("--stations", type=int, default=2, help="Enter the total number of charging stations in the network")
    
    args = parser.parse_args()
    n = args.vehicles
    k = args.stations
    
    current_hour = datetime.now().hour
    print("The current hour is", current_hour)
    
    #Note: all the grid_prices are given in paise
    
    if (6<=current_hour and current_hour<9) or (18<=current_hour and current_hour<22):
        grid_price = cs_sell_price = 9
    
    elif (9<=current_hour and current_hour<16):
        grid_price = cs_sell_price = 6
        
    else:
        grid_price = cs_sell_price = 7.5
        
    #Change in price is denoted by delta_lambda
    #Let us assume that initially we sell at the same price as the grid
    delta_lambda = 0.10
    
    #lambda_max is the maximum price at which the user exits the charging station
    lambda_max = np.ones((n,1))
    
    #lambda_b is the minimum price at which the user starts becoming sensitive to the price
    lambda_b =  np.ones((n,1))
    
    #lambda_sell is the selling price offered by the charging station
    lambda_sell = np.ones((n,1))
    
    #lambda_purchase is the purchase price at whihc the charging station purchases electricity from the grid
    lambda_purchase = np.ones((n,1))*grid_price
    initial_soc = np.ones((n,1))
    final_soc = np.ones((n,1))
    Cn = np.ones((n,1))
    E_n_t = np.ones((n,1))
    
    cs_sell_price_variation = [cs_sell_price*np.ones((n,1))]
    demand_variation = []
    omega_variation = []
    profit_variation = []
    profit_prev = 0 
    
    demand_final = np.zeros((n,1))
    count = 0
    state = 0
    
    while True:
        
        #increase the price by 10 paise
        cs_sell_price+=delta_lambda
        
        
        print("###########################")
        print("The current charging station price proposed is", cs_sell_price)
    
        for i in range(n):
            lambda_sell[i,:] = cs_sell_price
            
            lambda_max[i,:] = 20
            
            #Assuming optimal user behaviour we set En,t = En,t*
            lambda_b[i,:] = 9
            
            #Assume EV battery capacity of 40KW
            Cn[i,:] = 40
            
            initial_soc[i,:]=0.1
            
            final_soc[i,:]=0.9
            
        count+=1
        lambda_sell_append = copy.deepcopy(lambda_sell)
        cs_sell_price_variation.append(lambda_sell_append)
            
        S_b = calculate_base_sensitivity(lambda_max, lambda_b, Cn)
               
        alpha = calculate_alpha(lambda_sell, lambda_b, lambda_max)
        
        B_n_t = calculate_behavioural_response(alpha, type_="medium")
        
        S_n_t = np.divide(S_b,(final_soc-initial_soc)*B_n_t)
                
        E_n_t[B_n_t != 1] = calculate_energy_n(lambda_max[B_n_t != 1], lambda_sell[B_n_t != 1], S_n_t[B_n_t != 1])
        E_n_t[B_n_t == 1] = energy_requirement_of_customers(final_soc[B_n_t == 1], initial_soc[B_n_t == 1], Cn[B_n_t == 1])
        
        print("The energy demand for the vehicles is", E_n_t)
        
        omega = calculate_utility(S_n_t, E_n_t, lambda_max, lambda_sell)
        omega_append = copy.deepcopy(omega)
        omega_variation.append(omega_append)
        
        E_n_t_append = copy.deepcopy(E_n_t)
        demand_variation.append(E_n_t_append)
        
        profit = profit_of_kth_station_at_time_t(lambda_sell, lambda_purchase, E_n_t)
        profit_append = copy.deepcopy(profit)
        profit_variation.append(profit_append)
       
        print("The profit is", profit)
        
        
        if profit < profit_prev:
            demand_final = E_n_t
            cs_sell_price-=delta_lambda
            break
            state+=1
        
        profit_prev = profit
        
    
    cs_sell_price_variation = np.array(cs_sell_price_variation)
    demand_variation = np.array(demand_variation)
    profit_variation = np.array(profit_variation)
    omega_variation = np.array(omega_variation)
    
    print(np.shape(profit_variation))
    print(np.shape(omega_variation))
    #print(cs_sell_price_variation, lambda_purchase)
    cs_purchase_price_variation = np.repeat(lambda_purchase[np.newaxis,:,:], count+1, axis=0)
    print(np.shape(cs_purchase_price_variation))
    
    print(cs_sell_price)
    print(count)
    
    #plot_gridpurchase_sell_n(cs_sell_price_variation, cs_purchase_price_variation, n, count)
    plot_gridpurchase_sell_single(cs_sell_price_variation, cs_purchase_price_variation, count)
    plot_price_demand(cs_sell_price_variation, demand_variation)
    plot_nash_equilibrium(profit_variation, omega_variation, demand_variation)
    plot_nash_equilibrium_2(profit_variation, omega_variation, cs_sell_price_variation)
    combined_plot_price(profit_variation, omega_variation, cs_sell_price_variation, demand_variation)
    plt.show()
    
        
        