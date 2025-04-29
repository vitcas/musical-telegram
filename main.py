from fastapi import FastAPI, Response
import random
import kai

app = FastAPI()

@app.get("/", response_model=str)
def read_root():
    return "Bem-vindo à API! Tudo funcionando por aqui! 🚀"

@app.get("/generate-deck", response_class=Response)
def generate_deck():
    mode = random.choice([1, 2, 3])
    content = kai.mode_select(mode)
    return Response(content=content, media_type="text/plain")
