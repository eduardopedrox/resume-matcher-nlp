import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from pypdf import PdfReader

from database import SessionLocal, Candidato
from comparador import comparar, palavras_em_comum

app = FastAPI(title="TalentMatch")


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
def ranking(
    vaga: str = Form(...),
    area: str = Form(""),
    cidade: str = Form(""),
    limite: int = Form(0),
):
    db = SessionLocal()
    try:
        candidatos = db.query(Candidato).all()

        # filtros (ignoram maiúsculas/minúsculas)
        if area.strip():
            candidatos = [c for c in candidatos if area.strip().lower() in (c.area or "").lower()]
        if cidade.strip():
            candidatos = [c for c in candidatos if cidade.strip().lower() in (c.cidade or "").lower()]

        if not candidatos:
            return []

        por_id = {c.id: c for c in candidatos}
        textos = {c.id: c.texto_curriculo for c in candidatos}
        resultado = comparar(vaga, textos)  # cosseno

        if limite > 0:
            resultado = resultado[:limite]

        return [
            {
                "id": i,
                "nome": por_id[i].nome,
                "area": por_id[i].area,
                "cidade": por_id[i].cidade,
                "email": por_id[i].email,
                "telefone": por_id[i].telefone,
                "score": score,
                "palavras": palavras_em_comum(vaga, por_id[i].texto_curriculo),
                "trecho": por_id[i].texto_curriculo[:500],
            }
            for i, score in resultado
        ]
    finally:
        db.close()

@app.get("/candidatos")
def listar():
    db = SessionLocal()
    try:
        candidatos = db.query(Candidato).order_by(Candidato.criado_em.desc()).all()
        return [
            {
                "id": c.id,
                "nome": c.nome,
                "email": c.email,
                "telefone": c.telefone,
                "cidade": c.cidade,
                "area": c.area,
                "criado_em": c.criado_em.strftime("%d/%m/%Y"),
            }
            for c in candidatos
        ]
    finally:
        db.close()


@app.delete("/candidatos/{candidato_id}")
def excluir(candidato_id: int):
    db = SessionLocal()
    try:
        candidato = db.get(Candidato, candidato_id)
        if not candidato:
            raise HTTPException(404, "Candidato não encontrado.")
        db.delete(candidato)
        db.commit()
        return {"mensagem": "Candidato excluído."}
    finally:
        db.close()

app.mount("/", StaticFiles(directory="static", html=True), name="static")