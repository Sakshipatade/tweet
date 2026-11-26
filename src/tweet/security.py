from pwdlib import PasswordHash # pwdlib is a Python library for password hashing and verification.
# PasswordHash is a class provided by this library.

passwordHash = PasswordHash.recommended()

def hashPassword(password:str)->str:
    return passwordHash.hash(password)

def verifyPassword(plain_password:str, hashedPassword:str) -> bool:
    return passwordHash.verify(hashedPassword, plain_password)