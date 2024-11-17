import os
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do arquivo .env

class Config:
    """Configurações do aplicativo."""
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "default_secret_key")
    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "3364"),
        "database": os.getenv("DB_NAME", "controle_financeiro"),
    }
