import streamlit as st
from comparador import carregar_curriculos, comparar

st.set_page_config(page_title="Comparador de Currículos", page_icon="📄", layout="centered")

st.title("📄 Comparador de Currículos")
st.caption("Cole a descrição da vaga e veja os currículos ordenados por compatibilidade.")

vaga = st.text_area("Descrição da vaga", height=180, placeholder="Ex: Procuro desenvolvedor Python com experiência em dados e SQL")

if st.button("Comparar", type="primary"):
    if not vaga.strip():
        st.warning("Cole a descrição da vaga antes de comparar.")
    else:
        curriculos = carregar_curriculos()
        ranking = comparar(vaga, curriculos)

        st.subheader("Ranking")
        for posicao, (nome, score) in enumerate(ranking, start=1):
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                col1.markdown(f"**{posicao}º  {nome.capitalize()}**")
                col2.metric("Compatibilidade", f"{score}%")
                st.progress(min(int(score), 100))
                with st.expander("Ver currículo"):
                    st.write(curriculos[nome])