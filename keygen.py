from cryptography.hazmat.primitives.asymmetric import rsa,utils
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.hashes import SHA256
import random
from sympy import isprime
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
    return SHA256(message)



def find_e():
    while True:
        N_public_modulus,p,q,d_private_exponent, pq_tonos= rsa_keygen(512)
        try :
            e=pow(d_private_exponent,-1, pq_tonos)
            if isprime(e):
                g=find_g(p,q,N_public_modulus)
                v=83764532362
                print( "Found")
                #end loop when suitable e is found
                break
        # raised when it is not invertible
        except ValueError:
            continue
        
find_e()



    




