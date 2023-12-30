from public_PDP import test, Public_PDP
import matplotlib.pyplot as plt 
import numpy as np
import time


# test("fs/100000_bytes.txt",512,1000,100)


def verifier_space(key_size, chal_size, num_chal, num_replicas, replica_size):
    verifier_storage = key_size * num_replicas
    verifier_comm_per_challenge = chal_size * num_replicas
    total_comm = verifier_comm_per_challenge * num_chal

    return verifier_storage+total_comm
    

def verifier_decision(verifier_space, replica_size):


    if verifier_space> replica_size:
        return "Keep on blockchain"
    else:
        return "Keep on servers"

def repl_size_3d():
    # Fixed challenge size
    chal_size = 768
    # Fixed key size
    key_size = 1024
    num_chal=10

    # Continuous values for replica_size
    replica_size_values = np.logspace(2, 6, num=100)  # Varying from 100 to 10^6

    # Values for num_replicas
    num_replicas_values = list(range(1, 11))

    # Create a meshgrid for the values
    x, y = np.meshgrid(replica_size_values, num_replicas_values)

    # Function to calculate total_comm for each replica size
    def calculate_total_comm(replica_size, num_replicas):
        return verifier_space(key_size, chal_size, num_chal, num_replicas, replica_size)

    # Vectorize the function to work with numpy arrays
    calculate_total_comm_vectorized = np.vectorize(calculate_total_comm)

    # Create a 3D meshgrid for the total communication values
    z_values = calculate_total_comm_vectorized(x, y)

    # Plot the results
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(np.log10(x), y, z_values, cmap='viridis', edgecolor='k')

    ax.set_xlabel('Log10(Replica Size)')
    ax.set_ylabel('Number of Replicas')
    ax.set_zlabel('Total Communication (bytes)')
    ax.set_title('Relationship between Replica Size, Number of Replicas, and Total Communication')
    ax.set_zscale('log')  # Use a logarithmic scale for the z-axis
    ax.view_init(elev=20, azim=45)  # Set the view angle for better visualization

    plt.savefig("repl_size3d.png")

def file_size_vs_verifier_size():
    key_size = 1024
    chal_size = 768
    num_chal = 30
    num_replicas = 10

    replica_size_values = np.linspace(100, 10**6, 100)

    verifier_space_values2 = [verifier_space(key_size, chal_size, num_chal, 2, size) for size in replica_size_values]
    verifier_space_values5 = [verifier_space(key_size, chal_size, num_chal, 5, size) for size in replica_size_values]
    verifier_space_values10= [verifier_space(key_size, chal_size, num_chal, 10, size) for size in replica_size_values]

    all_in_verifier_space_values = [size for size in replica_size_values]

    plt.figure(figsize=(10, 6))
    plt.plot(replica_size_values, verifier_space_values2, label='Verifier Space 2 replicas')
    plt.plot(replica_size_values, verifier_space_values5, label='Verifier Space 5 replicas')
    plt.plot(replica_size_values, verifier_space_values10, label='Verifier Space 10 replicas')

    plt.plot(replica_size_values, all_in_verifier_space_values, label='File stored in Verifier', linestyle='--')

    plt.xlabel('Replica Size (bytes)')
    plt.ylabel('Space Needed (bytes)')
    plt.title('Space needed in Verifier for varying file sizes')
    plt.legend()
    plt.grid(True)
    plt.savefig("total_space_vs_file_size.png")



def time_create_replica(filepath,key_size,number_of_blocks):
    # to create a replica using PDP we need to generate the keys 
    # and also tag the file.
    start_time=time.time() 
    filename, extension=os.path.splitext(filepath)
    tagspath=filename+ "_tags"+extension
    pdp=Public_PDP(filepath=filepath,tagspath=tagspath, key_size=key_size)
    pk, sk=pdp.rsa_key()
    pdp.tagfile(filepath,number_of_blocks,pk,sk)
    end_time=time.time()
    elapsed_time=end_time-start_time
    print("Time to create a replica: " ,elapsed_time)

number_of_blocks=[10, 100,1000]
import os
# folderpath="fs/"
# files = [os.path.join(folderpath,f) for f in os.listdir(folderpath) if os.path.isfile(os.path.join(folderpath, f))]
# we have to adjust for the number of blocks because otherwise we get the following error
# ValueError: Exceeds the limit (4300) for integer string conversion: value has 23674 digits;
#  use sys.set_int_max_str_digits() to increase the limit
files=["fs/100_bytes.txt", "fs/1000_bytes.txt","fs/10000_bytes.txt"]

for file,num_of_blocks in zip(files,number_of_blocks):
    print(file,num_of_blocks)
    time_create_replica(file,512,num_of_blocks)


