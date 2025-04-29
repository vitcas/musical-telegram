from dotenv import load_dotenv
import os

# Determina qual arquivo .env carregar (local ou produção)
env = os.getenv("ENVIRONMENT", "dev")  # Default é "local"
env_file = f".env.{env}"

# Carrega o arquivo .env correto
load_dotenv(env_file)

USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Se estiver no ambiente local, não precisa de SSL
if env == "dev":
    DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
else:
    # Para o ambiente de produção (Supabase), SSL é obrigatório
    DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

# Cria conexão assíncrona
#database = Database(DATABASE_URL)
