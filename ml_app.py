import streamlit as st
import secrets
import hashlib
import base64
import requests
import urllib.parse

# ======================================
# CONFIG MERCADO LIVRE
# ======================================
CLIENT_ID = "8611967944426259"
CLIENT_SECRET = "EBXpqfZLRgKC6e71BYRtKtsmD1zEXXZg"
REDIRECT_URI = "https://ml-anuncios-r37onkxuojbhs8ht5mwb8f.streamlit.app"

st.set_page_config(page_title="ML Login", page_icon="🛒")

st.title("🔐 Login Mercado Livre com PKCE")


# ======================================
# PKCE FIXO NA SESSÃO
# ======================================
if "pkce_generated" not in st.session_state:
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).rstrip(b"=").decode()

    st.session_state.code_verifier = verifier
    st.session_state.code_challenge = challenge
    st.session_state.pkce_generated = True


# ======================================
# LINK DE AUTORIZAÇÃO
# ======================================
auth_url = (
    "https://auth.mercadolibre.com/authorization?"
    f"response_type=code&client_id={CLIENT_ID}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    f"&code_challenge={st.session_state.code_challenge}"
    f"&code_challenge_method=S256"
)

st.markdown(f"👉 [Clique aqui para fazer login no Mercado Livre]({auth_url})")

st.info("Após o login você será redirecionado de volta aqui com ?code=.")


# ======================================
# RECUPERA O CODE DO RETORNO
# ======================================
query_params = st.experimental_get_query_params()

if "code" in query_params:
    code = query_params["code"][0]
    st.success("Código recebido! Solicitando token...")

    payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": st.session_state.code_verifier
    }

    token = requests.post("https://api.mercadolibre.com/oauth/token", data=payload)
    result = token.json()

    st.subheader("📦 Resposta:")
    st.json(result)

    if "access_token" in result:
        st.success("Token obtido com sucesso!")
        st.session_state.access_token = result["access_token"]
