from base64 import b64encode, b64decode
import hashlib, os, base64
from Cryptodome.Cipher import AES
from dotenv import load_dotenv
load_dotenv()

systemKey = os.getenv("DECRYPT_PASSWORD")

def generate_salt():
    return os.urandom(16)

# first encode salt to base64 to be stored
def salt_to_base64(salt):
    return base64.b64encode(salt).decode('utf-8')

# when salt is needed decode it from base64 to salt
def base64_to_salt(base64_salt):
    return base64.b64decode(base64_salt.encode('utf-8'))

# Generate a key derived from the given password and salt.
# This key is used for both encryption and decryption.
# password: The user's password (str)
# salt: A random sequence of bytes used for generating the key (bytes)
# iterations: The number of iterations for the key derivation function (int)
def generate_key(password, salt, iterations=100000):
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
    return key

# Encrypt the given plaintext using AES-GCM with a password and salt.
# plaintext: The data to be encrypted (str)
# password: The user's password (str)
# salt: A random sequence of bytes used for generating the key (bytes)
def encrypt(plaintext, password, salt):
    key = generate_key(password, salt)
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
    # Return a base64-encoded string containing the nonce, tag, and ciphertext
    return b64encode(cipher.nonce + tag + ciphertext).decode()

# Decrypt the given encrypted data using AES-GCM with a password and salt.
# enc_data: The base64-encoded encrypted data (str)
# password: The user's password (str)
# salt: A random sequence of bytes used for generating the key (bytes)
def decrypt(enc_data, password, salt):
    enc_data = b64decode(enc_data)
    # Separate the nonce, tag, and ciphertext from the encoded data
    nonce, tag, ciphertext = enc_data[:16], enc_data[16:32], enc_data[32:]
    
    key = generate_key(password, salt)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    # Decrypt and verify the ciphertext and tag, then return the plaintext
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext.decode()

# if __name__ == '__main__':
#     secrete_key = os.getenv("SECRET_KEY")
#     salt = generate_salt()
#     password = "example-password123"
#     encryped = encrypt(password, secrete_key, salt)
#     print(encryped)
#     decrypted = decrypt(encryped, secrete_key, salt)
#     print(decrypted)