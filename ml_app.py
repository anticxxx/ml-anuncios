import streamlit as st
import requests

# ==========================
# CONFIG MERCADO LIVRE
# ==========================
CLIENT_ID = "8638371271882362"
CLIENT_SECRET = "O2cEpSmK09bP6N3qCBxGb1GeiAm6CCHn"
REDIRECT_URI = "https://ml-anuncios-r37onkxuojbhs8ht5mwb8f.streamlit.app"

AUTH_URL = "https://auth.mercadolivre.com.br/authorization"
TOKEN_URL = "https://api.mercadolivre.com/oauth/token"

st.set_page_config(page_title="Login ML", layout="centered")

st.title("🔐 Login Mercado Livre (OAuth2 Sem PKCE)")


# ==========================
# BOTÃO LOGIN
# ==========================
if st.button("👉 Clique aqui para fazer login no Mercado Livre", use_container_width=True):
    auth_link = (
        f"{AUTH_URL}?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
    )
    st.markdown(f"🌍 **Abra este link para autorizar:**\n\n[{auth_link}]({auth_link})")


# ==========================
# CAPTURA DO CODE
# ==========================
query_params = st.experimental_get_query_params()

if "code" in query_params:
    code = query_params["code"][0]
    st.success("Código recebido!")
    st.code(code)

    # ==========================
    # SOLICITA TOKEN
    # ==========================
    payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    st.write("📨 Enviando token request...")
    st.json(payload)

    response = requests.post(TOKEN_URL, data=payload, headers={"Accept": "application/json"})
    result = response.json()

    st.write("📦 Resposta da API:")
    st.json(result)

    if "access_token" in result:
        st.success("🎉 TOKEN GERADO COM SUCESSO!")
        st.session_state["access_token"] = result["access_token"]
        st.session_state["refresh_token"] = result["refresh_token"]
