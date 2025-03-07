import csv
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

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
            
def read_from_csv(file_path):
    curr = os.getcwd()
    file_path = os.path.join(curr, file_path)
    data = []
    with open(file_path, 'r') as f:
        file = csv.reader(f)
        for lines in file:
            data.append(lines)
    
    return data

def plot_time_selling_purchse_price(data):
    plt.figure(1)
    
    time = np.linspace(0, 23, 24)
    sell = [float(i[0]) for i in data ]
    purchase = [float(i[1]) for i in data ]

    plt.step(time, sell, label="Selling Price", where="mid", color="steelblue", linewidth=2)
    plt.step(time, purchase, label="Electricity Cost", where="mid", color="orange", linewidth=2)

    plt.xlabel('Hours')
    plt.ylabel('cents/kWh')
    plt.title("Hourly cost of purchasing electricity from the grid and selling price")

    # ax = plt.gca()
    # ax.yaxis.set_major_locator(ticker.MultipleLocator(1))  # Ensure consistent tick intervals

    plt.legend()
    plt.grid()
    
def plot_time_average_hourly_cost_per_charging_session(data):
    plt.figure(2)
    time = np.linspace(0, 23, 24)
    price = [float(i[0])/100 for i in data]
    plt.step(time, price, label = "Price of electricity sold to EV", color = 'b')
    plt.xlabel('Hours')
    plt.ylabel('Dollar')
    plt.title("Average cost per charging session")
    
    plt.legend()
    plt.grid()
    
        
if __name__ == "__main__":
    prices = read_from_csv("sell_purchase_1.csv")
    plot_time_selling_purchse_price(prices)
    
    cost_charging_session = read_from_csv("average_amount_1.csv")
    plot_time_average_hourly_cost_per_charging_session(cost_charging_session)
    
    plt.show()
    
    
    
    
    
    
        
    