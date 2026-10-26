from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def carregar_curriculos(pasta="curriculos"):
    """Lê todos os .txt da pasta e devolve {nome: texto}."""
    curriculos = {}
    for arquivo in Path(pasta).glob("*.txt"):
        curriculos[arquivo.stem] = arquivo.read_text(encoding="utf-8")
    return curriculos


def comparar(vaga, curriculos):
    """Devolve lista de (nome, pontuação) ordenada do melhor pro pior."""
    nomes = list(curriculos.keys())
    textos = [vaga] + [curriculos[n] for n in nomes]

    vetorizador = TfidfVectorizer()
    matriz = vetorizador.fit_transform(textos)

    scores = cosine_similarity(matriz[0:1], matriz[1:])[0]

    resultado = sorted(zip(nomes, scores), key=lambda x: x[1], reverse=True)
    return [(nome, round(float(s) * 100, 1)) for nome, s in resultado]


if __name__ == "__main__":
    vaga = "Procuro desenvolvedor Python com experiência em dados e SQL"
    curriculos = carregar_curriculos()
    for nome, score in comparar(vaga, curriculos):
        print(f"{nome}: {score}%")