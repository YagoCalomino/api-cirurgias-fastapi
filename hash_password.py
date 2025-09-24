# hash_password.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# Altere a senha aqui para o que você quiser
senha_plana = "minhasenha123"
senha_hashed = get_password_hash(senha_plana)

print(f"Sua senha plana é: {senha_plana}")
print(f"Seu hash para o banco de dados é: {senha_hashed}")