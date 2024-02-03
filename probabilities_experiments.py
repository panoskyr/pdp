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
            t=0.05*n
            probabilities.append(calculate_probability(n,c,t))
        ax.plot(c_percentages, probabilities, label=f'n={n}')
    
    ax.set_title("P(detection) vs Number of Queried Blocks (c) for 1% corruption" )
    ax.set_xlabel("Number of queried blocks (c) as a % of n")
    ax.set_ylabel("Probability of detection")
    ax.legend()
    ax.grid(True)
    
    fig.savefig(fname="p-detect-5-percent.jpg")


# Example usage
# n_values = np.linspace(1000, 10000, 9)  # Adjust the range as needed
# c_values = np.linspace(start=0, stop=20, num=20)


# plot_probability_graph(n_values, c_values)
    
def a():
    n=1000
    t=0.05*n
    c=380
    print(calculate_probability(n,c,t))


def plot_fixed_probability():
    n_values=np.linspace(1000,100000,20)
    c_values=np.linspace(50,400,7)
    fig,ax=plt.subplots()

    for n in n_values:
        probabilities=[]
        t=0.05*n 
        for c in c_values:
            probabilities.append(calculate_probability(n=n,c=c, t=t))
        ax.plot(c_values,probabilities)
    
    ax.set_title("P(detection)" )
    ax.set_xlabel("Number of queried blocks (c) as a % of n")
    ax.set_ylabel("Probability of detection")
    ax.legend()
    ax.grid(True)
    
    fig.savefig(fname="p-fixed-5-percent.jpg")

plot_fixed_probability()




