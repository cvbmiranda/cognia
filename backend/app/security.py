import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    raise ValueError("FALHA CRÍTICA: ENCRYPTION_KEY não encontrada no ambiente. O sistema não pode operar dados sensíveis.")

# Inicializa o motor de criptografia
fernet = Fernet(ENCRYPTION_KEY.encode())

def encrypt_text(text: str | None) -> str | None:
    """Recebe um texto em claro e devolve a string criptografada."""
    if not text:
        return None
    # O Fernet trabalha com bytes, então precisamos codificar para utf-8 e depois decodificar para salvar no banco como string
    return fernet.encrypt(text.encode('utf-8')).decode('utf-8')

def decrypt_text(encrypted_text: str | None) -> str | None:
    """Recebe o texto criptografado do banco e devolve em claro."""
    if not encrypted_text:
        return None
    return fernet.decrypt(encrypted_text.encode('utf-8')).decode('utf-8')