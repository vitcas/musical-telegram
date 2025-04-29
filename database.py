import os
#from dotenv import load_dotenv

#load_dotenv()  # Carrega variáveis do arquivo .env

USER = os.environ.get("USER")
PASSWORD = os.environ.get("PASSWORD")
HOST = os.environ.get("HOST")
PORT = os.environ.get("PORT")
DBNAME = os.environ.get("DBNAME")

DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"
