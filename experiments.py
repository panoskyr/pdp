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

def time_create_challenge(filepath,key_size,number_of_blocks,challenge_blocks, num_challenges):
    filename, extension=os.path.splitext(filepath)
    tagspath=filename+ "_tags"+extension
    pdp=Public_PDP(filepath=filepath,tagspath=tagspath, key_size=key_size)
    pk,sk=pdp.rsa_key()
    pdp.tagfile(filepath,number_of_blocks,pk,sk)

    start_time=time.time() 
    for chal in range(num_challenges):
        pdp.gen_challenge(pk,num_of_chals=challenge_blocks)
    end_time=time.time()

    elapsed_time=end_time-start_time

    time_per_chal=elapsed_time / num_challenges
    print("Time to generate {} challenges: {}".format(num_challenges, elapsed_time))
    print("Time per challenge: ", time_per_chal)

def time_create_proof(filepath,key_size,number_of_blocks,challenge_blocks, num_challenges):
    filename, extension=os.path.splitext(filepath)
    tagspath=filename+ "_tags"+extension
    pdp=Public_PDP(filepath=filepath,tagspath=tagspath, key_size=key_size)
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
    print("Time per proof generation for S-PDP: ", time_per_proof)
    return time_per_proof


number_of_blocks=[10, 100,1000]
import os
# folderpath="fs/"
# files = [os.path.join(folderpath,f) for f in os.listdir(folderpath) if os.path.isfile(os.path.join(folderpath, f))]
# we have to adjust for the number of blocks because otherwise we get the following error
# ValueError: Exceeds the limit (4300) for integer string conversion: value has 23674 digits;
#  use sys.set_int_max_str_digits() to increase the limit
files=["fs/100_bytes.txt", "fs/1000_bytes.txt","fs/10000_bytes.txt","fs/100000_bytes.txt","fs/1000000_bytes.txt"]

# for file,num_of_blocks in zip(files,number_of_blocks):
#     print(file,num_of_blocks)
#     time_create_replica(file,512,num_of_blocks)


# time_create_challenge("fs/10000_bytes.txt",512,1000, 400,100)
# time_create_proof("fs/100000_bytes.txt",512,400, 400,10)
def plot_proof_time_per_block():
    # times=[]
    # blocks=[]
    # for num_blocks in range(500,10000,500):
    #     blocks.append(num_blocks)
    #     times.append(time_create_proof("fs/100000_bytes.txt",512,num_blocks, 400,5))
        
    # print (times)
    # print(blocks)


    times=[1.4669550895690917, 1.006958532333374, 0.8640816688537598, 0.7885423183441163, 0.7152153968811035, 0.7220099925994873, 0.673245620727539, 0.6510652065277099, 0.6850062370300293, 0.6391323566436767, 0.7058959484100342, 0.6457850456237793, 0.6586476802825928, 0.6600796222686768, 0.6086238384246826, 0.6399340152740478, 0.6492188930511474, 0.6720044136047363, 0.6474973678588867]
    blocks=[500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000, 9500]
    blocksize=[100000// b for b in blocks]

    plt.plot(blocksize,times)

    plt.xlabel("Block size (bytes)")
    plt.ylabel("Proof generation time (s)")
    plt.title("Proof generation time vs Block size")
    plt.legend()

    plt.savefig("Blocksize_proof_time.png")

def time_tradeoff_preprocessing_proofgen(filepath,key_size,challenge_blocks):
    filename, extension=os.path.splitext(filepath)
    tagspath=filename+ "_tags"+extension
    pdp=Public_PDP(filepath=filepath,tagspath=tagspath, key_size=key_size)
    pk,sk=pdp.rsa_key()

    preprocessing_times=[]
    blocks=[]
    proofgen_times=[]


    for num_blocks in range(500,50,-100):
        blocks.append(num_blocks)
        t1=time.time()
        pdp.tagfile(filepath,num_blocks,pk,sk)
        t2=time.time()
        elapsed_time=t2-t1

        preprocessing_times.append(elapsed_time)
        print(num_blocks," tagged file")
        chal=pdp.gen_challenge(pk,num_of_chals=challenge_blocks)
        start_time=time.time() 
        pdp.gen_proof(pk,chal)
        end_time=time.time()

        elapsed_time=end_time-start_time
        proofgen_times.append(elapsed_time)
        print(num_blocks, "challenge done")

    print(preprocessing_times)
    print(blocks)
    print(proofgen_times)

def plot_tradeoff_preprocessing_proofgen():
# time_tradeoff_preprocessing_proofgen("fs/100000_bytes.txt",512 ,400)
    preprocessing_times=[81.36914443969727, 71.64296078681946, 66.43421936035156, 58.37679576873779, 53.05766320228577, 46.72343564033508, 41.005367279052734, 36.23488116264343, 31.41566252708435, 26.709068298339844, 23.630056619644165, 19.73828101158142, 16.32840895652771, 13.046043157577515, 9.976933479309082, 7.963518142700195, 6.43603777885437, 4.3269031047821045, 2.9445297718048096]
    proofgen_times=[0.5956690311431885, 0.5920383930206299, 0.5951406955718994, 0.5979886054992676, 0.6002893447875977, 0.6031191349029541, 0.6208312511444092, 0.6224358081817627, 0.6123216152191162, 0.6323070526123047, 0.6467475891113281, 0.648059606552124, 0.6442465782165527, 0.6526796817779541, 0.6776039600372314, 0.6997809410095215, 0.7470924854278564, 0.8229777812957764, 0.937746524810791]
    numblocks=[10000, 9500, 9000, 8500, 8000, 7500, 7000, 6500, 6000, 5500, 5000, 4500, 4000, 3500, 3000, 2500, 2000, 1500, 1000]
    blocksize=[100000/b for b in numblocks]


    plt.plot(blocksize,proofgen_times,color="red", label="Proof Generation time (s)")
    plt.plot(blocksize,preprocessing_times,color="blue", label="Preprocessing time (s)")

    plt.xlabel("Block size (bytes)")
    plt.ylabel("Time (s)")
    plt.title("Tradeoff between Proof Generation and Preprocessing time \nfor different block sizes")
    plt.legend()

    plt.savefig("tradeoff_for_dif_block_sizes.png")

# plot_tradeoff_preprocessing_proofgen()

# time_tradeoff_preprocessing_proofgen("fs/1000000_bytes.txt",512 ,50)
    


def time_proof_checking(filepath,key_size,number_of_blocks,challenge_blocks, num_challenges):
    filename, extension=os.path.splitext(filepath)
    tagspath=filename+ "_tags"+extension
    pdp=Public_PDP(filepath=filepath,tagspath=tagspath, key_size=key_size)
    pk,sk=pdp.rsa_key()
    pdp.tagfile(filepath,number_of_blocks,pk,sk)

    times=[]
    for _ in range(num_challenges):
        chal=pdp.gen_challenge(pk,num_of_chals=challenge_blocks)
        V,coefs=pdp.gen_proof(pk,chal)

        start_time=time.time()
        pdp.check_proof(pk,sk,V,coefs,chal)
        end_time=time.time()
        times.append(end_time-start_time)

    elapsed_time=sum(times)
    time_per_check_proof=elapsed_time / num_challenges
    print("Time to generate {} proofs: {}".format(num_challenges, elapsed_time))
    print("Time per proof checking for S-PDP: ", time_per_check_proof)
    return time_per_check_proof

def trial_time_proof_checking():
    # when possible do 400 blocks for challenge as in original paper
    # proof_checking_e_pdp.png
    key_size=512
    runs=10
    trials=[[files[0],512,100,100,runs],
    [files[1],512,500,400,runs],
    [files[2], 512, 500, 400,runs],
    [files[3], 512, 500, 400, runs],
    [files[4], 512, 600, 400, runs]]
    times=[]
    for trial in trials:
        times.append(time_proof_checking(*trial))
    return times

def plot_check_proof_time():
    check_proof_times=trial_time_proof_checking()
    filesize=[10**2, 10**3, 10**4, 10**5, 10**6]
    num_blocks=[100,500,500,500,600]

    block_size_in_bytes=[a//b for a,b in zip(filesize,num_blocks)]

    l=len(block_size_in_bytes)
    plt.plot(block_size_in_bytes,[check_proof_times[0]]*l,label="100 (only 100 challenges)")
    plt.plot(block_size_in_bytes,[check_proof_times[1]]*l,label="1000")
    plt.plot(block_size_in_bytes,[check_proof_times[2]]*l,label="10000")
    plt.plot(block_size_in_bytes,[check_proof_times[3]]*l,label="100000")
    plt.plot(block_size_in_bytes,[check_proof_times[4]]*l,label="1000000")

    plt.xlabel("File size (bytes)")
    plt.ylabel("Time (s)")
    plt.legend()


    plt.title("S-PDP:CheckProof time for 400 blocks per challenge \nfor different file sizes ")
    plt.savefig("spdp_proof_check_time_vs_bytes_in_challenge.png")


def time_proof_checking_for_comparison(filepath,key_size,number_of_blocks,challenge_blocks, num_challenges):
    filename, extension=os.path.splitext(filepath)
    tagspath=filename+ "_tags"+extension
    pdp=Public_PDP(filepath=filepath,tagspath=tagspath, key_size=key_size)
    pk,sk=pdp.rsa_key()
    pdp.tagfile(filepath,number_of_blocks,pk,sk)

    tag_time_start=time.time()
    pdp.tagfile(filepath,number_of_blocks,pk,sk)
    tag_time_end=time.time()

    gen_chal_time_start=time.time()
    chal=pdp.gen_challenge(pk,num_of_chals=challenge_blocks)
    gen_chal_time_end=time.time()

    gen_proof_time_start=time.time()
    V, coefs=pdp.gen_proof(pk,chal)
    gen_proof_time_end=time.time()

    check_proof_time_start=time.time()
    pdp.check_proof(pk,sk,V,coefs,chal)
    check_proof_time_end=time.time()

    tag_time=tag_time_end-tag_time_start
    gen_chal_time=gen_chal_time_end-gen_chal_time_start
    gen_proof_time=gen_proof_time_end-gen_proof_time_start
    check_proof_time=check_proof_time_end-check_proof_time_start

    return [tag_time,gen_chal_time, gen_proof_time,check_proof_time]
from e_pdp_experiments import print_avg_from_trials
def compare_trials_comparison():
    trial=[files[3], 512, 500, 400,10]
    print(trial[0])
    time_trials=[]
    for i in range(10):
        time_trials.append(time_proof_checking_for_comparison(*trial))
    print(time_trials)
    print_avg_from_trials(time_trials)


compare_trials_comparison()

