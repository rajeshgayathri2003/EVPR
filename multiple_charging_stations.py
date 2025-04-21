#This code is based on the algorithm proposed by Abbasi et al in "A Coupled Game Theory and Lyapunov Optimization Approach to Electric Vehicle Charging at Fast Charging Stations"
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

def assign_vehicle_details(Cn, cs_sell_price, lambda_sell, initial_soc, final_soc, station):
    
    with open('EVdata.csv', 'r') as file:
        csv_file = list(csv.reader(file))
        
        if station == 0:
            csv_file = csv_file[0:20]
            
        elif station == 1:
            csv_file = csv_file[20:40]
            
        elif station == 2:
            csv_file = csv_file[40:]
        
        for i, lines in enumerate(csv_file):
    
                
            Cn[i,station] = lines[1]
                
            initial_soc[i,station] = lines[2]
                        
            final_soc[i,station] = lines[3]
            

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
                          delta_lambda = 2):
    
    
    for station in range(stations):
        prev_profit = 0
        cs_sell_price = grid_price
        cs_sell_price_variation = [cs_sell_price*np.ones((n,k))]
        demand_variation = []
        omega_variation = []
        profit_variation = []
        sensitivity_variation = [] 
        
        assign_vehicle_details(Cn, cs_sell_price, lambda_sell, initial_soc, final_soc, station)
        
        print("The present station is {}".format(station))
        
        while True:
            cs_sell_price+=delta_lambda
            
            lambda_sell[:,station] = cs_sell_price
            
            print("The present selling price is {}".format(cs_sell_price))    
            
            lambda_sell_append = copy.deepcopy(lambda_sell)
            
            cs_sell_price_variation.append(lambda_sell_append)
                
            S_b = calculate_base_sensitivity(lambda_max[:, station:station+1], lambda_b[:, station:station+1], Cn[:, station:station+1])
            # print(np.shape(S_b))
                
            alpha = calculate_alpha(lambda_sell[:, station:station+1], lambda_b[:, station:station+1], lambda_max[:, station:station+1])
            # print(np.shape(alpha))
            
            B_n_t = calculate_behavioural_response(alpha, type_="medium")
            # print(np.shape(B_n_t))
            
            B_n_t_dash  = B_n_t
            
            # print("shapes")
            # print(np.shape(S_b), np.shape(final_soc[:, station:station+1]), np.shape(B_n_t))
            
            S_n_t = np.divide(S_b,(final_soc[:, station:station+1]-initial_soc[:, station:station+1])*B_n_t)
            #print(np.shape(S_n_t))
            
            E_n_t[:, station:station+1][B_n_t_dash == 0] = 0
            E_n_t[:, station:station+1][B_n_t_dash != 1] = calculate_energy_n(lambda_max[:, station:station+1][B_n_t_dash != 1], lambda_sell[:, station:station+1][B_n_t_dash != 1], S_n_t[B_n_t_dash != 1])
            E_n_t[:, station:station+1][B_n_t_dash == 1] = energy_requirement_of_customers(final_soc[:, station:station+1][B_n_t_dash == 1], initial_soc[:, station:station+1][B_n_t_dash == 1], Cn[:, station:station+1][B_n_t_dash == 1])
            
            #print("The energy demand for the vehicles is", E_n_t[:, station:station+1])
            
            omega = calculate_utility(S_n_t, E_n_t[:, station:station+1], lambda_max[:, station:station+1], lambda_sell[:, station:station+1])
            # print(np.shape(omega))
            omega_append = copy.deepcopy(omega)
            omega_variation.append(omega_append)
            
            E_n_t_append = copy.deepcopy(E_n_t[:, station:station+1])
            demand_variation.append(E_n_t_append)
            
            sensitivity_variation.append(copy.deepcopy(S_n_t[:, station:station+1]))
            
            
            profit = profit_of_kth_station_at_time_t(lambda_sell[:, station:station+1], lambda_purchase[:, station:station+1], E_n_t[:, station:station+1])
            profit_append = copy.deepcopy(profit)
            profit_variation.append(profit_append)
        
            print("The profit is", profit/100)
            
            #print("the profits are", profit)
            
            if profit<prev_profit:
                print("Nash Equilibrium price for station {} is {}".format(station, cs_sell_price-delta_lambda))
                nash = cs_sell_price-delta_lambda
                print(E_n_t_append)
                break
                
            prev_profit = profit
            
        cs_sell_price_variation = np.array(cs_sell_price_variation)
        demand_variation = np.array(demand_variation)
        profit_variation = np.array(profit_variation)
        print(profit_variation)
        omega_variation = np.array(omega_variation)
        sensitivity_variation = np.array(sensitivity_variation)
        
            
        combined_plot_price(profit_variation, omega_variation, cs_sell_price_variation, demand_variation, nash, station)
            
            
def combined_plot_price(profit_variation, omega_variation, cs_sell_price_variation, demand_variation, nash, station_id):
    fig, ax1 = plt.subplots()

    # Extract relevant data
    omega_plot = omega_variation[:,0,0]
    price_plot = cs_sell_price_variation[1:,0, station_id]
    demand_plot = demand_variation[:,0,0]

    # Primary y-axis (Profit & Utility)
    ax1.plot(price_plot, profit_variation, label="Profit to the Charging Station", color='b')
    #ax1.plot(price_plot, omega_plot, label="Utility of EV", color='r', linestyle='--')
    ax1.axvline(x=nash, color='m', linestyle='dotted', linewidth=2, label='Nash Equilibrium')
    
    ax1.set_xlabel("Selling Price of Electricity to EVs")
    ax1.set_ylabel("")
    ax1.text(-0.1, 0.45, "Profit ($\cent$)", color="blue", fontsize=14, transform=ax1.transAxes, 
         va='center', ha='center', rotation=90)
    # ax1.text(-0.13, 0.45, "Utility ($\cent$)", color="red", fontsize=12, transform=ax1.transAxes, 
        #  va='center', ha='center', rotation=90)


    ax1.tick_params(axis='y')
    
    # Secondary y-axis (Demand)
    ax2 = ax1.twinx()
    ax2.plot(price_plot, demand_plot, label="Demand of EV", linestyle='-.', color='g')
    
    ax2.set_ylabel("Demand (kWh)", color='g', fontsize=14)
    ax2.tick_params(axis='y', labelcolor='g')

    # Title, legend, and grid
    fig.suptitle("Nash Equilibrium", fontsize=18)
    ax1.grid()
    
    # Combine legends
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="best", fontsize=12)
    
    plt.show()
            
        
if __name__ == "__main__":
    
    #Add the number of vehicles and the number of charging stations
    parser = argparse.ArgumentParser(description="Add the number of vehicels and the number of charging stations")
    parser.add_argument("--vehicles", type=int, default=20, help="Enter the total number of vehicles we are taking into account for the given system")
    parser.add_argument("--stations", type=int, default=3, help="Enter the total number of charging stations in the network")
        
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
    profit_prev = np.zeros((n,k))
        
    demand_final = np.zeros((n,k))
    count = 0
    state = 0
        
    #lambda_max is the maximum price at which the user exits the charging station
    lambda_max = np.random.randint(25, 30, size = (n,k))
    
    #lambda_b is the minimum price at which the user starts becoming sensitive to the price
    lambda_b = np.random.randint(10, 15, size= (n,k))
    print(lambda_max)
    print(lambda_b)
    
    find_nash_equilibrium(grid_price, cs_sell_price, lambda_sell, lambda_purchase, n, k, Cn, initial_soc, final_soc, E_n_t, 
                            delta_lambda = 2)
    
    
    
    
    
    