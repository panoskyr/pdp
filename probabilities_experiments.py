import numpy as np
import matplotlib.pyplot as plt

def calculate_probability(n, c, t):
    # probability that i detect misbehavior with t deleted blocks and c sample blocks
    probability = 1 - ((n - c - 1 - t) / (n -c-1))**c
    return probability



def plot_probability_graph(n_values, c_percentages):
    fig, ax=plt.subplots()

    for n in n_values:
        probabilities=[]
        for c_percentage in c_percentages:
            c=(c_percentage/100) * n
            t=0.01*n
            probabilities.append(calculate_probability(n,c,t))
        ax.plot(c_percentages, probabilities, label=f'n={n}')
    
    ax.set_title("P(detection) vs Number of Queried Blocks (c) for 1% corruption" )
    ax.set_xlabel("Number of queried blocks (c) as a % of n")
    ax.set_ylabel("Probability of detection")
    ax.legend()
    ax.grid(True)
    
    fig.savefig(fname="Probability of detection for different size of deleted blocks more n.jpg")


# Example usage
n_values = np.linspace(10000, 20000, 9)  # Adjust the range as needed
c_values = np.linspace(start=10, stop=50, num=5)


plot_probability_graph(n_values, c_values)
