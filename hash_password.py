#!/usr/bin/env python3
"""Generate hashed username + password for ALLOWED_USERS. Nothing readable is printed.
Run: python hash_password.py <username> <password>
Output: JSON with username_hash (SHA-256) and password_hash (bcrypt) for your env."""
import sys
import json
import hashlib
import bcrypt

def main():
    if len(sys.argv) < 3:
        print("Usage: python hash_password.py <username> <password>")
        print("Output: JSON entry (hashed only) to add to ALLOWED_USERS env.")
        sys.exit(1)
    username = sys.argv[1]
    password = sys.argv[2]
    username_hash = hashlib.sha256(username.encode("utf-8")).hexdigest()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")
    entry = {"username_hash": username_hash, "password_hash": password_hash}
    print(json.dumps(entry))
    print("\nAdd this to ALLOWED_USERS env (JSON array). No username or password is stored in plain text.")

if __name__ == "__main__":
    main()
