import streamlit as st
import secrets
import hashlib
import base64
import requests
import urllib.parse

# ======================================================
# CONFIG MERCADO LIVRE
# ======================================================
CLIENT_ID = "8611967944426259"
CLIENT_SECRET = "EBXpqfZLRgKC6e71BYRtKtsmD1zEXXZg"
REDIRECT_URI = "https://ml-anuncios-r37onkxuojbhs8ht5mwb8f.streamlit.app"

st.set_page_config(page_title="ML Anúncios", page_icon="🛒")

st.title("🛒 Integração Mercado Livre – Login OAuth2 PKCE")

# ======================================================
# GERA PKCE
# ======================================================
def generate_pkce():
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).rstrip(b"=").decode("utf-8")
    return verifier, challenge

# Guarda PKCE na sessão
if "code_verifier" not in st.session_state:
    st.session_state.code_verifier, st.session_state.code_challenge = generate_pkce()

# ======================================================
# URL para login Mercado Livre
# ======================================================
auth_url = (
    "https://auth.mercadolibre.com/authorization?"
    f"response_type=code&client_id={CLIENT_ID}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    f"&code_challenge={st.session_state.code_challenge}"
    f"&code_challenge_method=S256"
)

st.subheader("🔐 Conectar com Mercado Livre")

st.markdown(f"👉 [**Clique aqui para fazer login no Mercado Livre**]({auth_url})")

st.info("Após autenticar, o Mercado Livre te enviará de volta para esta página com o código de autorização.")

# ======================================================
# PROCESSA O CODE RETORNADO
# ======================================================
query_params = st.experimental_get_query_params()

if "code" in query_params:
    code = query_params["code"][0]
    st.success("Código recebido! Agora solicitando TOKEN...")

    payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": st.session_state.code_verifier,
    }

    token_resp = requests.post("https://api.mercadolibre.com/oauth/token", data=payload)

    result = token_resp.json()

    st.subheader("📦 Resposta da API")
    st.json(result)

    # salva token se estiver OK
    if "access_token" in result:
        st.session_state.access_token = result["access_token"]
        st.success("Token obtido com sucesso! 🎉")

        st.write("Agora você pode criar anúncios usando o token acima.")

