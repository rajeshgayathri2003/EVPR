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
import os

def average_cost_per_charging_session(energy, nash):
    price = energy*nash
    average_cost = np.sum(price)/len(price)
    return average_cost
    
    

def assign_vehicle_details(Cn, cs_sell_price, lambda_sell, initial_soc, final_soc, station, n, vehicles):
    
    n1 = vehicles[station]
    
    with open('EVdata.csv', 'r') as file:
        csv_file = list(csv.reader(file))
        
        if station == 0:
            csv_file = csv_file[0:n1]
            
        elif station == 1:
            csv_file = csv_file[vehicles[station-1]+1:vehicles[station-1]+1+n1]
            
        elif station == 2:
            csv_file = csv_file[n-n1+1:n+1]
        
        for i, lines in enumerate(csv_file):
                
            Cn[i,:] = lines[1]
                
            initial_soc[i,:] = lines[2]
                        
            final_soc[i,:] = lines[3]
            
def write_to_csv(file_path, data):
    curr = os.getcwd()
    file_path = os.path.join(curr, file_path)
            
    if os.path.exists(file_path):
        with open(file_path, 'a') as f:
            writer_object = csv.writer(f)
            writer_object.writerow(data)
            
            f.close()
            
    else:
        with open(file_path, 'w') as f:
            writer_object = csv.writer(f)
            writer_object.writerow(data)
            
            f.close()

            

def find_nash_equilibrium(grid_price, 
                          cs_sell_price, 
                          n, 
                          stations, 
                          vehicles,
                          delta_lambda = [2,2,2]):
    
    
    k = 1
    for station in range(stations):
        n1 = vehicles[station]
        delta_lambda_val = delta_lambda[station]
        
        lambda_max = np.random.randint(16, 20, size=(n1, k))  # Max price users will accept
        lambda_b = np.random.randint(8, 12, size=(n1, k))    # Price where users become sensitive
        
        print(lambda_max)
        print(lambda_b)
        
        #lambda_sell is the selling price offered by the charging station
        lambda_sell = np.ones((n1,k))
            
        #lambda_purchase is the purchase price at which the charging station purchases electricity from the grid
        lambda_purchase = np.ones((n1,k))*grid_price
        initial_soc = np.ones((n1,k))
        final_soc = np.ones((n1,k))
        Cn = np.ones((n1,k))
        E_n_t = np.ones((n1,k))
        sell_price_array = cs_sell_price*np.ones((k, 1))
        
        prev_profit = 0
        cs_sell_price = grid_price
        cs_sell_price_variation = [cs_sell_price*np.ones((n1,k))]
        demand_variation = []
        omega_variation = []
        profit_variation = []
        sensitivity_variation = [] 
        
        assign_vehicle_details(Cn, cs_sell_price, lambda_sell, initial_soc, final_soc, station, n, vehicles)
        
        print("The present station is {}".format(station))
        
        while True:
            
            cs_sell_price+=delta_lambda_val
            
            lambda_sell[:,:] = cs_sell_price
            
            print("The present selling price is {}".format(cs_sell_price))    
            
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
            
            if profit<prev_profit:
                print("Nash Equilibrium price for station {} is {}".format(station, cs_sell_price-delta_lambda_val))
                nash = cs_sell_price-delta_lambda_val
                print(E_n_t_append)
                cost = average_cost_per_charging_session(E_n_t_append, nash)
                data = [grid_price, nash]
                write_to_csv("twenty_four.csv", data)
                data_2 = [cost]
                write_to_csv("average_price_twenty_four.csv", data_2)
                break
            
            prev_profit = profit
            
        
        cs_sell_price_variation = np.array(cs_sell_price_variation)
        demand_variation = np.array(demand_variation)
        profit_variation = np.array(profit_variation)
        print(profit_variation)
        omega_variation = np.array(omega_variation)
        sensitivity_variation = np.array(sensitivity_variation)
        
            
        #combined_plot_price(profit_variation, omega_variation, cs_sell_price_variation, demand_variation, nash)
            
            
def combined_plot_price(profit_variation, omega_variation, cs_sell_price_variation, demand_variation, nash):
    fig, ax1 = plt.subplots()

    # Extract relevant data
    omega_plot = omega_variation[:,0,0]
    price_plot = cs_sell_price_variation[1:,0, 0]
    demand_plot = demand_variation[:,0,0]

    # Primary y-axis (Profit & Utility)
    ax1.plot(price_plot, profit_variation, label="Profit to the Charging Station", color='b')
    #ax1.plot(price_plot, omega_plot, label="Utility of EV", color='r', linestyle='--')
    ax1.axvline(x=nash, color='m', linestyle='dotted', linewidth=2, label='Nash Equilibrium')
    
    ax1.set_xlabel("Selling Price of Electricity to EVs")
    ax1.set_ylabel("")
    ax1.text(-0.1, 0.45, "Profit (₹)", color="blue", fontsize=14, transform=ax1.transAxes, 
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
    parser.add_argument("--vehicles", type=int, default=100, help="Enter the total number of vehicles we are taking into account for the given system")
    parser.add_argument("--stations", type=int, default=3, help="Enter the total number of charging stations in the network")
        
    args = parser.parse_args()
    n = args.vehicles
    k = args.stations
        
    current_hours = [i for i in range (24)]
        
    #Note: all the grid_prices are given in paise
    
    for current_hour in (current_hours):
     
        # price at the present hour
        if (6<=current_hour and current_hour<9) or (18<=current_hour and current_hour<22):
            grid_price = cs_sell_price = 9
        
        elif (9<=current_hour and current_hour<16):
            grid_price = cs_sell_price = 6
            
        else:
            grid_price = cs_sell_price = 7.5
            
        print("The present grid purchase price is", grid_price)
            
        #Change in price is denoted by delta_lambda
        #Let us assume that initially we sell at the same price as the grid
        delta_lambda = [2, 2, 2]
                
        # cs_sell_price_variation = [cs_sell_price*np.ones((n,k))]
        demand_variation = []
        omega_variation = []
        profit_variation = []
        sensitivity_variation = []
        profit_prev = np.zeros((n,k))
            
        demand_final = np.zeros((n,k))
        count = 0
        state = 0
            
        #lambda_max is the maximum price at which the user exits the charging station
        
        
        vehicles = [20, 30, 50]
        
        find_nash_equilibrium(grid_price, cs_sell_price, n, k, vehicles, delta_lambda)
    
    
    
    
    
    