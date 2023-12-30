from cryptography.hazmat.primitives.asymmetric import rsa,utils
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
import random
from sympy import isprime
import os
class E_PDP():
    """
    A lighter class of the PDP. It does not use coefficients for each different challenge,
    practically the coefficients are just one for every block
    Now, the possession of the sum is guaranteed instead of every block separately.
    """

    def __init__(self,filepath="d.txt",tagspath="tags.txt",key_size=512):
        self.key_size=key_size
        self.filepath=filepath
        self.tagspath=tagspath


    def rsa_key(self):
        private_key=rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.key_size
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
        g=self.find_g(p_prime,q_prime,N_public_modulus)
        v=random.getrandbits(128)
        pk=(N_public_modulus,g)
        sk=(e_public_exponent,d_private_exponent,v) 
        keysfilepath=self.get_keysfilename()
        self.write_pk_sk_to_file(keysfilepath,pk,sk)
        return pk,sk
    
    def get_keysfilename(self):
        filename, extension=os.path.splitext(self.filepath)
        keysfilename=filename+"_keys"+extension
        return keysfilename
    
    def is_ok_number(self,a, p, q):
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


    def find_a(self,p,q,N,upto=1000):
        for _ in range(upto):
            a=random.randrange(1,N+1)
            if (self.is_ok_number(a,p=p,q=q) ):
                return a 
        return -1

    def find_g(self,p,q,N):
        a=self.find_a(p,q,N)
        if a!=-1:
            return a^2
        else:
            return "No g found"
        
    
    def h(self,message):
        digest=hashes.Hash(hashes.SHA256())
        digest.update(message.encode('utf-8'))
        return digest.finalize()
    
    def to_digit(self,s):
        return int(''.join(map(str,map(ord,s))))  
  
    def tagfile(self,file_to_tag,number_of_blocks,pk,sk):
        self.filepath=file_to_tag
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
            tag=self.tagblock(sk,pk, block, block_num)
            tags.append(tag)
            block_nums.append(block_num)

            with open(self.tagspath, "w") as f:
                for block_num, tag in zip(block_nums, tags):
                    f.write(f"{block_num}:{tag}\n")

    def get_num_of_blocks(self,tagsfilepath):
        with open(tagsfilepath, "rb") as f:
            num_of_blocks=sum(1 for _ in f)
        return num_of_blocks


    def gen_challenge(self,pk,num_of_chals):
        N,g=pk
        num_of_blocks=self.get_num_of_blocks(self.tagspath)


        c=num_of_chals
        assert c <= num_of_blocks
        assert c>0
        indices_of_blocks=random.sample(range(num_of_blocks),c)

        # s is generated per challenge
        s=random.getrandbits(16)

        return indices_of_blocks,s


    def get_blocks(self,filepath,tagspath):

        num_of_blocks=self.get_num_of_blocks(tagspath)
        blocks=[]

        with open(filepath, "r") as file:
            data=file.read()

        block_size=len(data) // num_of_blocks
        # print("block_size is ", block_size)


        for block_num in range(num_of_blocks):
            start_idx=block_num*block_size
            # if we are at the last block go to the end of the file.
            end_idx=start_idx+block_size if block_num <num_of_blocks-1 else start_idx+len(filepath)
            block=data[start_idx:end_idx]
            blocks.append(block)
        return blocks

    def get_tags(self,tagspath):
        tags=[]
        with open(tagspath) as f:
            for line in f:
                block_num, tag=line.strip().split(sep=':')
                block_num=int(block_num)
                tags.append(int(tag))
        return tags


    def gen_proof(self,pk,chal):
        indices_of_blocks,s=chal
        N,g=pk
        


        blocks=self.get_blocks(self.filepath,self.tagspath)

        tags=self.get_tags(self.tagspath)

        
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
            tmp=pow(g_s,self.to_digit(block),N)
            g_prod=pow(g_prod*tmp,1,N)
        rho=self.hash_number(g_prod)
        # print(rho)
        return (T,rho)

    def check_proof(self,pk,sk,V,chal):
        indices_of_blocks,s=chal
        N,g=pk
        e,d,v=sk
        T,rho=V

        # t= T^e modN and ed congruent 1 modN
        t=pow(T,e,N)


        for i in indices_of_blocks:
            w_i=str(v)+str(i)
            h_w_i=int.from_bytes(self.h(w_i),byteorder='big')
            h_inv=pow(h_w_i,-1,N)

            t=pow(t*h_inv,1,N)
        
        t_s=pow(t,s,N)

        rho=self.hash_number(t_s)

        # print(rho)


    def tagblock(self,sk,pk,block,i):
        # T_i=(h(w_i) * g ^ block)^ d modn
        # T_i =( (h(w_i)^d ) modn * (g^(block*d)) modn ) modn 
        # the last modn brings it back to [0,N-1]

        w_i=str(sk[2])+str(i)
        g=pk[1]
        d=sk[1]
        N=pk[0]
        g_comp=pow(base=g,exp=(self.to_digit(block)*d),mod=N)
        w_comp=pow(base=int.from_bytes(self.h(w_i),byteorder='big'),exp=d, mod=N)
        tag=pow(w_comp*g_comp,1 ,N)
        # print (tag)
        return tag
    
    def hash_number(self,number):
        # convert number to bytes
        # add 7 to avoid truncation
        number_bytes = number.to_bytes((number.bit_length() + 7) // 8, byteorder='big')

        digest = hashes.Hash(hashes.SHA256())
        digest.update(number_bytes)
        hashed_number = digest.finalize()

        return hashed_number
    
    def write_pk_sk_to_file(self,keysfile,pk,sk):
        with open(keysfile, "w") as file:
            N_public_modulus,g=pk
            e_public_exponent,d_private_exponent,v=sk
            file.write(f"N_public_modulus={N_public_modulus}\n")
            file.write(f"d_private_exponent={d_private_exponent}\n")
            file.write(f"e_public_exponent={e_public_exponent}\n")
            file.write(f"g={g}\n")
            file.write(f"v={v}\n")
            file.write(f"pk={pk}\n")
            file.write(f"sk={sk}\n")
        

        
    
# pdp=Public_PDP()

# pk, sk=pdp.rsa_key()
# number_of_blocks=20
# pdp.tagfile("as.txt",number_of_blocks,pk,sk)
# chal=pdp.gen_challenge(pk,1)
# V=pdp.gen_proof(pk,chal)
# pdp.check_proof(pk,sk,V,chal)


def test(filepath,key_size, number_of_blocks, number_of_chals):
    # number of vhallenges must be less than number of blocks
    pdp=E_PDP(filepath=filepath,key_size=key_size)
    pk, sk=pdp.rsa_key()
    pdp.tagfile(filepath,number_of_blocks,pk,sk)
    chal=pdp.gen_challenge(pk,number_of_chals)
    V=pdp.gen_proof(pk,chal)
    pdp.check_proof(pk,sk,V,chal)


test("fs/100000_bytes.txt", 512, 60,50)