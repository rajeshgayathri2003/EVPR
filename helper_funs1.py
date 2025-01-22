import numpy as np

def energy_requirement_of_customers(final_SOC, initial_SOC, battery_capacity):
    """Function to calculate the energy requirement of the nth Electric Vehicle

    Args:
        final_SOC (np.ndarray): It is a numpy array of dimension (n,1) where the nth element of the array denotes the final SOC of the nth electric vehicle
        initial_SOC (np.ndarray): It is a numpy array of dimension (n,1) where the nth element of the array denotes the initial SOC of the nth electric vehicle
        battery_capacity (np.ndarray): It is a numpy array of dimension (n,1) where the nth element of the array denotes the battery capacity of the nth electric vehicle

    Returns:
        np.ndarray: It is a numpy array where the nth element denotes the energy requirement of the nth EV
    """
    return (final_SOC-initial_SOC)*battery_capacity

def profit_of_kth_station_at_time_t(lambda_sell, lambda_purchase, energy):
    """Calculate the profit of the kth charging station

    Args:
        lambda_sell (float): A floating point value that indicates the selling of electricity to the elctric vehicle at time t
        lambda_purchase (float): A floating point value that indicates the price at which electricity is purchased from the grid at time t
        energy (np.ndarray): This is a numpy array where the nth element denotes the energy supplied to the nth EV
    Returns:
        float: The profit earned by the kth charging station
    """
    profit = np.sum(lambda_sell*energy - lambda_purchase*energy)
    
    return profit

def calculate_energy_n(lambda_max, lambda_sell_t, S):
    energy_n = np.divide((lambda_max - lambda_sell_t),S)
    return energy_n

def calculate_base_sensitivity(lambda_max, lambda_b, battery_capacity):
    S_b = np.divide((lambda_max-lambda_b)/battery_capacity)
    return S_b

def calculate_alpha(lambda_sell, lambda_b, lambda_max):
    val = np.divide((lambda_sell-lambda_b),(lambda_max-lambda_b))
    n = np.shape[0]
    alpha = np.max(np.min(np.ones(n)-val,np.ones(n)),np.zeros(n))
    return alpha

def calculate_behavioural_response(alpha, type_="high"):
    if type_ == "high":
        return (np.exp(alpha)-1)/(np.e - 1)
    if type_ == "medium":
        return alpha
    if type_ == "low":
        return np.log(alpha*(np.e-1)+1)