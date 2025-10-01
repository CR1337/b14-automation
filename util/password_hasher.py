import hashlib
from getpass import getpass


def hash_password(password: str) -> str:
    hashed = hashlib.sha256(password.encode()).hexdigest()
    del password
    return hashed


def main():
    password = getpass("Enter password >")
    hashed = hash_password(password)
    del password
    print(hashed)


if __name__ == "__main__":
    main()
