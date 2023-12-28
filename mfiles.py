import sys
import secrets
import string
def create_text_file(num_bytes):
    file_name = f"{num_bytes}_bytes.txt"
    data = generate_random_string(num_bytes)

    with open(file_name, "w", encoding="utf-8") as file:
        file.write(data)

def generate_random_string(num_bytes):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(num_bytes))


create_text_file(100)
create_text_file(1000)
create_text_file(10000)
create_text_file(100000)
create_text_file(1000000)
