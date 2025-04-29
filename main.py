from fastapi import FastAPI, Response
import random
import kai
from sqlalchemy import create_engine, text
from database import DATABASE_URL  # importa do seu database.py

app = FastAPI()

engine = create_engine(DATABASE_URL)

@app.get("/", response_model=str)
def read_root():
    return "Bem-vindo à API! Tudo funcionando por aqui! 🚀"

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
