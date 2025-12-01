import streamlit as st
import requests
import sqlite3
import os
from urllib.parse import urlencode

# ======================================================
# CONFIGURAÇÕES DO MERCADO LIVRE
# ======================================================
CLIENT_ID = "8611967944426259"
CLIENT_SECRET = "EBXpqfZLRgKC6e71BYRtKtsmD1zEXXZg"
REDIRECT_URI = "https://ml-anuncios-r37onkxuojbhs8ht5mwb8f.streamlit.app"   # configure no app ML

AUTH_URL = "https://auth.mercadolivre.com.br/authorization"
TOKEN_URL = "https://api.mercadolibre.com/oauth/token"
ITEM_URL = "https://api.mercadolibre.com/items"

DB_NAME = "MLBANCO.db"

# ======================================================
# BANCO LOCAL SQLITE PARA GUARDAR ANÚNCIOS
# ======================================================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS anuncios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            preco REAL,
            categoria TEXT,
            ml_id TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ======================================================
# AUTENTICAÇÃO MERCADO LIVRE
# ======================================================
def get_auth_link():
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
    }
    return f"{AUTH_URL}?{urlencode(params)}"

def get_token(authorization_code):
    payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": authorization_code,
        "redirect_uri": REDIRECT_URI
    }
    resp = requests.post(TOKEN_URL, data=payload)
    return resp.json()

def create_item(access_token, titulo, preco, categoria, fotos_ids):
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "title": titulo,
        "category_id": categoria,
        "price": float(preco),
        "currency_id": "BRL",
        "available_quantity": 1,
        "buying_mode": "buy_it_now",
        "listing_type_id": "gold_pro",
        "condition": "new",
        "pictures": [{"id": img} for img in fotos_ids]
    }

    resp = requests.post(ITEM_URL, json=data, headers=headers)
    return resp.json()

# ======================================================
# UPLOAD DE IMAGEM PARA ML
# ======================================================
def upload_image_to_ml(access_token, image_file):
    headers = {"Authorization": f"Bearer {access_token}"}
    files = {"file": image_file}
    url = "https://api.mercadolibre.com/pictures/items/upload"
    resp = requests.post(url, files=files, headers=headers)
    return resp.json()

# ======================================================
# STREAMLIT
# ======================================================
st.set_page_config(page_title="Criador ML", layout="wide")

st.title("🛒 Criador de Anúncios – Mercado Livre")

# Sessão
if "access_token" not in st.session_state:
    st.session_state.access_token = None

# ======================================================
# LOGIN MERCADO LIVRE
# ======================================================
st.header("1️⃣ Autenticação")

if not st.session_state.access_token:
    st.info("Clique abaixo para autenticar no Mercado Livre")
    st.markdown(f"[🔐 Fazer Login no Mercado Livre]({get_auth_link()})")

    authorization_code = st.text_input("Cole aqui o código retornado pela URL após o login:")

    if st.button("Validar código"):
        if authorization_code:
            token_data = get_token(authorization_code)
            if "access_token" in token_data:
                st.session_state.access_token = token_data["access_token"]
                st.success("Autenticado com sucesso!")
            else:
                st.error(f"Erro: {token_data}")
else:
    st.success("Você já está autenticado!")

# ======================================================
# FORMULÁRIO DO ANÚNCIO
# ======================================================
if st.session_state.access_token:

    st.header("2️⃣ Criar anúncio")

    titulo = st.text_input("Título do anúncio")
    preco = st.number_input("Preço (R$)", min_value=1.0)
    categoria = st.text_input("Categoria (ex.: MLM1678)")

    fotos = st.file_uploader("Envie até 5 fotos", accept_multiple_files=True)

    if st.button("📦 Enviar Anúncio", use_container_width=True, type="primary"):
        if not titulo or not preco or not categoria:
            st.error("Preencha todos os campos!")
        else:
            fotos_ids = []
            for foto in fotos:
                up = upload_image_to_ml(st.session_state.access_token, foto)
                if "id" in up:
                    fotos_ids.append(up["id"])
                else:
                    st.error(f"Erro ao enviar uma foto: {up}")

            item = create_item(st.session_state.access_token, titulo, preco, categoria, fotos_ids)

            if "id" in item:
                st.success(f"Anúncio criado! ID: {item['id']}")

                # salvar localmente
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("""
                    INSERT INTO anuncios (titulo, preco, categoria, ml_id)
                    VALUES (?,?,?,?)
                """, (titulo, preco, categoria, item["id"]))
                conn.commit()
                conn.close()

                st.info("Anúncio salvo localmente no banco MLBANCO.db")
            else:
                st.error(f"Erro ao criar anúncio: {item}")

# ======================================================
# LISTAR ANÚNCIOS SALVOS
# ======================================================
st.header("3️⃣ Anúncios cadastrados no SQLite")

conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
rows = c.execute("SELECT titulo, preco, categoria, ml_id FROM anuncios").fetchall()
conn.close()

st.table(rows)

