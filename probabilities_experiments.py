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
    n=100000
    t=0.1*n
    for c in np.linspace(25,400,8):
        print("c is {}, t is {} , prob is:{} ".format(c,0.010,calculate_probability(n,c,t)))


def plot_fixed_probability():
    n_values=[10**5]
    c_values=np.linspace(50,400,7)
    fig,ax=plt.subplots()

    for n in n_values:
        probabilities=[]
        t=0.05*n 
        for c in c_values:
            probabilities.append(calculate_probability(n=n,c=c, t=t))
        ax.plot(c_values,probabilities, label="t=5%")

    for n in n_values:
        probabilities=[]
        t=0.01*n 
        for c in c_values:
            probabilities.append(calculate_probability(n=n,c=c, t=t))
        ax.plot(c_values,probabilities, label="t=1%")

    for n in n_values:
        probabilities=[]
        t=0.1*n 
        for c in c_values:
            probabilities.append(calculate_probability(n=n,c=c, t=t))
        ax.plot(c_values,probabilities, label="t=10%")
    
    ax.set_title("P(detection) for t=1, 5 and 10% for a 10^5 blocks file" )
    ax.set_xlabel("Number of queried blocks (c)")
    ax.set_ylabel("Probability of detection P_X")
    ax.legend()
    ax.grid(True)
    
    fig.savefig(fname="p-fixed-for-different-1-5-10-corruption.jpg")

def get_different_probabilities_per_challenge():
    c_values=np.linspace(10,100, 10)
    n=10**5
    t=0.01*n
    return [(calculate_probability(n=n, c=c, t=t),c) for c in c_values] 


from scipy.stats import binom

# Function to plot the CDF of a binomial distribution
def plot_binomial_cdf():
    # a challenge daily


    fig,ax=plt.subplots()

    for p ,c in get_different_probabilities_per_challenge():
        tries=30
        x = np.arange(1, tries+1)
        print(p,c)
        at_least_one_success=[]
        for challenge in range(tries):
            at_least_one_success.append(1-binom.pmf(k=0, n=challenge, p=p))
        ax.step(x, at_least_one_success, where='mid', label='{} blocks / challenge '.format(int(c)))

    plt.title('P(detection) for 1% corruption for a month')
    plt.xlabel('Number of Challenges')
    plt.ylabel('Probability of at least 1 detection')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.legend()
    plt.savefig("CDF.png")

plot_binomial_cdf()
