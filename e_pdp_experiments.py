from e_pdp import  E_PDP
import matplotlib.pyplot as plt 
import numpy as np
import time
import os
files=["fs/1000_bytes.txt","fs/10000_bytes.txt","fs/100000_bytes.txt","fs/1000000_bytes.txt"]

def time_create_replica(filepath,key_size,number_of_blocks):
    # to create a replica using PDP we need to generate the keys 
    # and also tag the file.
    start_time=time.time() 
    filename, extension=os.path.splitext(filepath)
    tagspath=filename+ "_tags_e"+extension
    pdp=E_PDP(filepath=filepath,tagspath=tagspath, key_size=key_size)
    pk, sk=pdp.rsa_key()
    pdp.tagfile(filepath,number_of_blocks,pk,sk)
    end_time=time.time()
    elapsed_time=end_time-start_time
    print("Time to create a replica: " ,elapsed_time)
    return elapsed_time

def dif_num_blocks_files_replica_creation():
# different replica creation for same number of blocks
    for f in files:
        times=[]
        for num_blocks in [100,200,250,500]:
            times.append(time_create_replica(f,512,num_blocks))
            print("for file {} time for 1 replica creation (e-pdp) and {} blocks is: ".format(f,num_blocks))
        print(times)
    

    

def plot_replica_creation_time_vs_block_size():
# from dif_num_blocks_files_replica_creation():

    replica_time_1000_bytes=[0.20560598373413086, 0.3384819030761719, 0.43284130096435547, 0.9009180068969727]  
    replica_time_10000_bytes=[0.2724902629852295, 0.451946496963501, 0.5302445888519287, 1.0588581562042236]
    replica_time_100000_bytes=[1.2115259170532227, 1.3950207233428955, 1.499701976776123, 1.8913791179656982]
    num_blocks=[100,200,250,500]
    plt.plot(num_blocks ,replica_time_1000_bytes, label="10^3 bytes", color="red")
    plt.plot(num_blocks, replica_time_10000_bytes, label="10^4 bytes", color="blue")
    plt.plot(num_blocks, replica_time_100000_bytes, label="10^5 bytes", color="green")
    
    plt.xlabel("Number of blocks")
    plt.ylabel("Time needed (s)")
    plt.title("Replica generation time for different file sizes \nand number of blocks")
    plt.legend()

    plt.savefig("repl_creation_dif_files_and_num_blocks.png")    

plot_replica_creation_time_vs_block_size()