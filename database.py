import os
#from dotenv import load_dotenv

#load_dotenv()  # Carrega variáveis do arquivo .env

USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DBNAME = os.getenv("DBNAME")

print("DB VARS:", USER, PASSWORD, HOST, PORT, DBNAME)

DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"
