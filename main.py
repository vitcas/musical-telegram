from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse
import random
import kai  # certifique-se de que kai.py está junto no repositório

app = FastAPI()

@app.get("/", response_class=PlainTextResponse)
def generate_deck():
    mode = random.choice([1, 2, 3])
    content = kai.mode_select(mode)
    return content

# para Vercel funcionar
# cria uma variável chamada "handler"
from mangum import Mangum
handler = Mangum(app)
