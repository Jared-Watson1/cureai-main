import string
import random
import os
import mysql.connector
from dotenv import load_dotenv
from encryption import generate_salt, salt_to_base64, base64_to_salt, generate_key, encrypt, decrypt

load_dotenv()
systemKey = os.getenv("DECRYPT_PASSWORD")


#   Database queries and methods
def create_connection():
    print("Connecting ...")
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        # ssl_disabled=True
    )
    print("Connected")
    return connection
# print(create_connection())

# Add user with basic information (username, email, password, and salt)


def add_user_basic_info(username, email, password):
    connection = create_connection()
    cursor = connection.cursor()

    # Hash the password before storing it
    salt = generate_salt()
    salt_base64 = salt_to_base64(salt)  # Store the base64-encoded salt
    passwordEncrypted = encrypt(
        plaintext=password, password=systemKey, salt=salt)

    query = f"""INSERT INTO users (username, email, password_hash, salt)
                VALUES ('{username}', '{email}', '{passwordEncrypted}', '{salt_base64}')"""

    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()


# Add payment information for a user (card_number, card_expiration, security_code, name_on_card, billing_address, country_or_region)
def add_payment_info(username, card_number, card_expiration, security_code, name_on_card, billing_address, country_or_region):
    connection = create_connection()
    cursor = connection.cursor()

    # Get user info from the database
    user_info = get_user_info(username)
    print(user_info)
    if not user_info:
        print("User not found.")
        return

    salt_base64 = user_info["salt"]
    salt = base64_to_salt(salt_base64)

    # Encrypt payment information
    card_number_enc = encrypt(card_number, systemKey,
                              salt) if card_number else None
    card_expiration_enc = encrypt(
        card_expiration, systemKey, salt) if card_expiration else None
    security_code_enc = encrypt(
        security_code, systemKey, salt) if security_code else None
    name_on_card_enc = encrypt(
        name_on_card, systemKey, salt) if name_on_card else None
    billing_address_enc = encrypt(
        billing_address, systemKey, salt) if billing_address else None
    country_or_region_enc = encrypt(
        country_or_region, systemKey, salt) if country_or_region else None

    query = f"""UPDATE users SET
                card_number='{card_number_enc}',
                card_expiration='{card_expiration_enc}',
                security_code='{security_code_enc}',
                name_on_card='{name_on_card_enc}',
                billing_address='{billing_address_enc}',
                country_or_region='{country_or_region_enc}'
                WHERE username='{username}'"""

    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()


def create_users_table():
    connection = create_connection()
    cursor = connection.cursor()

    query = '''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        salt VARCHAR(255) NOT NULL,
        card_number VARCHAR(255),
        card_expiration VARCHAR(255),
        security_code VARCHAR(255),
        name_on_card VARCHAR(255),
        billing_address VARCHAR(255),
        country_or_region VARCHAR(255)
    );
    '''

    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()


def delete_all_users():
    connection = create_connection()
    cursor = connection.cursor()

    query = "DELETE FROM users"
    alter_query = "ALTER TABLE users AUTO_INCREMENT = 1"

    cursor.execute(query)
    cursor.execute(alter_query)
    connection.commit()
    cursor.close()
    connection.close()


# methods for data retrieval
def get_user_info(username):
    connection = create_connection()
    cursor = connection.cursor()

    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)

    user = cursor.fetchone()
    if not user:
        print("User not found.")
        return None

    user_id, username, email, password_hash, salt_base64, card_number_enc, card_expiration_enc, security_code_enc, name_on_card_enc, billing_address_enc, country_or_region_enc = user
    salt = base64_to_salt(salt_base64)

    # Decrypt the encrypted data
    card_number = decrypt(card_number_enc, systemKey,
                          salt) if card_number_enc else None
    card_expiration = decrypt(
        card_expiration_enc, systemKey, salt) if card_expiration_enc else None
    security_code = decrypt(security_code_enc, systemKey,
                            salt) if security_code_enc else None
    name_on_card = decrypt(name_on_card_enc, systemKey,
                           salt) if name_on_card_enc else None
    billing_address = decrypt(
        billing_address_enc, systemKey, salt) if billing_address_enc else None
    country_or_region = decrypt(
        country_or_region_enc, systemKey, salt) if country_or_region_enc else None
    password = decrypt(password_hash, systemKey, salt)
    # password = password_hash

    user_info = {
        "id": user_id,
        "username": username,
        "email": email,
        "password": password,
        "card_number": card_number,
        "card_expiration": card_expiration,
        "security_code": security_code,
        "name_on_card": name_on_card,
        "billing_address": billing_address,
        "country_or_region": country_or_region,
        'salt': salt_base64
    }

    cursor.close()
    connection.close()

    return user_info


# TESTING METHODS


def generate_card_number():
    return "".join([str(random.randint(0, 9)) for _ in range(16)])


def generate_security_code():
    return "".join([str(random.randint(0, 9)) for _ in range(3)])


def generate_expiration_date():
    month = str(random.randint(1, 12)).zfill(2)
    year = str(random.randint(23, 30)).zfill(2)
    return f"{month}/{year}"


def generate_billing_address(index):
    return f"{index} Example St"


def generate_country_or_region():
    countries = ["USA", "Canada", "UK", "Germany", "France",
                 "Spain", "Italy", "Australia", "Brazil", "Mexico"]
    return random.choice(countries)


def create_database():
    connection = create_connection()
    cursor = connection.cursor()

    query = f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')}"
    cursor.execute(query)

    connection.commit()
    cursor.close()
    connection.close()


def random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

# Generate 100 users and add them to the database


def generate_and_add_users(num_users):
    for i in range(num_users):
        print(i)
        username = f"user{i}"
        email = f"user{i}@example.com"
        password = random_string(10)

        # Add basic user information
        add_user_basic_info(username, email, password)

        # Generate payment information
        card_number = generate_card_number()
        card_expiration = generate_expiration_date()
        security_code = generate_security_code()
        name_on_card = f"User {i}"
        billing_address = generate_billing_address(i)
        country_or_region = generate_country_or_region()

        # Add payment information for the user
        add_payment_info(username, card_number, card_expiration,
                         security_code, name_on_card, billing_address, country_or_region)

print(get_user_info('admin'))