import time
from Crypto.Cipher import DES, AES
from Crypto.Random import get_random_bytes
import os
import random
import string
import sys

# ! Generate usable data for encryption
def create_random_text_file(filename, sizeMb):
    size_in_bytes = sizeMb * 1024 * 1024
    with open(filename, 'w') as f:
        while os.path.getsize(filename) < size_in_bytes:
            random_text = ''.join(random.choices(string.ascii_letters + string.digits, k=1024))
            f.write(random_text + '\n')

filename = "10mb_file.txt"
create_random_text_file(filename, 30)
print(f"{filename} created.")

# ! This version of the code generates data to be encrypted
def compareSpeed(algorithm, mode, keySize, dataSize):
    data = get_random_bytes(dataSize)
    if algorithm == "DES":
        key = get_random_bytes(8)
        cipher = DES.new(key, mode)
    elif algorithm == "AES":
        key = get_random_bytes(keySize)
        cipher = AES.new(key, mode)
    
    start_time = time.time()
    cipher.encrypt(data)
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    speed = dataSize / elapsed_time
    return speed

dataSize = 10 * 1024 * 1024 
mode = AES.MODE_CBC                      # ! CBC Mode specified

# ! Test DES
desSpeed = compareSpeed("DES", DES.MODE_CBC, 8, dataSize)
print(f"\nDES speed: {desSpeed:.2f} bytes/second\n", file=sys.stderr)

# ! Test AES
aes128Speed = compareSpeed("AES", AES.MODE_CBC, 16, dataSize)
print(f"AES-128 speed: {aes128Speed:.2f} bytes/second", file=sys.stderr)

aes192Speed = compareSpeed("AES", AES.MODE_CBC, 24, dataSize)
print(f"AES-192 speed: {aes192Speed:.2f} bytes/second", file=sys.stderr)

aes256Speed = compareSpeed("AES", AES.MODE_CBC, 32, dataSize)
print(f"AES-256 speed: {aes256Speed:.2f} bytes/second\n", file=sys.stderr)


# ! This version of the function takes a specified input and output file for the encryption.
def encryptFile(algorithm, mode, keySize):
    key = get_random_bytes(keySize)
    iv = get_random_bytes(16) if algorithm == "AES" else get_random_bytes(8)
    
    if algorithm == "DES":
        cipher = DES.new(key, mode, iv)
    elif algorithm == "AES":
        cipher = AES.new(key, mode, iv)

    sys.stdout.buffer.write(iv)

    start_time = time.time()
    total_bytes = 0

    while True:
        chunk = sys.stdin.buffer.read(8192)
        if len(chunk) == 0:
            break
        total_bytes += len(chunk) 
        if len(chunk) % AES.block_size != 0:
            chunk += b' ' * (AES.block_size - len(chunk) % AES.block_size)
        sys.stdout.buffer.write(cipher.encrypt(chunk))

    end_time = time.time() 

    elapsed_time = end_time - start_time
    speed = total_bytes / elapsed_time if elapsed_time > 0 else 0

    print(f"Encryption with stdin and stdout completed in {elapsed_time:.2f} seconds.", file=sys.stderr)
    print(f"Speed: {speed:.2f} bytes/second.\n", file=sys.stderr)

encryptFile("AES", AES.MODE_CBC, 16)        # ! CBC mode specified


