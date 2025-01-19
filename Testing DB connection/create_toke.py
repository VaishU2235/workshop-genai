from secrets import token_bytes
from base64 import b64encode

# Generate a 32-byte (256-bit) random key
secret_key = token_bytes(32)
# Convert to base64 for easier storage
secret_key_b64 = b64encode(secret_key).decode('utf-8')

print(f"Generated secret key: {secret_key_b64}")