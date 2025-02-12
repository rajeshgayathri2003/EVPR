import matplotlib.pyplot as plt
import numpy as np


def plot_gridpurchase_sell_n(cs_sell_price_variation, cs_purchase_price_variation, n, count, k =0):
    """This function plots the graph of variation in price with time across different iterations for all n vehicles

    Args:
        cs_sell_price_variation (_type_): _description_
        cs_purchase_price_variation (_type_): _description_
        n (_type_): _description_
        count (_type_): _description_
        k (int, optional): _description_. Defaults to 0.
    """
    plt.figure(1)
    fig, axes = plt.subplots(n, 1, figsize=(8, 2 * n), sharex=True)
    fig.suptitle('Variation of Selling Price to EVs and Purchase from the grid for CS', fontsize=16)
    time_steps = np.arange(count+1)
    
    selling_price = cs_sell_price_variation[: ,: ,k]
    purchase_price = cs_purchase_price_variation[:,:,k]
    
    for vehicle in range(n):
        axes[vehicle].plot(time_steps, selling_price[:, vehicle], label=f"Selling Price - Vehicle {vehicle + 1}")
        axes[vehicle].plot(time_steps, purchase_price[:, vehicle], linestyle='--', label=f"Purchase Price - Vehicle {vehicle + 1}")
        axes[vehicle].set_title(f"Vehicle {vehicle + 1}")
        axes[vehicle].set_ylabel("Price")
        axes[vehicle].legend()
        axes[vehicle].grid(True)
        
    axes[-1].set_xlabel("Time Steps")
    plt.tight_layout()
    #plt.show()
    
    
def plot_gridpurchase_sell_single(cs_sell_price_variation, cs_purchase_price_variation, count):
    """This graph plots the variation of price with each iteration for a single electric vehicle
    """
    plt.figure(2)
    time_steps = np.arange(count+1)
    # print(time_steps)
    # print(cs_sell_price_variation)
    sell_price_plot = cs_sell_price_variation[:,0,0]
    purchase_price_plot = cs_purchase_price_variation[:,0,0]
    plt.plot(time_steps, sell_price_plot, label = "selling price", color = 'b')
    plt.plot(time_steps, purchase_price_plot, label = "purchase price", color = 'r', linestyle = '--')
    
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Variation of Selling Price to EVs and Purchase from the grid for CS', fontsize=10)
    
    plt.legend()
    plt.grid()
    #plt.show()
    
def plot_price_demand(cs_sell_price_variation, demand_variation):
    """This graph plots the variation of electric vehicle charging demand with the selling price offered by the charging station
    
    """
    plt.figure(3)
    sell_price_plot = cs_sell_price_variation[1:,0,0]
    demand_plot = demand_variation[:,0,0]
    
    plt.plot(sell_price_plot, demand_plot, color = 'r')
    
    plt.xlabel('EV charging price offered by the CS')
    plt.ylabel('Demand of EV')
    plt.title('Variation of demand with the Electic Vehicle charging price', fontsize = 10)
    plt.grid()
    
    plt.legend()
    #plt.show()
    
def plot_nash_equilibrium(profit_variation, omega_variation, demand_variation):
    """This function plots the profits versus the utility function to identify the nash equilibrium
    """
    plt.figure(4)
    #time_steps = np.arange(count)
    
    omega_plot = omega_variation[:,0,0]
    demand_plot = (demand_variation[:,0,0])
    #print("shape is", (demand_plot))
    demand_plot = np.flip(demand_variation[:,0,0])
    #print("shape is", (demand_plot))
    #print("shape is", np.shape(profit_variation))
    print(profit_variation)
    
    plt.gca().invert_xaxis()
    
    plt.plot(demand_plot, np.flip(profit_variation), label = "Profit to the charging station", color = 'b')
    plt.plot(demand_plot, np.flip(omega_plot), label = "Utility of EV", color = 'r', linestyle = '--')
    
    plt.xlabel('Demand in kWh')
    plt.ylabel('Profit')
    plt.title('Nash Equilibrium', fontsize=10)
    plt.grid()
    plt.legend()
    
def plot_nash_equilibrium_2(profit_variation, omega_variation, cs_sell_price_variation):
    """This function plots the profits versus the utility function to identify the nash equilibrium
    """
    plt.figure(5)
    #time_steps = np.arange(count)
    
    omega_plot = omega_variation[:,0,0]
    price_plot = cs_sell_price_variation[1:,0,0]
    
    plt.plot(price_plot, profit_variation, label = "Profit to the charging station", color = 'b')
    plt.plot(price_plot, omega_plot, label = "Utility of EV", color = 'r', linestyle = '--')
    
    plt.xlabel('Selling Price of Electricity to EVs')
    plt.ylabel('Profit')
    plt.title('Nash Equilibrium', fontsize=10)
    plt.grid()
    plt.legend()
    
    

def combined_plot_price(profit_variation, omega_variation, cs_sell_price_variation, demand_variation):
    fig, ax1 = plt.subplots()

    # Extract relevant data
    omega_plot = omega_variation[:,0,0]
    price_plot = cs_sell_price_variation[1:,0,0]
    demand_plot = demand_variation[:,0,0]

    # Primary y-axis (Profit & Utility)
    ax1.plot(price_plot, profit_variation, label="Profit to the Charging Station", color='b')
    ax1.plot(price_plot, omega_plot, label="Utility of EV", color='r', linestyle='--')
    
    ax1.set_xlabel("Selling Price of Electricity to EVs")
    ax1.set_ylabel("Profit / Utility", color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    
    # Secondary y-axis (Demand)
    ax2 = ax1.twinx()
    ax2.plot(price_plot, demand_plot, label="Demand of Charging Station", linestyle='-.', color='g')
    
    ax2.set_ylabel("Demand", color='g')
    ax2.tick_params(axis='y', labelcolor='g')

    # Title, legend, and grid
    fig.suptitle("Nash Equilibrium", fontsize=10)
    ax1.grid()
    
    # Combine legends
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="best")
    
def combined_plot_price_n(profit_variation, omega_variation, cs_sell_price_variation, demand_variation, n):
    fig, axes = plt.subplots(3, 2, figsize=(10, 8))  # Adjusted figure size for clarity

    # Extract relevant data
    omega_plot = omega_variation[:, :, 0]
    price_plot = cs_sell_price_variation[1:, 0, 0]
    demand_plot = demand_variation[:, :, 0]

    axes = axes.flatten()  # Flatten the 2D array for easier iteration

    for i in range(len(axes)):
        if i >= n:  # Skip unused plots if n < total subplots
            axes[i].axis("off")
            continue

        # Plot profit and utility on the primary y-axis
        axes[i].plot(price_plot, profit_variation, label="Profit to the Charging Station", color='b')
        axes[i].plot(price_plot, omega_plot[:, i], label="Utility of EV", color='r', linestyle='--')
        axes[i].set_xlabel("Selling Price of Electricity to EVs")
        axes[i].set_ylabel("Profit / Utility", color='b')
        axes[i].tick_params(axis='y', labelcolor='b')
        axes[i].grid(True)

        # Create a secondary y-axis for demand
        ax2 = axes[i].twinx()
        ax2.plot(price_plot, demand_plot[:, i], label="Demand of Charging Station", linestyle='-.', color='g')
        ax2.set_ylabel("Demand", color='g')
        ax2.tick_params(axis='y', labelcolor='g')

        # Combine legends from both axes
        lines_1, labels_1 = axes[i].get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        axes[i].legend(lines_1 + lines_2, labels_1 + labels_2, loc="best")

    # Title for the entire figure
    fig.suptitle("Nash Equilibrium", fontsize=10)
    plt.tight_layout()  # Adjust layout to avoid overlapping

def plot_price_demand_n(cs_sell_price_variation, demand_variation, n):
    """This graph plots the variation of electric vehicle charging demand with the selling price offered by the charging station
    
    """
    fig, axes = plt.subplots(3, 2, figsize=(6, 2 * n))
    fig.suptitle('Variation of Demand of Different Vehicles with selling Price', fontsize=16)
    sell_price_plot = cs_sell_price_variation[1:,0,0]
    demand_plot = demand_variation[:,:,0]
    count = 0
    for demand in range(n//2):
        for k in range(n//3):
            axes[demand, k].plot(sell_price_plot, demand_plot[:, count], label=f"Demand - Selling Price")
            axes[demand, k].set_title("Demand of EV {}".format(count+1))
            axes[demand, k].set_ylabel("Demand in kWh")
            axes[demand, k].set_xlabel("Price of EV")
            axes[demand, k].legend()
            axes[demand, k].grid(True)
            count+=1
    
    
    #plt.plot(sell_price_plot, demand_plot, color = 'r')
    
    # plt.xlabel('EV charging price offered by the CS')
    # plt.ylabel('Demand of EV')
    # plt.title('Variation of demand with the Electic Vehicle charging price', fontsize = 10)
    # plt.grid()
    plt.tight_layout()
    
    plt.legend()
    
def plot_price_omega_n(cs_sell_price_variation, omega_variation, n):
    """This graph plots the variation of electric vehicle charging demand with the selling price offered by the charging station
    
    """
    fig, axes = plt.subplots(3, 2, figsize=(6, 2 * n))
    fig.suptitle('Variation of Demand of Different Vehicles with selling Price', fontsize=16)
    sell_price_plot = cs_sell_price_variation[1:,0,0]
    omega_plot = omega_variation[:,:,0]
    count = 0
    for demand in range(n//2):
        for k in range(n//3):
            axes[demand, k].plot(sell_price_plot, omega_plot[:, count], label=f"Omega - Selling Price")
            axes[demand, k].set_title("Utility of EV {}".format(count+1))
            axes[demand, k].set_ylabel("Utility of the EV")
            axes[demand, k].set_xlabel("Price of EV")
            axes[demand, k].legend()
            axes[demand, k].grid(True)
            count+=1
    
    
    #plt.plot(sell_price_plot, demand_plot, color = 'r')
    
    # plt.xlabel('EV charging price offered by the CS')
    # plt.ylabel('Demand of EV')
    # plt.title('Variation of demand with the Electic Vehicle charging price', fontsize = 10)
    # plt.grid()
    plt.tight_layout()
    
    plt.legend()

def plot_nash_equilibrium_n(profit_variation, omega_variation, demand_variation, n):
    """This function plots the profits versus the utility function to identify the nash equilibrium
    """
    omega_plot = omega_variation[:,:,0]
    demand_plot = (demand_variation[:,:,0])
    
    
    fig, axes = plt.subplots(3, 2, figsize=(6, 2 * n))
    fig.suptitle('Variation of Demand of Different Vehicles with selling Price', fontsize=16)
    # sell_price_plot = cs_sell_price_variation[1:,0,0]
    omega_plot = omega_variation[:,:,0]
    count = 0
    for demand in range(n//2):
        for k in range(n//3):
            demand_plot = np.flip(demand_variation[:, count,0])
            
            axes[demand, k].plot(demand_plot, np.flip(profit_variation), label = "Profit to the charging station", color = 'b')
            axes[demand, k].plot(demand_plot, np.flip(omega_plot[:, count]), label = "Utility of EV", color = 'r', linestyle = '--')
            axes[demand, k].set_title("Utility of EV {} and Profit to Charging Station".format(count+1))
            axes[demand, k].set_ylabel("Utility of the EV")
            axes[demand, k].set_xlabel("Demand in kWh")
            axes[demand, k].legend()
            axes[demand, k].grid(True)
            axes[demand, k].invert_xaxis()
            count+=1
    
    