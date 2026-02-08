#!/usr/bin/env python3
"""Generate bcrypt password hashes for ALLOWED_USERS. Run: python hash_password.py <username> <password>"""
import sys
import json
import bcrypt

def main():
    if len(sys.argv) < 3:
        print("Usage: python hash_password.py <username> <password>")
        print("Output: JSON entry to add to ALLOWED_USERS env (array of such objects).")
        sys.exit(1)
    username = sys.argv[1]
    password = sys.argv[2]
    h = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")
    entry = {"username": username, "password_hash": h}
    print(json.dumps(entry))
    print("\nAdd to ALLOWED_USERS env as JSON array, e.g.:")
    print("ALLOWED_USERS=[{\"username\":\"" + username + "\",\"password_hash\":\"" + h + "\"}]")

if __name__ == "__main__":
    main()
