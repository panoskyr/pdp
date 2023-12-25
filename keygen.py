from cryptography.hazmat.primitives.asymmetric import rsa,utils
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
import random
from sympy import isprime
import string
import lorem
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
    try:
        digest=hashes.Hash(hashes.SHA256)
        digest.update(bytes(message))
        return digest.finalize()

    except:
        "Could not digest message"


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
            f.write(lorem.text()+"\n")
def to_digit(s):
    return int(''.join(map(str,map(ord,s))))  
  
def tagfile(file_to_tag,number_of_blocks,sk,pk):
    # use read bytes to capture all characters
    with open(file_to_tag, "r") as file:
        data=file.read()
    block_size=len(data) // number_of_blocks
    for block_num in range(number_of_blocks):
        start_idx=block_num*block_size
        # if we are at the last block go to the end of the file.
        end_idx=start_idx+block_size if block_num <number_of_blocks-1 else len(file_to_tag)

        tagblock(sk,pk,data[start_idx:end_idx], block_num)

def tagblock(sk,pk,block,i):
    # T_i=(h(w_i) * g ^ block)^ d modn
    # T_i =( (h(w_i)^d ) modn * (g^(block*d)) modn ) modn 
    # the last modn brings it back to [0,N-1]

    w_i=bytes(str(sk[2])+str(i), "utf-8")
    g=pk[1]
    d=sk[1]
    N=pk[0]
    g_comp=pow(base=g,exp=(to_digit(block)*d),mod=N)
    w_comp=pow(base=h(w_i),exp=d, mod=N)
    tag=pow(w_comp*g_comp,1 ,N)
    print(tag)
    

    
pk,sk=get_keys()
tagfile("random_text.txt",200,sk,pk)  
