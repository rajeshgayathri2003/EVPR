import matplotlib.pyplot as plt
import numpy as np


def plot_gridpurchase_sell(cs_sell_price_variation, cs_purchase_price_variation, n, count, k =0):
    fig, axes = plt.subplots(n, 1, figsize=(8, 2 * n), sharex=True)
    fig.suptitle('Variation of Selling Price to EVs and Purchase from the grid for CS', fontsize=16)
    time_steps = np.arange(count+1)
    
    selling_price = cs_sell_price_variation[: ,: ,k]
    purchase_price = cs_purchase_price_variation[:,:,k]
    
    for vehicle in range(1):
        axes[vehicle].plot(time_steps, selling_price[:, vehicle], label=f"Selling Price - Vehicle {vehicle + 1}")
        axes[vehicle].plot(time_steps, purchase_price[:, vehicle], linestyle='--', label=f"Purchase Price - Vehicle {vehicle + 1}")
        axes[vehicle].set_title(f"Vehicle {vehicle + 1}")
        axes[vehicle].set_ylabel("Price")
        axes[vehicle].legend()
        axes[vehicle].grid(True)
        
    axes[-1].set_xlabel("Time Steps")
    plt.tight_layout()
    plt.show()