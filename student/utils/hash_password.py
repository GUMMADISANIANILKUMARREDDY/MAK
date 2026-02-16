"""Run: python -m utils.hash_password
   Use output to insert users in Supabase."""
import bcrypt

if __name__ == "__main__":
    password = input("Enter password to hash: ")
    pwd_bytes = password.encode("utf-8")[:72]
    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode("utf-8")
    print(f"Hashed password: {hashed}")
