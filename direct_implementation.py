#This code is based on the algorithm proposed by Abbasi et al in "A Coupled Game Theory and Lyapunov Optimization Approach to Electric Vehicle Charging at Fast Charging Stations"
# to achieve the Nash Equilibrium 

from helper_funs1 import energy_requirement_of_customers, profit_of_kth_station_at_time_t, calculate_energy_n, calculate_base_sensitivity, calculate_alpha, calculate_behavioural_response, calculate_utility
import numpy as np
from datetime import datetime
import argparse
from plots import plot_gridpurchase_sell_n, plot_gridpurchase_sell_single, plot_price_demand, plot_nash_equilibrium, plot_nash_equilibrium_2, combined_plot_price, plot_price_demand_n, combined_plot_price_n, plot_price_omega_n, plot_nash_equilibrium_n, plot_omega_energy, plot_energy_sensitivity
import copy
import matplotlib.pyplot as plt
import random
from csv_plots import write_to_csv


if __name__ == "__main__":
    
    #Add the number of vehicles and the number of charging stations
    parser = argparse.ArgumentParser(description="Add the number of vehicels and the number of charging stations")
    parser.add_argument("--vehicles", type=int, default=6, help="Enter the total number of vehicles we are taking into account for the given system")
    parser.add_argument("--stations", type=int, default=2, help="Enter the total number of charging stations in the network")
        
    args = parser.parse_args()
    n = args.vehicles
    k = args.stations
        
    
    current_hour = datetime.now().hour
    print("The current hour is", current_hour)
        
    #Note: all the grid_prices are given in paise
     
    # price at the present hour
    grid_price = cs_sell_price = random.randint(10, 18)
    print("The present grid purchase price is", grid_price)
            
    #Change in price is denoted by delta_lambda
    #Let us assume that initially we sell at the same price as the grid
    delta_lambda = 2
        
    #lambda_max is the maximum price at which the user exits the charging station
    lambda_max = np.ones((n,k))
        
    #lambda_b is the minimum price at which the user starts becoming sensitive to the price
    lambda_b =  np.ones((n,k))
        
    #lambda_sell is the selling price offered by the charging station
    lambda_sell = np.ones((n,k))
        
    #lambda_purchase is the purchase price at whihc the charging station purchases electricity from the grid
    lambda_purchase = np.ones((n,k))*grid_price
    initial_soc = np.ones((n,k))
    final_soc = np.ones((n,k))
    Cn = np.ones((n,k))
    E_n_t = np.ones((n,k))
    sell_price_array = cs_sell_price*np.ones((k, 1))
        
    cs_sell_price_variation = [cs_sell_price*np.ones((n,k))]
    demand_variation = []
    omega_variation = []
    profit_variation = []
    sensitivity_variation = []
    # profit_prev = np.zeros((n,k))
    profit_prev = 0
    
    demand_final = np.zeros((n,k))
    count = 0
    state = 0
        
    lambda_max = np.random.randint(25, 30, size = (n,k))
    lambda_b = np.random.randint(10, 15, size= (n,k))
    print(lambda_max)
    print(lambda_b)
    
    completed_values = []
        
    while True:
            
            #increase the price by 10 paise
            cs_sell_price+=delta_lambda
            
            
            print("###########################")
            print("The current charging station price proposed is", cs_sell_price)
        
            for j in range(k):
                for i in range(n):
                    
                    lambda_sell[i,j] = cs_sell_price
                    
                    #lambda_max[i,:] = 2000
                    
                    #Assuming optimal user behaviour we set En,t = En,t*
                    #lambda_b[i,:] = 900
                    
                    #Assume EV battery capacity of 40KW
                    #This has to be replaced by a CSV file
                    if j==0:
                        Cn[i,j] = 40
                    else:
                        Cn[i,j] = 60
                    
                    initial_soc[i,j]=0.1
                    
                    final_soc[i,j]=0.9
                
            count+=1
            lambda_sell_append = copy.deepcopy(lambda_sell)
            cs_sell_price_variation.append(lambda_sell_append)
                
            S_b = calculate_base_sensitivity(lambda_max, lambda_b, Cn)
            print(np.shape(S_b))    
            
            alpha = calculate_alpha(lambda_sell, lambda_b, lambda_max)
            print(np.shape(alpha))
            
            B_n_t = calculate_behavioural_response(alpha, type_="medium")
            #print(B_n_t)
            
            S_n_t = np.divide(S_b,(final_soc-initial_soc)*B_n_t)
                    
            E_n_t[B_n_t == 0] = 0
            E_n_t[B_n_t != 1] = calculate_energy_n(lambda_max[B_n_t != 1], lambda_sell[B_n_t != 1], S_n_t[B_n_t != 1])
            E_n_t[B_n_t == 1] = energy_requirement_of_customers(final_soc[B_n_t == 1], initial_soc[B_n_t == 1], Cn[B_n_t == 1])
            
            print("The energy demand for the vehicles is", E_n_t)
            
            omega = calculate_utility(S_n_t, E_n_t, lambda_max, lambda_sell)
            omega_append = copy.deepcopy(omega)
            omega_variation.append(omega_append)
            
            E_n_t_append = copy.deepcopy(E_n_t)
            demand_variation.append(E_n_t_append)
            
            sensitivity_variation.append(copy.deepcopy(S_n_t))
            
            profit = profit_of_kth_station_at_time_t(lambda_sell, lambda_purchase, E_n_t)
            profit_append = copy.deepcopy(profit)
            profit_variation.append(profit_append)
        
            print("The profit is", profit/100)
            
            print("the profits are", profit)
            
            if profit < profit_prev:
                demand_final =  E_n_t
                cs_sell_price-=delta_lambda
                
                break
            
            profit_prev = profit
            
            # indices = np.where(profit < profit_prev)[0]
            
            # indices_lst = [x for x in indices if x not in completed_values]
            
            # print(indices)
            
            # if len(indices_lst) > 0:
            #     for index in indices_lst:
            #         demand_final[:, index] = E_n_t[:, index]
                
            #     price = cs_sell_price - delta_lambda
            #     print(np.shape(sell_price_array))
            #     sell_price_array[indices] = price
                
                
            # completed_values.extend(list(indices))
            # print(completed_values, "VALUES")
            
            # print(demand_final)
            
            # if np.all(demand_final != 0):
            #     break
            # profit_prev = profit
            
    print(cs_sell_price)
            
            
    cs_sell_price_variation = np.array(cs_sell_price_variation)
    demand_variation = np.array(demand_variation)
    profit_variation = np.array(profit_variation)
    omega_variation = np.array(omega_variation)
    sensitivity_variation = np.array(sensitivity_variation)
    
    print(np.shape(profit_variation))
    print(np.shape(omega_variation))
    #print(cs_sell_price_variation, lambda_purchase)
    cs_purchase_price_variation = np.repeat(lambda_purchase[np.newaxis,:,:], count+1, axis=0)
    print(np.shape(cs_purchase_price_variation))
        
        
    print(sell_price_array, "NASH")
    print(cs_sell_price/100)
    nash = cs_sell_price
    print(lambda_sell)
    print(count)
        
    data = [np.sum(demand_final*cs_sell_price)/n]
    write_to_csv("average_amount_1.csv", data)
        
    data = [cs_sell_price, grid_price]
    write_to_csv("sell_purchase_1.csv", data)
    plot_omega_energy(omega_variation, demand_variation)
    plot_energy_sensitivity(demand_variation, sensitivity_variation)
    # plot_gridpurchase_sell_n(cs_sell_price_variation, cs_purchase_price_variation, n, count)
    # plot_nash_equilibrium_2(profit_variation, omega_variation, cs_sell_price_variation, nash)
    # combined_plot_price(profit_variation, omega_variation, cs_sell_price_variation, demand_variation, nash)
    # plot_gridpurchase_sell_single(cs_sell_price_variation, cs_purchase_price_variation, count)
    # plot_price_demand_n(cs_sell_price_variation, demand_variation, n)
    # combined_plot_price_n(profit_variation, omega_variation, cs_sell_price_variation, demand_variation, n)
    # plot_price_omega_n(cs_sell_price_variation, omega_variation, n)
    # plot_nash_equilibrium_n(profit_variation, omega_variation, demand_variation, n)
    
    
    plt.show()
    
    
    #plot_price_demand(cs_sell_price_variation, demand_variation)
    #plot_nash_equilibrium(profit_variation, omega_variation, demand_variation)
    #plot_nash_equilibrium_2(profit_variation, omega_variation, cs_sell_price_variation)
    #combined_plot_price(profit_variation, omega_variation, cs_sell_price_variation, demand_variation)
    
        
        