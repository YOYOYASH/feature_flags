import secrets
import bcrypt
import hashlib
import hmac


def generate_api_key() -> str:
    api_key =  secrets.token_hex(32)
    return api_key

def hash_password(password):
    """
    Hash a password using bcrypt.
    
    Args:
        password (str): The password to hash
    
    Returns:
        str: The hashed password (as a string)
    """
    # Convert password to bytes and generate a salt
    password_bytes = password.encode('utf-8')
    
    # Generate a salt and hash the password
    # Default work factor is 12, which is a good balance between security and performance
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    
    # Convert to string for easy storage
    return hashed.decode('utf-8')


def verify_password(stored_password, provided_password):
    """
    Verify a stored password against one provided by user.
    
    Args:
        stored_password (str): The previously hashed password
        provided_password (str): The password to check
    
    Returns:
        bool: True if password is correct, False otherwise
    """
    # Convert inputs to bytes
    stored_bytes = stored_password.encode('utf-8')
    provided_bytes = provided_password.encode('utf-8')
    
    # Check the password
    return bcrypt.checkpw(provided_bytes, stored_bytes)


def hash_api_key(api_key:str) -> str:
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    return api_key_hash

def verify_api_key(hashed_key:str,stored_key:str) -> bool:
    incoming_key_hash = hashlib.sha256(hashed_key.encode()).hexdigest()
    return hmac.compare_digest(incoming_key_hash,stored_key)

