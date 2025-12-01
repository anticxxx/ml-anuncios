import streamlit as st
import secrets, hashlib, base64, requests, urllib.parse

CLIENT_ID = "8611967944426259"
CLIENT_SECRET = "EBXpqfZLRgKC6e71BYRtKtsmD1zEXXZg"
REDIRECT_URI = "https://ml-anuncios-r37onkxuojbhs8ht5mwb8f.streamlit.app"

st.set_page_config(page_title="ML PKCE Debug", layout="centered")
st.title("Debug OAuth2 PKCE — Troca de code")

# --- gerar PKCE só 1 vez por sessão ---
if "code_verifier" not in st.session_state:
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    st.session_state.code_verifier = verifier
    st.session_state.code_challenge = challenge
    st.session_state.pkce_locked = True

auth_url = (
    "https://auth.mercadolibre.com/authorization?"
    f"response_type=code&client_id={CLIENT_ID}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    f"&code_challenge={st.session_state.code_challenge}"
    f"&code_challenge_method=S256"
)

st.markdown(f"[➜ Abrir login Mercado Livre]({auth_url})")
st.write("Após o redirect cole a URL completa aqui (ex.: https://.../?code=TG-... ):")

redirect_url = st.text_input("Cole a URL de retorno aqui:")

if st.button("Trocar code por token (Testar)"):
    if not redirect_url:
        st.error("Cole a URL de retorno primeiro.")
    else:
        # extrair code da URL
        try:
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(redirect_url)
            code = parse_qs(parsed.query).get("code",[None])[0]
            if not code:
                st.error("Não achei ?code= na URL fornecida.")
            else:
                st.write(">> Code detectado:", code)
                payload = {
                    "grant_type": "authorization_code",
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": REDIRECT_URI,
                    "code_verifier": st.session_state.code_verifier
                }
                st.subheader("🔎 Payload enviado:")
                st.json(payload)
                # fazer a requisição
                resp = requests.post("https://api.mercadolibre.com/oauth/token", data=payload)
                st.subheader("📦 Resposta bruta:")
                try:
                    st.json(resp.json())
                except Exception:
                    st.text(resp.text)
        except Exception as e:
            st.error("Erro ao processar a URL: " + str(e))
