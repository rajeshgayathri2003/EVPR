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
    plt.show()
    
    
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
    
    plt.legend()
    #plt.show()
    
def plot_nash_equilibrium(profit_variation, omega_variation, demand_variation):
    """This function plots the profits versus the utility function to identify the nash equilibrium
    """
    plt.figure(4)
    #time_steps = np.arange(count)
    
    omega_plot = omega_variation[:,0,0]
    demand_plot = demand_variation[:,0,0]
    
    plt.plot(demand_plot, profit_variation, label = "Profit to the charging station", color = 'b')
    plt.plot(demand_plot, omega_plot, label = "Utility of EV", color = 'r', linestyle = '--')
    
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Nash Equilibrium', fontsize=10)
    
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
    
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Nash Equilibrium', fontsize=10)
    
    plt.legend()
