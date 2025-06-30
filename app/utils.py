import uuid
import secrets

def generate_league_code():
    """
    Generate a unique 8-character code for private leagues.
    Returns:
        str: Uppercase 8-character UUID substring.
    """
    return str(uuid.uuid4()).upper()[:8]

def generate_random_string(length=32):
    """
    Generate a random string for secrets or tokens.
    Args:
        length (int): Length of the string (default: 32).
    Returns:
        str: Random hexadecimal string.
    """
    return secrets.token_hex(length // 2)