from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

def keygen(key_size):
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
    # print(public_key.public_numbers().n)

    p=private_key.private_numbers().p
    q=private_key.private_numbers().q
    N=public_key.public_numbers().n
    # print(int.from_bytes(os.urandom(16), byteorder='big'))
    return (N, p, q)

    
keygen(512)
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






