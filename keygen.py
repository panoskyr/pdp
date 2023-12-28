from cryptography.hazmat.primitives.asymmetric import rsa,utils
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
import random
from sympy import isprime
import string
import lorem
import math
def rsa_keygen(key_size=512):
    private_key=rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size
    )
    private_key_readable=private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    

    public_key=private_key.public_key()
    public_key_readable=public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


    p_prime=private_key.private_numbers().p
    q_prime=private_key.private_numbers().q
    N_public_modulus=public_key.public_numbers().n
    d_private_exponent=private_key.private_numbers().d
    e_public_exponent=65537
    # it holds that e*d congruent to 1mod(phi(n)) equal to (p-1)*(q-1)
   
    # print(e)
    # pk=(N)
    # sk=(e, d_private_exponent,u)
    # return pk,sk
    p_tonos=int((p_prime-1)/2)
    q_tonos=int((q_prime-1)/2)
    pq_tonos=p_tonos*q_tonos
    # e=pow(d_private_exponent,-1,pq_tonos)
    # print(isprime(e))
    # return N_public_modulus, e,d_private_exponent, p_prime,q_prime
    return N_public_modulus,p_prime,q_prime,d_private_exponent, pq_tonos

def keygen(key_size):
    # v is a secret random number
    v=83764532362
    N_public_modulus,e_secret,d_private_exponent, p, q=rsa_keygen(key_size)
    g=find_g(p,q,N_public_modulus)
    
    return (N_public_modulus,g), (e_secret,d_private_exponent,v)

def is_ok_number(a, p, q):
    aModp=a % p

    if (
        aModp==0 or aModp==1 or aModp==(p-1) 
    ):
        return False
    
    aModq=a % q 

    if (
        aModq==0 or aModq==1 or aModq==(q-1)
    ):
        return False
    return True


def find_a(p,q,N,upto=1000):
    for _ in range(upto):
        a=random.randrange(1,N+1)
        if ( is_ok_number(a,p=p,q=q) ):
            return a 
    return -1

def find_g(p,q,N):
    a=find_a(p,q,N)
    if a!=-1:
        return a^2
    else:
        return "No g found"
    

def h(message):
    digest=hashes.Hash(hashes.SHA256())
    digest.update(message.encode('utf-8'))
    return digest.finalize()



def find_e():
    while True:
        N_public_modulus,p,q,d_private_exponent, pq_tonos= rsa_keygen(512)
        try :
            e=pow(d_private_exponent,-1, pq_tonos)
            if isprime(e):
                g=find_g(p,q,N_public_modulus)
                v=83764532362
                print( "Found")
                with open("file.txt", "w") as f:
                    f.write("N:"+str(N_public_modulus)+"\n")
                    f.write("g:"+ str(g)+"\n")
                    f.write("e:"+str(e)+"\n")
                    f.write("d:"+str( d_private_exponent)+"\n")
                    f.write("v:"+ str(v)+"\n")



                #end loop when suitable e is found
                break
        # raised when it is not invertible
        except ValueError:
            continue
def load_keys(filename="file.txt"):
    data = {}
    with open(filename, "r") as f:
        lines = f.readlines()

    for line in lines:
        key, value = line.strip().split(":")
        data[key] = value

    return data

def get_keys():
    loaded_data = load_keys()

    N_public_modulus= int(loaded_data["N"])
    g = int(loaded_data["g"])
    e = int(loaded_data["e"])
    d_private_exponent = int(loaded_data["d"])
    v = int(loaded_data["v"])

    pk=(N_public_modulus,g)
    sk=(e,d_private_exponent,v)

    return pk,sk



def generate_random_text(length=100):
    # unicode_characters = [chr(code) for code in range(32, 127)] + [chr(code) for code in range(160, 1280)]

# a= ''.join(random.choice(unicode_characters) for _ in range(length))
    with open('random_text.txt', "w") as f:
        for l in range(length):
            f.write(lorem.text())
def to_digit(s):
    return int(''.join(map(str,map(ord,s))))  
  
def tagfile(file_to_tag,number_of_blocks,pk,sk):
    with open(file_to_tag, "r") as file:
        data=file.read()
    block_size=len(data) // number_of_blocks


    tags=[]
    block_nums=[]
    # blocks=[]
    for block_num in range(number_of_blocks):
        start_idx=block_num*block_size
        # if we are at the last block go to the end of the file.
        end_idx=start_idx+block_size if block_num <number_of_blocks-1 else start_idx+len(file_to_tag)
        block=data[start_idx:end_idx]
        # blocks.append(block)
        tag=tagblock(sk,pk, block, block_num)
        tags.append(tag)
        block_nums.append(block_num)

        with open("tags.txt", "w") as f:
            for block_num, tag in zip(block_nums, tags):
                f.write(f"{block_num}:{tag}\n")

        # with open("blocks.txt", "w") as f:
        #     for block_num,block in zip(block_nums,blocks):
        #         f.write(f"{block_num}:{block}")

def get_num_of_blocks(tagsfilepath):
    with open(tagsfilepath, "rb") as f:
        num_of_blocks=sum(1 for _ in f)
    return num_of_blocks


def gen_challenge(pk):
    N,g=pk
    num_of_blocks=get_num_of_blocks("tags.txt")


    c=7
    assert c <= num_of_blocks
    indices_of_blocks=random.sample(range(num_of_blocks),c)

    # s is generated per challenge
    s=random.getrandbits(16)

    return indices_of_blocks,s


def get_blocks(filepath,tagspath):

    num_of_blocks=get_num_of_blocks(tagspath)
    blocks=[]

    with open(filepath, "r") as file:
        data=file.read()

    block_size=len(data) // num_of_blocks
    print("block_size is ", block_size)


    for block_num in range(num_of_blocks):
        start_idx=block_num*block_size
        # if we are at the last block go to the end of the file.
        end_idx=start_idx+block_size if block_num <num_of_blocks-1 else start_idx+len(filepath)
        block=data[start_idx:end_idx]
        blocks.append(block)
    return blocks

def get_tags(tagspath):
    tags=[]
    with open(tagspath) as f:
        for line in f:
            block_num, tag=line.strip().split(sep=':')
            block_num=int(block_num)
            tags.append(int(tag))
    return tags


def gen_proof(pk,chal):
    indices_of_blocks,s=chal
    N,g=pk


    blocks=get_blocks("d.txt","tags.txt")

    tags=get_tags("tags.txt")

    
    assert len(tags)==len(blocks)

    tags=[tags[i] for i in indices_of_blocks]
    blocks=[blocks[i] for i in indices_of_blocks]
    # tagz=[tagblock(sk,pk,blocks[0],0), tagblock(sk,pk,blocks[1],1)]
    # print(tagz)
    product=1
    for tag in tags:
        product = pow(product*tag,1,N)
    T=product
    

    g_s=pow(g,s,N)
    g_prod=1
    for block in blocks:
        tmp=pow(g_s,to_digit(block),N)
        g_prod=pow(g_prod*tmp,1,N)
    rho=hash_number(g_prod)
    print(rho)
    return (T,rho)

def check_proof(pk,sk,V,chal):
    indices_of_blocks,s=chal
    N,g=pk
    e,d,v=sk
    T,rho=V

    # t= T^e modN and ed congruent 1 modN
    t=pow(T,e,N)


    for i in indices_of_blocks:
        w_i=str(v)+str(i)
        h_w_i=int.from_bytes(h(w_i),byteorder='big')
        h_inv=pow(h_w_i,-1,N)

        t=pow(t*h_inv,1,N)
    
    t_s=pow(t,s,N)

    rho=hash_number(t_s)

    print(rho)


def tagblock(sk,pk,block,i):
    # T_i=(h(w_i) * g ^ block)^ d modn
    # T_i =( (h(w_i)^d ) modn * (g^(block*d)) modn ) modn 
    # the last modn brings it back to [0,N-1]

    w_i=str(sk[2])+str(i)
    g=pk[1]
    d=sk[1]
    N=pk[0]
    g_comp=pow(base=g,exp=(to_digit(block)*d),mod=N)
    w_comp=pow(base=int.from_bytes(h(w_i),byteorder='big'),exp=d, mod=N)
    tag=pow(w_comp*g_comp,1 ,N)
    # print (tag)
    return tag
    
def rsa_key(key_size=512):
    private_key=rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size
    )
    private_key_readable=private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    

    public_key=private_key.public_key()
    public_key_readable=public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


    p_prime=private_key.private_numbers().p
    q_prime=private_key.private_numbers().q
    N_public_modulus=public_key.public_numbers().n
    d_private_exponent=private_key.private_numbers().d
    e_public_exponent=65537
    g=find_g(p_prime,q_prime,N_public_modulus)
    v=987564
    pk=(N_public_modulus,g)
    sk=(e_public_exponent,d_private_exponent,v) 
    return pk,sk

def jj(pk,sk):
    random.seed(1955)
    s=random.getrandbits(16)
    a1=random.getrandbits(5)   
    N,g=pk
    e,d,v=sk

    

    m1="asdf"
    tag1=tagblock(sk,pk,m1,0)

    w_1=str(v)+str(0)
    h_w_1=int.from_bytes(h(w_1),byteorder='big')

    # gen proof

    T_proof=pow(tag1,a1,N)

    g_s=pow(g,s,N)

    rho=pow(g_s,a1*to_digit(m1),N)

    print(rho)

    #checkproof

    t=pow(T_proof,e,N)
    
    h_w1_a1=pow(h_w_1,a1,N)
    inv=pow(h_w1_a1,-1,N)
    t=pow(t*inv,1,N)

    t_s=pow(t,s,N)

    print(t_s)


def hash_number(number):
    # convert number to bytes
    # add 7 to avoid truncation
    number_bytes = number.to_bytes((number.bit_length() + 7) // 8, byteorder='big')

    digest = hashes.Hash(hashes.SHA256())
    digest.update(number_bytes)
    hashed_number = digest.finalize()

    return hashed_number
    





    # g_s=pow(g,s,N)

    # rho=pow(g_s,message,N)
    
    # tau=pow(message,e,N)
    # h_inv=pow(h_w_i,-1,N)
    # tau=pow(tau*h_inv,1, N)
    # rho_tonos=pow(tau,s,N)
    # print(message)
    # print(tau)
    # print(rho)
    # print(rho_tonos)



    # tagged_block=tagblock(sk,pk,block,1)
    # print("Original tag is:",tagged_block )


    # h_w_i=int.from_bytes(h(w_i),byteorder='big')
    # T=tagged_block
    # random.seed(1955)
    # s=random.getrandbits(16)
    # g=random.getrandbits(20)
    # g_s=pow(base=g, exp=s, mod=N)
    # try:
    #     rho=pow(base=g_s, exp=to_digit(block), mod=N)
    # except:
    #     print("could not compute")
    # try:
    #     tau=pow(T,e, N)
    # except:
    #     print("could not compute tau")

    # tau=pow(tau//h_w_i, 1,N)


    # try:
    #     rho_tonos=pow(tau, s, N)
    # except:
    #     print("could not compute")

    # print(rho_tonos )
    # print(rho)



pk,sk=rsa_key()
jj(pk,sk)

# number_of_blocks=18
# tagfile("d.txt",number_of_blocks,pk,sk)

# chal=gen_challenge(pk)
# V=gen_proof(pk,chal)
# check_proof(pk,sk,V,chal)