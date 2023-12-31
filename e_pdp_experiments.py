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
    trials=[[files[0],512,100,100,runs],
    [files[1],512,500,400,runs],
    [files[2], 512, 500, 400,runs],
    [files[3], 512, 500, 400, runs],
    [files[4], 512, 600, 400, runs]]
    times=[]
    for trial in trials:
        times.append(time_proof_checking(*trial))
    print(times)

def plot_check_proof_time_epdp():
    check_proof_times=[0.014735984802246093, 0.014516353607177734, 0.014137744903564453, 0.014367508888244628, 0.003717803955078125]
    check_proof_times_asc=check_proof_times[::-1]
    filesize=[10**2, 10**3, 10**4, 10**5, 10**6]
    num_blocks=[100,500,500,500,600]

    block_size_in_bytes=[a//b for a,b in zip(filesize,num_blocks)]

    l=len(block_size_in_bytes)
    plt.plot(block_size_in_bytes,[check_proof_times_asc[0]]*l,label="100 (only 100 challenges)")
    plt.plot(block_size_in_bytes,[check_proof_times_asc[1]]*l,label="1000")
    plt.plot(block_size_in_bytes,[check_proof_times_asc[2]]*l,label="10000")
    plt.plot(block_size_in_bytes,[check_proof_times_asc[3]]*l,label="100000")
    plt.plot(block_size_in_bytes,[check_proof_times_asc[4]]*l,label="1000000")

    plt.xlabel("File size (bytes)")
    plt.ylabel("Time (s)")
    plt.legend()


    plt.title("CheckProof time for 400 blocks per challenge \nfor different file sizes ")
    plt.savefig("proof_check_time_vs_bytes_in_challenge.png")
    
def time_proof_checking_for_comparison(filepath,key_size,number_of_blocks,challenge_blocks, num_challenges):
    filename, extension=os.path.splitext(filepath)
    tagspath=filename+ "_tags"+extension
    pdp=E_PDP(filepath=filepath,tagspath=tagspath, key_size=key_size)
    pk,sk=pdp.rsa_key()
    tag_time_start=time.time()
    pdp.tagfile(filepath,number_of_blocks,pk,sk)
    tag_time_end=time.time()

    gen_chal_time_start=time.time()
    chal=pdp.gen_challenge(pk,num_of_chals=challenge_blocks)
    gen_chal_time_end=time.time()

    gen_proof_time_start=time.time()
    V=pdp.gen_proof(pk,chal)
    gen_proof_time_end=time.time()

    check_proof_time_start=time.time()
    pdp.check_proof(pk,sk,V,chal)
    check_proof_time_end=time.time()

    tag_time=tag_time_end-tag_time_start
    gen_chal_time=gen_chal_time_end-gen_chal_time_start
    gen_proof_time=gen_proof_time_end-gen_proof_time_start
    check_proof_time=check_proof_time_end-check_proof_time_start

    return [tag_time,gen_chal_time, gen_proof_time,check_proof_time]



def compare_trials_comparison():
    trial=[files[3], 512, 500, 400,10]
    time_trials=[]
    for i in range(10):
        time_trials.append(time_proof_checking_for_comparison(*trial))
    print(time_trials)
# trials=[[1.0603930950164795, 0.00029754638671875, 0.11113238334655762, 0.014624595642089844], [1.034226655960083, 0.00026345252990722656, 0.11201643943786621, 0.017019987106323242], [0.9397141933441162, 0.0002682209014892578, 0.10011601448059082, 0.014503717422485352], [1.0192842483520508, 0.0002646446228027344, 0.10857653617858887, 0.014707326889038086], [0.949462890625, 0.0002617835998535156, 0.10524582862854004, 0.014547586441040039], [0.9486091136932373, 0.00026106834411621094, 0.10635542869567871, 0.014729976654052734], [1.0043368339538574, 0.00032520294189453125, 0.10454654693603516, 0.014475584030151367], [1.0523738861083984, 0.0002624988555908203, 0.11185145378112793, 0.01454472541809082], [0.9445037841796875, 0.0002601146697998047, 0.10436272621154785, 0.014287948608398438], [0.9741437435150146, 0.000354766845703125, 0.10868048667907715, 0.014751672744750977]]
    print_avg_from_trials(time_trials)


def print_avg_from_trials(trials):
    time_categories = list(map(list, zip(*trials)))

    avg_tag_time = sum(time_categories[0]) / len(time_categories[0])
    avg_gen_chal_time = sum(time_categories[1]) / len(time_categories[1])
    avg_gen_proof_time = sum(time_categories[2]) / len(time_categories[2])
    avg_check_proof_time = sum(time_categories[3]) / len(time_categories[3])

    print(f"Average Tag Time: {avg_tag_time}")
    print(f"Average Generate Challenge Time: {avg_gen_chal_time}")
    print(f"Average Generate Proof Time: {avg_gen_proof_time}")
    print(f"Average Check Proof Time: {avg_check_proof_time}")


compare_trials_comparison()