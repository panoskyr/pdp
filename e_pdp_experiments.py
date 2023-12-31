from e_pdp import  E_PDP
import matplotlib.pyplot as plt 
import numpy as np
import time
import os
files=["fs/100_bytes.txt","fs/1000_bytes.txt","fs/10000_bytes.txt","fs/100000_bytes.txt","fs/1000000_bytes.txt"]

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

def time_proof_generation(filepath,key_size,number_of_blocks,challenge_blocks, num_challenges):
    filename, extension=os.path.splitext(filepath)
    tagspath=filename+ "_tags"+extension
    pdp=E_PDP(filepath=filepath,tagspath=tagspath, key_size=key_size)
    pk,sk=pdp.rsa_key()
    pdp.tagfile(filepath,number_of_blocks,pk,sk)

    times=[]
    for _ in range(num_challenges):
        chal=pdp.gen_challenge(pk,num_of_chals=challenge_blocks)
        start_time=time.time() 
        pdp.gen_proof(pk,chal)
        end_time=time.time()
        times.append(end_time-start_time)
    
    
    elapsed_time=sum(times)
    time_per_proof=elapsed_time / num_challenges
    print("Time to generate {} proofs: {}".format(num_challenges, elapsed_time))
    print("Time per proof generation for E-PDP: ", time_per_proof)
    return time_per_proof

# time_proof_generation(files[0],512,50,20,10)
# time_proof_generation(files[1], 512,100,40,10)
# time_proof_generation(files[2], 512,500,100,10)
#time_proof_generation(files[3], 1024,600,100,10)
# time_proof_generation(files[0], 512,50,20,10)
def plot_proof_gen_time_vs_file_size():

# time_proof_generation(files[0],512,50,20,10)
# time_proof_generation(files[1], 512,100,40,10)
# time_proof_generation(files[2], 512,500,200,10)
#time_proof_generation(files[3], 512,600,240,10)
# time_proof_generation(files[0], 512,50,20,10)
    filesize=[10**2, 10**3, 10**4, 10**5, 10**6]
    times=[0.0007976055145263672, 0.005676794052124024, 0.04509317874908447,0.2185814380645752 ,5.177749228477478]


    plt.plot(filesize,times, color="blue")
    plt.xlabel("File size (bytes)")
    plt.ylabel("Time (s)")

    plt.title("Proof generation with 40% of blocks \n for different file sizes")
    plt.savefig("proof_generation_timevsfilesize.png")


def time_proof_checking(filepath,key_size,number_of_blocks,challenge_blocks, num_challenges):
    filename, extension=os.path.splitext(filepath)
    tagspath=filename+ "_tags"+extension
    pdp=E_PDP(filepath=filepath,tagspath=tagspath, key_size=key_size)
    pk,sk=pdp.rsa_key()
    pdp.tagfile(filepath,number_of_blocks,pk,sk)

    times=[]
    for _ in range(num_challenges):
        chal=pdp.gen_challenge(pk,num_of_chals=challenge_blocks)
        V=pdp.gen_proof(pk,chal)

        start_time=time.time()
        pdp.check_proof(pk,sk,V,chal)
        end_time=time.time()
        times.append(end_time-start_time)

    elapsed_time=sum(times)
    time_per_check_proof=elapsed_time / num_challenges
    print("Time to generate {} proofs: {}".format(num_challenges, elapsed_time))
    print("Time per proof checking for E-PDP: ", time_per_check_proof)
    return time_per_check_proof
    

def trial_time_proof_checking():
    # when possible do 400 blocks for challenge as in original paper
    # proof_checking_e_pdp.png
    key_size=512
    runs=10
    trials=[[files[0],512,50,50,runs],
    [files[1],512,500,400,runs],
    [files[2], 512, 500, 400,runs],
    [files[3], 512, 500, 400, runs],
    [files[4], 512, 600, 400, runs]]
    times=[]
    for trial in reversed(trials):
        times.append(time_proof_checking(*trial))
    print(times)

trial_time_proof_checking()
