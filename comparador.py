from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Palavras comuns que não ajudam a comparar (artigos, preposições etc.)
STOPWORDS = {
    "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas", "por", "para",
    "com", "sem", "sobre", "entre", "até", "ao", "aos", "as", "os", "um", "uma",
    "uns", "umas", "ou", "que", "se", "como", "mais", "muito", "ser", "ter", "tem",
    "foi", "são", "há", "já", "não", "sua", "seu", "suas", "seus", "meu", "minha",
    "este", "esta", "isso", "isto", "também", "procuro", "busco",
}


def carregar_curriculos(pasta="curriculos"):
    """Lê todos os .txt da pasta e devolve {nome: texto}."""
    curriculos = {}
    for arquivo in Path(pasta).glob("*.txt"):
        curriculos[arquivo.stem] = arquivo.read_text(encoding="utf-8")
    return curriculos


def comparar(vaga, curriculos):
    """Devolve lista de (chave, pontuação) ordenada do melhor pro pior."""
    chaves = list(curriculos.keys())
    textos = [vaga] + [curriculos[k] for k in chaves]

    vetorizador = TfidfVectorizer(stop_words=list(STOPWORDS))
    matriz = vetorizador.fit_transform(textos)

    scores = cosine_similarity(matriz[0:1], matriz[1:])[0]

    resultado = sorted(zip(chaves, scores), key=lambda x: x[1], reverse=True)
    return [(chave, round(float(s) * 100, 1)) for chave, s in resultado]


def palavras_em_comum(vaga, texto, limite=12):
    """Palavras da vaga que também aparecem no currículo."""
    analisador = TfidfVectorizer().build_analyzer()
    palavras_texto = set(analisador(texto))

    vistas, resultado = set(), []
    for palavra in analisador(vaga):
        if palavra in STOPWORDS or palavra in vistas:
            continue
        vistas.add(palavra)
        if palavra in palavras_texto:
            resultado.append(palavra)
    return resultado[:limite]