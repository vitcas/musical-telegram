import os
#from dotenv import load_dotenv

#load_dotenv()  # Carrega variáveis do arquivo .env

USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
DB_PORT = os.getenv("DB_PORT")
DBNAME = os.getenv("DBNAME")

#DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{DB_PORT}/{DBNAME}?sslmode=require"
DATABASE_URL = f"postgresql://postgres.oludipbtxguatsdhgkba:{PASSWORD}@aws-0-sa-east-1.pooler.supabase.com:5432/postgres"
