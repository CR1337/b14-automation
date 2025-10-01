import hashlib
from getpass import getpass


def hash_password(password: str) -> str:
    hashed = hashlib.sha256(password.encode()).hexdigest()
    del password
    return hashed


def main():
    password = getpass("Enter password >")
    password_2 = getpass("Reenter password >")
    if password != password_2:
        print("Passwords do not match!")
        return
    hashed = hash_password(password)
    del password
    print(hashed)


if __name__ == "__main__":
    main()
