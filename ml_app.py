import streamlit as st
import requests
import base64
import hashlib
import os
import urllib.parse

# ==========================
# CONFIG MERCADO LIVRE (App Público)
# ==========================
CLIENT_ID = "8611967944426259"
REDIRECT_URI = "https://ml-anuncios-r37onkxuojbhs8ht5mwb8f.streamlit.app"
AUTH_URL = "https://auth.mercadolivre.com.br/authorization"
TOKEN_URL = "https://api.mercadolibre.com/oauth/token"

st.set_page_config(page_title="ML PKCE Login", layout="centered")
st.title("🔐 Login Mercado Livre PKCE (App Público)")

# ==========================
# FUNÇÃO PARA GERAR PKCE
# ==========================
def generate_pkce():
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8").rstrip("=")
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode("utf-8")).digest()
    ).decode("utf-8").rstrip("=")
    return code_verifier, code_challenge

# ==========================
# GERAR PKCE UMA ÚNICA VEZ POR SESSÃO
# ==========================
if "code_verifier" not in st.session_state:
    st.session_state.code_verifier, st.session_state.code_challenge = generate_pkce()

# ==========================
# BOTÃO LOGIN
# ==========================
auth_link = (
    f"{AUTH_URL}?response_type=code"
    f"&client_id={CLIENT_ID}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    f"&code_challenge={st.session_state.code_challenge}"
    f"&code_challenge_method=S256"
)

st.markdown(f"[👉 Clique aqui para LOGIN no Mercado Livre]({auth_link})")

# ==========================
# CAPTURA CODE NA URL
# ==========================
query_params = st.experimental_get_query_params()
if "code" in query_params:
    code = query_params["code"][0]
    st.success("Código recebido!")
    st.write(code)

    payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "code": code,
        "code_verifier": st.session_state.code_verifier
    }

    st.write("📨 Enviando para o Mercado Livre...")
    st.json(payload)

    try:
        response = requests.post(TOKEN_URL, data=payload, headers={"Accept": "application/json"})
        data = response.json()
        st.write("📦 Resposta da API")
        st.json(data)

        if "access_token" in data:
            st.success("🎉 LOGIN OK — TOKEN GERADO!")
            st.session_state["token"] = data
        else:
            st.error("❌ Não foi possível gerar o token. Confira a URL de retorno e tente novamente.")
    except Exception as e:
        st.error(f"❌ Erro ao conectar na API: {e}")
