from fastapi import FastAPI, Response
import random
import kai
from sqlalchemy import create_engine, text
from database import DATABASE_URL  # importa do seu database.py
from supabase import create_client, Client
import os

app = FastAPI()

engine = create_engine(DATABASE_URL)
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.get("/", response_model=str)
def read_root():
    return "Bem-vindo à API! Tudo funcionando por aqui! 🚀"

@app.get("/supah")
def test_supabase():
    try:
        # Exemplo: listar registros da tabela "usuarios"
        response = supabase.table("archetypes").select("*").limit(1).execute()
        return {"status": "ok", "data": response.data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
        
@app.get("/testdb")
def test_db_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return {"success": True, "result": result.scalar()}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/generate-deck", response_class=Response)
def generate_deck():
    mode = random.choice([1, 2, 3])
    content = kai.mode_select(mode)
    return Response(content=content, media_type="text/plain")
