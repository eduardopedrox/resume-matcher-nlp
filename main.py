import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pypdf import PdfReader

from database import SessionLocal, Candidato
from comparador import comparar

app = FastAPI(title="Banco de Talentos")


def ler_pdf(conteudo: bytes) -> str:
    leitor = PdfReader(io.BytesIO(conteudo))
    return "\n".join((pagina.extract_text() or "") for pagina in leitor.pages).strip()


@app.post("/candidatos")
async def cadastrar(
    nome: str = Form(...),
    email: str = Form(...),
    telefone: str = Form(""),
    cidade: str = Form(""),
    area: str = Form(""),
    curriculo: UploadFile = File(...),
):
    if not curriculo.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Envie o currículo em PDF.")

    texto = ler_pdf(await curriculo.read())
    if not texto:
        raise HTTPException(400, "Não consegui ler texto desse PDF (pode ser imagem escaneada).")

    db = SessionLocal()
    try:
        candidato = Candidato(
            nome=nome, email=email, telefone=telefone,
            cidade=cidade, area=area, texto_curriculo=texto,
        )
        db.add(candidato)
        db.commit()
        return {"id": candidato.id, "mensagem": "Cadastro realizado!"}
    finally:
        db.close()


@app.post("/ranking")
def ranking(vaga: str = Form(...)):
    db = SessionLocal()
    try:
        candidatos = db.query(Candidato).all()
        if not candidatos:
            return []

        por_id = {c.id: c for c in candidatos}
        textos = {c.id: c.texto_curriculo for c in candidatos}
        resultado = comparar(vaga, textos)  # usa o cosseno do comparador.py

        return [
            {
                "id": i,
                "nome": por_id[i].nome,
                "area": por_id[i].area,
                "cidade": por_id[i].cidade,
                "email": por_id[i].email,
                "score": score,
            }
            for i, score in resultado
        ]
    finally:
        db.close()