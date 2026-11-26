import streamlit as st
import subprocess
import json
import os
import sys
import time
import uuid
import urllib.request
import urllib.error
import urllib.parse
import random
import secrets
import hashlib
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from google import genai
from google.genai import types

st.set_page_config(
    page_title="Mi Clipper IA Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONFIGURACIÓN DE ADMIN, YAPE Y ACTUALIZACIONES ---
ADMIN_EMAILS = ["gomezhermozaa@gmail.com"]
YAPE_NUMERO = "+51 953 027 160"
YAPE_WHATSAPP = "51953027160"
VERSION_ACTUAL = "1.5.0"
URL_VERSION_JSON = "https://raw.githubusercontent.com/andres261727/CLIPS-/main/version.json"
MODELOS_GEMINI = ["gemini-3.8-flash"]

# --- ESTILO VISUAL PREMIUM (NEXUS STUDIO VIBRANT DARK + NEON GLASS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Ocultar SOLO botón Deploy y menú de tres puntos */
    #MainMenu, [data-testid="stMainMenu"] {display: none !important;}
    .stDeployButton, [data-testid="stAppDeployButton"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    footer {visibility: hidden !important;}
    header[data-testid="stHeader"] {background: transparent !important;}

    /* Asegurar que el botón para abrir la barra lateral sea siempre visible */
    [data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        color: #ffffff !important;
    }

    /* Fondo dinámico con malla de luces neón */
    .stApp {
        background:
            radial-gradient(circle at 15% 10%, rgba(139, 92, 246, 0.32) 0%, transparent 45%),
            radial-gradient(circle at 85% 15%, rgba(236, 72, 153, 0.26) 0%, transparent 45%),
            radial-gradient(circle at 50% 90%, rgba(6, 182, 212, 0.18) 0%, transparent 50%),
            linear-gradient(180deg, #090912 0%, #101022 50%, #0b0b16 100%);
        color: #f8fafc;
    }

    /* Barra lateral */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d0d1a 0%, #131129 100%);
        border-right: 1px solid rgba(139, 92, 246, 0.25);
    }

    /* Contenedores con borde estilo tarjeta SaaS */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(139, 92, 246, 0.25) !important;
        border-radius: 18px !important;
        padding: 1rem !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(14px);
    }

    /* Expanders estilizados */
    .stExpander {
        background: rgba(20, 20, 38, 0.72) !important;
        border: 1px solid rgba(168, 85, 247, 0.3) !important;
        border-radius: 16px !important;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.3);
        margin-bottom: 0.8rem;
    }

    /* Tabs tipo píldora moderna */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(255, 255, 255, 0.04);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 8px 18px;
        color: #cbd5e1;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #7c3aed 0%, #ec4899 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(124, 58, 237, 0.45);
    }

    /* Botón principal neón */
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #7c3aed 0%, #ec4899 50%, #06b6d4 100%) !important;
        background-size: 200% auto !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.3rem !important;
        box-shadow: 0 4px 20px rgba(236, 72, 153, 0.4);
        transition: all 0.25s ease;
    }
    .stButton > button[kind="primary"]:hover {
        background-position: right center !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 28px rgba(6, 182, 212, 0.5);
    }

    /* Botones secundarios */
    .stButton > button {
        border-radius: 12px !important;
        border: 1px solid rgba(139, 92, 246, 0.35) !important;
        background: rgba(255, 255, 255, 0.05) !important;
        color: #f1f5f9 !important;
        font-weight: 600 !important;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        border-color: #22d3ee !important;
        background: rgba(34, 211, 238, 0.14) !important;
        transform: translateY(-1px);
    }

    /* Inputs con borde suave */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(15, 15, 30, 0.85) !important;
        border-color: rgba(139, 92, 246, 0.3) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }

    /* Encabezado Hero */
    .hero-box {
        text-align: center;
        padding: 1.2rem 1rem 1.5rem 1rem;
        margin-bottom: 1.2rem;
        border-radius: 20px;
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.18) 0%, rgba(236, 72, 153, 0.12) 50%, rgba(6, 182, 212, 0.12) 100%);
        border: 1px solid rgba(168, 85, 247, 0.3);
        box-shadow: 0 10px 35px rgba(0, 0, 0, 0.35);
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ffffff 0%, #c084fc 45%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .hero-sub {
        color: #cbd5e1;
        font-size: 1rem;
        margin-top: 0.4rem;
    }

    /* Tarjetas de estadísticas (KPIs) */
    .stat-card {
        background: rgba(255, 255, 255, 0.045);
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 14px;
        padding: 0.9rem 1rem;
        text-align: center;
    }
    .stat-num {
        font-size: 1.4rem;
        font-weight: 800;
        color: #38bdf8;
    }
    .stat-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }

    /* Etiqueta de paso */
    .step-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 0.8px;
        background: linear-gradient(90deg, #7c3aed, #ec4899);
        color: #ffffff;
        margin-bottom: 0.5rem;
    }

    /* Badge de viralidad */
    .viral-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.45);
    }

    /* Logo en sidebar */
    .brand-logo {
        font-size: 1.45rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #c084fc, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    /* Estilos Planes */
    .benefit-item {
        font-size: 0.95rem;
        color: #e2e8f0;
        margin: 0.45rem 0;
    }
    .price-box {
        background: rgba(124, 58, 237, 0.14);
        border: 1px solid rgba(168, 85, 247, 0.45);
        border-radius: 16px;
        padding: 1.1rem;
        margin: 0.8rem 0;
    }
    .super-box {
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.25) 0%, rgba(236, 72, 153, 0.2) 100%);
        border: 2px solid #ec4899;
        border-radius: 16px;
        padding: 1.1rem;
        margin: 0.8rem 0;
    }
    .discount-pill {
        display: inline-block;
        background: rgba(16, 185, 129, 0.22);
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.45);
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        margin-left: 6px;
    }
    .yape-card {
        background: linear-gradient(135deg, rgba(116, 34, 132, 0.35) 0%, rgba(16, 185, 129, 0.18) 100%);
        border: 1px solid rgba(192, 132, 252, 0.45);
        border-radius: 16px;
        padding: 1.1rem;
        text-align: center;
    }
    .beta-badge {
        display: inline-block;
        background: rgba(6, 182, 212, 0.18);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.45);
        padding: 2px 8px;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
        margin-left: 4px;
    }

    /* Comunidad */
    .avatar-circle {
        width: 40px;
        height: 40px;
        border-radius: 999px;
        background: linear-gradient(135deg, #7c3aed, #ec4899);
        color: #ffffff;
        font-weight: 800;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
    }
    .mini-avatar {
        width: 28px;
        height: 28px;
        border-radius: 999px;
        background: rgba(124, 58, 237, 0.35);
        border: 1px solid rgba(192, 132, 252, 0.5);
        color: #f8fafc;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-right: 4px;
    }
    .comm-stat-box {
        text-align: center;
        padding: 0.4rem 0.2rem;
    }
    .comm-stat-val {
        font-size: 1.25rem;
        font-weight: 800;
        color: #ffffff;
    }
    .comm-stat-lbl {
        font-size: 0.75rem;
        color: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# SISTEMA DE ACTUALIZACIONES AUTOMÁTICAS (VALIDACIÓN ESTRICTA DE VERSIÓN)
# ==============================================================================
def version_a_tupla(v: str):
    try:
        return tuple(int(x) for x in str(v).strip().lstrip("vV").split("."))
    except Exception:
        return (0, 0, 0)

def revisar_actualizacion():
    if "update_checked" in st.session_state:
        return
    st.session_state["update_checked"] = True
    st.session_state.pop("nueva_version", None)
    try:
        req = urllib.request.Request(URL_VERSION_JSON, headers={"Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            ver_remota = data.get("version", "")
            if ver_remota and version_a_tupla(ver_remota) > version_a_tupla(VERSION_ACTUAL):
                st.session_state["nueva_version"] = data
    except Exception:
        pass

@st.dialog("🚀 ¡Nueva versión disponible!")
def mostrar_popup_actualizacion(info):
    st.markdown(f"Tu versión actual: **`v{VERSION_ACTUAL}`** → Nueva versión: **`v{info['version']}`**")
    if info.get("notas"):
        st.info(f"**Novedades:** {info['notas']}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬇️ Actualizar ahora", type="primary", use_container_width=True):
            try:
                with st.spinner("Descargando e instalando actualización..."):
                    with urllib.request.urlopen(info["url_codigo"], timeout=10) as resp:
                        nuevo_codigo = resp.read().decode("utf-8")
                    Path(__file__).write_text(nuevo_codigo, encoding="utf-8")
                st.success("¡Actualizado! Recargando programa...")
                st.session_state.pop("nueva_version", None)
                time.sleep(1.5)
                st.rerun()
            except Exception as e:
                st.error(f"No se pudo actualizar: {e}")
    with col2:
        if st.button("Más tarde", use_container_width=True):
            st.session_state.pop("nueva_version", None)
            st.rerun()

revisar_actualizacion()
if "nueva_version" in st.session_state:
    ver_guardada = st.session_state["nueva_version"].get("version", "")
    if version_a_tupla(ver_guardada) > version_a_tupla(VERSION_ACTUAL):
        mostrar_popup_actualizacion(st.session_state["nueva_version"])
    else:
        st.session_state.pop("nueva_version", None)

# ==============================================================================
# BASE DE DATOS: USUARIOS, PLANES, KEYS Y COMUNIDAD
# ==============================================================================
def init_db():
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            email TEXT PRIMARY KEY,
            password TEXT,
            plan_activo INTEGER DEFAULT 0,
            plan_tipo TEXT DEFAULT 'FREE',
            plan_expira TEXT,
            es_admin INTEGER DEFAULT 0,
            apodo TEXT
        )
    """)
    for col_def in (
        "plan_activo INTEGER DEFAULT 0",
        "plan_tipo TEXT DEFAULT 'FREE'",
        "plan_expira TEXT",
        "es_admin INTEGER DEFAULT 0",
        "apodo TEXT"
    ):
        try:
            c.execute(f"ALTER TABLE usuarios ADD COLUMN {col_def}")
        except sqlite3.OperationalError:
            pass

    c.execute("""
        CREATE TABLE IF NOT EXISTS license_keys (
            clave TEXT PRIMARY KEY,
            dias INTEGER,
            plan_tipo TEXT DEFAULT 'PRO',
            da_admin INTEGER DEFAULT 0,
            usada_por TEXT,
            fecha_creacion TEXT,
            fecha_uso TEXT
        )
    """)
    for col_def in ("plan_tipo TEXT DEFAULT 'PRO'", "da_admin INTEGER DEFAULT 0"):
        try:
            c.execute(f"ALTER TABLE license_keys ADD COLUMN {col_def}")
        except sqlite3.OperationalError:
            pass

    c.execute("""
        CREATE TABLE IF NOT EXISTS comunidad_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            autor_email TEXT,
            autor_nombre TEXT,
            categoria TEXT,
            titulo TEXT,
            contenido TEXT,
            likes INTEGER DEFAULT 0,
            fecha TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS comunidad_comentarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            autor_nombre TEXT,
            comentario TEXT,
            fecha TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS comunidad_votos (
            email TEXT,
            opcion TEXT,
            PRIMARY KEY (email, opcion)
        )
    """)

    conn.commit()
    conn.close()

def encriptar_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def actualizar_password(email: str, nueva_password: str) -> bool:
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute(
        "UPDATE usuarios SET password = ? WHERE email = ?",
        (encriptar_password(nueva_password), email.strip().lower())
    )
    actualizados = c.rowcount > 0
    conn.commit()
    conn.close()
    return actualizados

def es_admin_super(email: str) -> bool:
    return email.strip().lower() in [a.lower() for a in ADMIN_EMAILS]

def es_admin(email: str) -> bool:
    if es_admin_super(email):
        return True
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("SELECT es_admin FROM usuarios WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()
    return bool(row and row[0])

def obtener_nombre_comunidad(email: str) -> str:
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("SELECT apodo FROM usuarios WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()
    if row and row[0] and row[0].strip():
        return row[0].strip()
    return email.split("@")[0]

def guardar_apodo_comunidad(email: str, apodo: str):
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("UPDATE usuarios SET apodo = ? WHERE email = ?", (apodo.strip(), email))
    conn.commit()
    conn.close()

def crear_post_comunidad(email: str, autor_nombre: str, categoria: str, titulo: str, contenido: str):
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO comunidad_posts (autor_email, autor_nombre, categoria, titulo, contenido, likes, fecha) VALUES (?, ?, ?, ?, ?, 0, ?)",
        (email, autor_nombre, categoria, titulo.strip(), contenido.strip(), datetime.now().strftime("%d/%m %H:%M"))
    )
    conn.commit()
    conn.close()

def dar_like_post(post_id: int):
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("UPDATE comunidad_posts SET likes = likes + 1 WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

def agregar_comentario_comunidad(post_id: int, autor_nombre: str, comentario: str):
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO comunidad_comentarios (post_id, autor_nombre, comentario, fecha) VALUES (?, ?, ?, ?)",
        (post_id, autor_nombre, comentario.strip(), datetime.now().strftime("%d/%m %H:%M"))
    )
    conn.commit()
    conn.close()

def votar_encuesta(email: str, opcion: str):
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM comunidad_votos WHERE email = ? AND opcion = ?", (email, opcion))
    ya_voto = c.fetchone() is not None
    if ya_voto:
        c.execute("DELETE FROM comunidad_votos WHERE email = ? AND opcion = ?", (email, opcion))
    else:
        c.execute("INSERT INTO comunidad_votos (email, opcion) VALUES (?, ?)", (email, opcion))
    conn.commit()
    conn.close()

def obtener_datos_comunidad():
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM usuarios")
    total_miembros = c.fetchone()[0]

    c.execute("SELECT email, apodo FROM usuarios")
    miembros_rows = c.fetchall()

    c.execute("SELECT id, autor_email, autor_nombre, categoria, titulo, contenido, likes, fecha FROM comunidad_posts ORDER BY id DESC")
    posts = c.fetchall()

    c.execute("SELECT id, post_id, autor_nombre, comentario, fecha FROM comunidad_comentarios ORDER BY id ASC")
    comentarios_rows = c.fetchall()

    c.execute("SELECT opcion, COUNT(*) FROM comunidad_votos GROUP BY opcion")
    votos_rows = dict(c.fetchall())
    conn.close()

    comentarios_por_post = {}
    for cid, pid, anombre, ctxt, cfecha in comentarios_rows:
        comentarios_por_post.setdefault(pid, []).append((cid, anombre, ctxt, cfecha))

    return {
        "total_miembros": total_miembros,
        "miembros_rows": miembros_rows,
        "posts": posts,
        "comentarios_por_post": comentarios_por_post,
        "total_comentarios": len(comentarios_rows),
        "votos": votos_rows
    }

def usuario_existe(email: str) -> bool:
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM usuarios WHERE email = ?", (email.strip().lower(),))
    existe = c.fetchone() is not None
    conn.close()
    return existe

def registrar_usuario(email: str, password: str) -> bool:
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    try:
        admin_flag = 1 if es_admin_super(email) else 0
        activo = 1 if admin_flag else 0
        tipo = "SUPER_PRO" if admin_flag else "FREE"
        expira = "ILIMITADO" if admin_flag else None
        apodo_ini = email.split("@")[0]
        c.execute(
            "INSERT INTO usuarios (email, password, plan_activo, plan_tipo, plan_expira, es_admin, apodo) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (email, encriptar_password(password), activo, tipo, expira, admin_flag, apodo_ini)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verificar_login(email: str, password: str) -> bool:
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute(
        "SELECT 1 FROM usuarios WHERE email = ? AND password = ?",
        (email, encriptar_password(password))
    )
    valido = c.fetchone() is not None
    conn.close()
    return valido

def obtener_estado_plan(email: str):
    if es_admin(email):
        return "SUPER_PRO", "ADMIN SUPER PRO"
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("SELECT plan_activo, plan_tipo, plan_expira FROM usuarios WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()
    if not row or not row[0]:
        return "FREE", "Plan Free"

    tipo = row[1] if row[1] in ("PRO", "SUPER_PRO") else "PRO"
    expira = row[2]
    etiqueta = "Super Pro" if tipo == "SUPER_PRO" else "Plan Pro"

    if expira == "ILIMITADO":
        return tipo, f"{etiqueta} (Ilimitado)"
    try:
        fecha_exp = datetime.strptime(expira, "%Y-%m-%d")
        if datetime.now() <= fecha_exp + timedelta(days=1):
            return tipo, f"{etiqueta} (hasta {expira})"
        return "FREE", f"Plan Free (venció {expira})"
    except Exception:
        return "FREE", "Plan Free"

def generar_nueva_key(dias: int, plan_tipo: str = "PRO", da_admin: bool = False) -> str:
    prefijo = "SPRO" if plan_tipo == "SUPER_PRO" else "PRO"
    parte1 = secrets.token_hex(2).upper()
    parte2 = secrets.token_hex(2).upper()
    clave = f"{prefijo}-{parte1}-{parte2}"
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO license_keys (clave, dias, plan_tipo, da_admin, usada_por, fecha_creacion, fecha_uso) VALUES (?, ?, ?, ?, NULL, ?, NULL)",
        (clave, dias, plan_tipo, 1 if da_admin else 0, datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()
    conn.close()
    return clave

def canjear_key(email: str, clave: str):
    clave = clave.strip().upper()
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("SELECT dias, plan_tipo, da_admin, usada_por FROM license_keys WHERE clave = ?", (clave,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False, "La key no existe. Verifica que esté bien escrita."
    dias, plan_tipo, da_admin, usada_por = row
    if usada_por is not None:
        conn.close()
        return False, "Esta key ya fue utilizada por otra cuenta."

    plan_tipo = plan_tipo if plan_tipo in ("PRO", "SUPER_PRO") else "PRO"
    expira = "ILIMITADO" if dias == 0 else (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d")

    c.execute(
        "UPDATE license_keys SET usada_por = ?, fecha_uso = ? WHERE clave = ?",
        (email, datetime.now().strftime("%Y-%m-%d %H:%M"), clave)
    )
    if da_admin:
        c.execute(
            "UPDATE usuarios SET plan_activo = 1, plan_tipo = ?, plan_expira = ?, es_admin = 1 WHERE email = ?",
            (plan_tipo, expira, email)
        )
    else:
        c.execute(
            "UPDATE usuarios SET plan_activo = 1, plan_tipo = ?, plan_expira = ? WHERE email = ?",
            (plan_tipo, expira, email)
        )
    conn.commit()
    conn.close()
    nombre_plan = "Plan Super Pro" if plan_tipo == "SUPER_PRO" else "Plan Pro"
    extra_admin = " + Panel Admin" if da_admin else ""
    return True, f"¡{nombre_plan} activado{extra_admin}! Vigencia: {expira}"

def actualizar_acceso_manual(email: str, plan_tipo: str, dias: int = 30):
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    if plan_tipo == "FREE":
        c.execute("UPDATE usuarios SET plan_activo = 0, plan_tipo = 'FREE', plan_expira = NULL WHERE email = ?", (email,))
    else:
        expira = "ILIMITADO" if dias == 0 else (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d")
        c.execute("UPDATE usuarios SET plan_activo = 1, plan_tipo = ?, plan_expira = ? WHERE email = ?", (plan_tipo, expira, email))
    conn.commit()
    conn.close()

def cambiar_rol_admin(email: str, hacer_admin: bool):
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("UPDATE usuarios SET es_admin = ? WHERE email = ?", (1 if hacer_admin else 0, email))
    conn.commit()
    conn.close()

def listar_keys():
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("SELECT clave, dias, plan_tipo, da_admin, usada_por, fecha_creacion, fecha_uso FROM license_keys ORDER BY fecha_creacion DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def listar_usuarios():
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("SELECT email, plan_activo, plan_tipo, plan_expira, es_admin FROM usuarios ORDER BY email ASC")
    rows = c.fetchall()
    conn.close()
    return rows

def enviar_codigo_gmail(destinatario: str, codigo: str, motivo: str = "registro"):
    if "EMAIL_REMITENTE" not in st.secrets or "BREVO_API_KEY" not in st.secrets:
        raise Exception("Falta configurar EMAIL_REMITENTE y BREVO_API_KEY en los Secrets.")

    remitente = st.secrets["EMAIL_REMITENTE"].strip()
    api_key = st.secrets["BREVO_API_KEY"].strip()

    if motivo == "recuperacion":
        asunto = "🔐 Recupera tu contraseña - Mi Clipper IA Studio"
        cuerpo = (
            f"Hola,\n\nSolicitaste restablecer tu contraseña en Mi Clipper IA Studio.\n"
            f"Tu código de recuperación (válido por 10 minutos) es:\n\n"
            f"    {codigo}\n\n"
            f"Ingrésalo en la web junto con tu nueva contraseña.\n"
            f"Si no solicitaste este cambio, ignora este correo y tu contraseña actual seguirá intacta."
        )
    else:
        asunto = "⚡ Tu código de verificación - Mi Clipper IA Studio"
        cuerpo = (
            f"Hola,\n\nTu código de verificación para crear tu cuenta en Mi Clipper IA Studio es:\n\n"
            f"    {codigo}\n\n"
            f"Ingrésalo en la web para activar tu cuenta.\n"
            f"Si no solicitaste este código, ignora este correo."
        )

    payload = json.dumps({
        "sender": {"name": "Mi Clipper IA Studio", "email": remitente},
        "to": [{"email": destinatario}],
        "subject": asunto,
        "textContent": cuerpo
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=payload,
        headers={
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status not in (200, 201, 202):
                raise Exception(f"Brevo devolvió estado HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        detalle = e.read().decode("utf-8", errors="ignore")
        raise Exception(f"Error de Brevo ({e.code}): {detalle}")

init_db()

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "pagina_actual" not in st.session_state:
    st.session_state["pagina_actual"] = "💬 Inicio (Chat IA)"
if "transcripciones_cache" not in st.session_state:
    st.session_state["transcripciones_cache"] = {}

# ==============================================================================
# PANTALLA DE LOGIN / REGISTRO / RECUPERAR CONTRASEÑA CON GMAIL
# ==============================================================================
if not st.session_state["autenticado"]:
    _, col_centro, _ = st.columns([1, 1.6, 1])
    with col_centro:
        st.markdown("""
        <div class="hero-box">
            <div class="hero-title">⚡ Mi Clipper IA Studio</div>
            <div class="hero-sub">Inicia sesión, crea tu cuenta o recupera tu contraseña con Gmail.</div>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            tab_login, tab_registro, tab_recuperar = st.tabs([
                "🔐 Iniciar Sesión",
                "✨ Crear Cuenta",
                "🔑 Olvidé mi contraseña"
            ])

            with tab_login:
                email_login = st.text_input("Correo Gmail", key="login_email", placeholder="tucorreo@gmail.com").strip().lower()
                pass_login = st.text_input("Contraseña", type="password", key="login_pass")

                if st.button("Entrar al Studio", type="primary", use_container_width=True):
                    if verificar_login(email_login, pass_login):
                        st.session_state["autenticado"] = True
                        st.session_state["usuario"] = email_login
                        st.rerun()
                    else:
                        st.error("Correo o contraseña incorrectos.")

            with tab_registro:
                email_reg = st.text_input("Tu correo Gmail", key="reg_email", placeholder="tucorreo@gmail.com").strip().lower()
                pass_reg = st.text_input("Crea una contraseña (mín. 6 caracteres)", type="password", key="reg_pass")

                if st.button("📩 Enviar código de verificación", type="primary", use_container_width=True):
                    if not email_reg.endswith("@gmail.com"):
                        st.warning("Por favor, usa un correo válido terminado en @gmail.com.")
                    elif len(pass_reg) < 6:
                        st.warning("La contraseña debe tener al menos 6 caracteres.")
                    elif usuario_existe(email_reg):
                        st.error("Este correo ya está registrado. Ve a Iniciar Sesión.")
                    else:
                        codigo = str(random.randint(100000, 999999))
                        try:
                            with st.spinner("Enviando código a tu Gmail..."):
                                enviar_codigo_gmail(email_reg, codigo, motivo="registro")
                            st.session_state["codigo_enviado"] = codigo
                            st.session_state["email_pendiente"] = email_reg
                            st.session_state["pass_pendiente"] = pass_reg
                            st.success("¡Código enviado! Revisa tu bandeja de entrada o la carpeta de Spam.")
                        except Exception as e:
                            st.error(f"Error al enviar el correo: {e}")

                if "codigo_enviado" in st.session_state:
                    st.divider()
                    codigo_ingresado = st.text_input("Ingresa el código de 6 dígitos", key="reg_codigo_in").strip()

                    if st.button("✅ Verificar y crear cuenta", type="primary", use_container_width=True):
                        if codigo_ingresado == st.session_state["codigo_enviado"]:
                            if registrar_usuario(st.session_state["email_pendiente"], st.session_state["pass_pendiente"]):
                                st.success("¡Cuenta creada con éxito! Ya puedes iniciar sesión.")
                                for k in ("codigo_enviado", "email_pendiente", "pass_pendiente"):
                                    st.session_state.pop(k, None)
                            else:
                                st.error("Ese correo ya está registrado.")
                        else:
                            st.error("Código incorrecto. Inténtalo de nuevo.")

            with tab_recuperar:
                st.caption("Te enviaremos un código de 6 dígitos a tu Gmail registrado para cambiar tu contraseña.")
                email_rec = st.text_input(
                    "Correo Gmail de tu cuenta",
                    key="rec_email",
                    placeholder="tucorreo@gmail.com"
                ).strip().lower()

                if st.button("📩 Enviar código de recuperación", type="primary", use_container_width=True):
                    if not email_rec.endswith("@gmail.com"):
                        st.warning("Ingresa un correo válido terminado en @gmail.com.")
                    elif not usuario_existe(email_rec):
                        st.error("No existe ninguna cuenta registrada con ese correo.")
                    else:
                        codigo_rec = str(random.randint(100000, 999999))
                        try:
                            with st.spinner("Enviando código de recuperación a tu Gmail..."):
                                enviar_codigo_gmail(email_rec, codigo_rec, motivo="recuperacion")
                            st.session_state["rec_codigo"] = codigo_rec
                            st.session_state["rec_email_pendiente"] = email_rec
                            st.session_state["rec_expira"] = time.time() + 600
                            st.success("¡Código enviado! Revisa tu bandeja de entrada o Spam (expira en 10 minutos).")
                        except Exception as e:
                            st.error(f"Error al enviar el correo: {e}")

                if "rec_codigo" in st.session_state and "rec_email_pendiente" in st.session_state:
                    st.divider()
                    st.info(f"Código enviado a **{st.session_state['rec_email_pendiente']}**")
                    codigo_rec_in = st.text_input("Código de 6 dígitos", key="rec_codigo_in").strip()
                    nueva_pass = st.text_input("Nueva contraseña (mín. 6 caracteres)", type="password", key="rec_new_pass")
                    confirmar_pass = st.text_input("Confirmar nueva contraseña", type="password", key="rec_conf_pass")

                    if st.button("🔄 Cambiar contraseña", type="primary", use_container_width=True):
                        if time.time() > st.session_state.get("rec_expira", 0):
                            st.error("El código ha expirado. Solicita uno nuevo.")
                            for k in ("rec_codigo", "rec_email_pendiente", "rec_expira"):
                                st.session_state.pop(k, None)
                        elif codigo_rec_in != st.session_state["rec_codigo"]:
                            st.error("El código de verificación es incorrecto.")
                        elif len(nueva_pass) < 6:
                            st.warning("La nueva contraseña debe tener al menos 6 caracteres.")
                        elif nueva_pass != confirmar_pass:
                            st.warning("Las contraseñas no coinciden.")
                        else:
                            if actualizar_password(st.session_state["rec_email_pendiente"], nueva_pass):
                                st.success("¡Contraseña actualizada con éxito! Ya puedes iniciar sesión con tu nueva clave.")
                                for k in ("rec_codigo", "rec_email_pendiente", "rec_expira"):
                                    st.session_state.pop(k, None)
                            else:
                                st.error("No se pudo actualizar la contraseña. Inténtalo de nuevo.")
    st.stop()

# ==============================================================================
# ESTADO DEL USUARIO ACTUAL (FREE / PRO / SUPER_PRO / ADMIN)
# ==============================================================================
nivel_plan, texto_plan = obtener_estado_plan(st.session_state["usuario"])
es_pro = nivel_plan in ("PRO", "SUPER_PRO")
es_super_pro = (nivel_plan == "SUPER_PRO")
usuario_es_admin = es_admin(st.session_state["usuario"])

# --- RUTAS Y ARCHIVOS SEPARADOS POR USUARIO ---
USER_HASH = hashlib.md5(st.session_state["usuario"].encode()).hexdigest()[:12]
USER_BASE = Path("user_data") / USER_HASH
WORK_DIR = USER_BASE / "workspace"
CLIPS_DIR = USER_BASE / "clips_generados"
EDITED_DIR = USER_BASE / "clips_editados"
USER_CONFIG_FILE = USER_BASE / "config_usuario.json"
PROJECTS_FILE = USER_BASE / "proyectos.json"

WORK_DIR.mkdir(parents=True, exist_ok=True)
CLIPS_DIR.mkdir(parents=True, exist_ok=True)
EDITED_DIR.mkdir(parents=True, exist_ok=True)

def cargar_json(path: Path, default):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def guardar_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

user_config = cargar_json(USER_CONFIG_FILE, {})
proyectos = cargar_json(PROJECTS_FILE, [])

# ==============================================================================
# SKILLS DE AGENTE (INSTRUCCIONES DE ESTILO / SUBAGENTE)
# ==============================================================================
SKILLS_DISPONIBLES = {
    "⚡ Viral Sniper (Ganchos rápidos y retención)": "Prioriza cortes con gancho agresivo en los primeros 2 segundos, giros rápidos y frases que detienen el scroll.",
    "🎬 Storyteller / Subagente Narrativo": "Actúa como subagente narrativo: busca arcos completos con inicio, tensión y remate claro, sin cortar ideas a medias.",
    "🔥 Debate / Polémica / Contraste": "Enfócate en opiniones fuertes, comparaciones extremas, errores comunes y momentos que provoquen comentarios.",
    "🎓 Educativo / Valor Directo": "Extrae explicaciones claras, pasos prácticos, datos sorprendentes y conclusiones accionables."
}

def obtener_instruccion_skill() -> str:
    skill_sel = user_config.get("skill_ia", list(SKILLS_DISPONIBLES.keys())[0])
    return SKILLS_DISPONIBLES.get(skill_sel, "")

# ==============================================================================
# MOTORES IA: DETECCIÓN DINÁMICA DE MODELOS GROQ + DEEPSEEK BETA + ANTI-413
# ==============================================================================
BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

def compactar_transcripcion(transcripcion: str, max_chars: int = 11500) -> str:
    if len(transcripcion) <= max_chars:
        return transcripcion
    lineas = transcripcion.splitlines()
    if len(lineas) <= 30:
        return transcripcion[:max_chars]
    paso = max(1, len(lineas) // 130)
    muestra = lineas[::paso]
    texto_compacto = "\n".join(muestra)
    if len(texto_compacto) > max_chars:
        texto_compacto = texto_compacto[:max_chars]
    return texto_compacto + "\n[...transcripción compactada para mantener velocidad y límite de tokens...]"

def obtener_modelos_groq_ordenados(api_key: str) -> list:
    if st.session_state.get("groq_modelos_lista"):
        return st.session_state["groq_modelos_lista"]

    url = "https://api.groq.com/openai/v1/models"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {api_key}", "User-Agent": BROWSER_UA},
        method="GET"
    )
    excluidos = ("whisper", "guard", "tts", "playai", "embed", "moderation", "orpheus", "safeguard", "qwen")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        modelos = [m["id"] for m in data.get("data", []) if m.get("id")]
        chat_modelos = [m for m in modelos if not any(ex in m.lower() for ex in excluidos)]

        def prioridad(nombre_m: str) -> int:
            nl = nombre_m.lower()
            if "8b" in nl and "llama" in nl:
                return 0
            if "llama" in nl:
                return 1
            if "gemma" in nl:
                return 2
            return 3

        chat_modelos.sort(key=prioridad)
        if chat_modelos:
            st.session_state["groq_modelos_lista"] = chat_modelos
            return chat_modelos
    except Exception:
        pass
    return []

def transcribir_audio_whisper_api(audio_path: str, proveedor: str, api_key: str) -> str:
    cache = st.session_state["transcripciones_cache"]
    if audio_path in cache:
        return cache[audio_path]

    if proveedor == "groq":
        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        modelo = "whisper-large-v3-turbo"
    else:
        url = "https://api.openai.com/v1/audio/transcriptions"
        modelo = "whisper-1"

    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    filename = Path(audio_path).name
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    partes = []
    for campo, valor in [("model", modelo), ("response_format", "verbose_json")]:
        partes.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{campo}"\r\n\r\n'
            f"{valor}\r\n".encode("utf-8")
        )
    partes.append(
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: audio/mpeg\r\n\r\n".encode("utf-8")
    )
    partes.append(audio_bytes)
    partes.append(f"\r\n--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(partes)

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": BROWSER_UA
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detalle = e.read().decode("utf-8", errors="ignore")
        raise Exception(f"HTTP {e.code}: {detalle}")

    segmentos = data.get("segments", [])
    if segmentos:
        resultado = "\n".join([f"[{s['start']:.1f}s - {s['end']:.1f}s] {s['text'].strip()}" for s in segmentos])
    else:
        resultado = data.get("text", "")

    cache[audio_path] = resultado
    return resultado

def llamar_chat_openai_compatible(proveedor: str, api_key: str, prompt: str, esperar_json: bool = False, max_tokens: int = 2500):
    if proveedor == "groq":
        url = "https://api.groq.com/openai/v1/chat/completions"
        candidatos = obtener_modelos_groq_ordenados(api_key)
        if not candidatos:
            raise Exception("No se encontraron modelos de chat activos en tu cuenta de Groq.")
    elif proveedor == "deepseek":
        url = "https://api.deepseek.com/chat/completions"
        candidatos = ["deepseek-chat"]
    else:
        url = "https://api.openai.com/v1/chat/completions"
        candidatos = ["gpt-4o-mini"]

    ultimo_err = None
    for idx_m, modelo in enumerate(candidatos):
        payload_dict = {
            "model": modelo,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4,
            "max_tokens": max_tokens
        }
        if esperar_json:
            payload_dict["response_format"] = {"type": "json_object"}

        req = urllib.request.Request(
            url,
            data=json.dumps(payload_dict).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": BROWSER_UA
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if idx_m > 0 and proveedor == "groq":
                st.session_state["groq_modelos_lista"] = candidatos[idx_m:] + candidatos[:idx_m]
            return data["choices"][0]["message"]["content"], modelo
        except urllib.error.HTTPError as e:
            detalle = e.read().decode("utf-8", errors="ignore")
            ultimo_err = Exception(f"HTTP {e.code} ({modelo}): {detalle}")
            if proveedor == "groq" and e.code in (404, 413, 400):
                continue
            raise ultimo_err

    raise ultimo_err

def obtener_orden_motores():
    preferencia = user_config.get("motor_ia", "⚡ Ultra Rápido (Groq → DeepSeek → Gemini)")
    if preferencia == "DeepSeek · API Beta":
        return ["deepseek"]
    if preferencia == "Solo Groq (Llama 3)":
        return ["groq"]
    if preferencia == "Solo Gemini":
        return ["gemini"]
    if preferencia == "Solo OpenAI (GPT-4o-mini)":
        return ["openai"]
    if preferencia == "Automático (Gemini → Groq → DeepSeek → OpenAI)":
        return ["gemini", "groq", "deepseek", "openai"]
    return ["groq", "deepseek", "gemini", "openai"]

def ejecutar_ia_con_respaldo(prompt: str, audio_path: str = None, esperar_json: bool = False, usar_google_search: bool = False, max_tokens: int = 2500):
    skill_txt = obtener_instruccion_skill()
    prompt_con_skill = f"SKILL ACTIVA DEL SUBAGENTE: {skill_txt}\n\n{prompt}" if skill_txt else prompt

    motores = obtener_orden_motores()
    errores = []

    for motor in motores:
        if motor == "gemini":
            g_key = user_config.get("api_key", "").strip()
            if not g_key:
                errores.append("Gemini: sin API Key")
                continue
            if st.session_state.get("gemini_agotado") and len(motores) > 1:
                errores.append("Gemini: cuota agotada (saltado)")
                continue

            client = genai.Client(api_key=g_key)
            audio_file = None
            try:
                contents = prompt_con_skill
                if audio_path:
                    audio_file = client.files.upload(file=audio_path)
                    while audio_file.state.name == "PROCESSING":
                        time.sleep(1.0)
                        audio_file = client.files.get(name=audio_file.name)
                    contents = [audio_file, prompt_con_skill]

                cfg_kwargs = {"max_output_tokens": max_tokens}
                if esperar_json:
                    cfg_kwargs["response_mime_type"] = "application/json"
                elif usar_google_search:
                    cfg_kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]
                cfg = types.GenerateContentConfig(**cfg_kwargs)

                for modelo in MODELOS_GEMINI:
                    try:
                        resp = client.models.generate_content(model=modelo, contents=contents, config=cfg)
                        return resp.text, f"Gemini ({modelo})"
                    except Exception as e_mod:
                        errores.append(f"{modelo}: {e_mod}")
                        if "429" in str(e_mod) or "RESOURCE_EXHAUSTED" in str(e_mod):
                            st.session_state["gemini_agotado"] = True
                            break
                        if "503" in str(e_mod) or "UNAVAILABLE" in str(e_mod):
                            time.sleep(1.5)
                            continue
            except Exception as e_g:
                errores.append(f"Gemini: {e_g}")
            finally:
                if audio_file:
                    try:
                        client.files.delete(name=audio_file.name)
                    except Exception:
                        pass

        elif motor == "groq":
            gr_key = user_config.get("groq_key", "").strip()
            if not gr_key:
                errores.append("Groq: sin API Key")
                continue
            try:
                prompt_final = prompt_con_skill
                if audio_path:
                    transcripcion = transcribir_audio_whisper_api(audio_path, "groq", gr_key)
                    transcripcion_lista = compactar_transcripcion(transcripcion, max_chars=11500)
                    prompt_final = f"TRANSCRIPCIÓN CON TIEMPOS EXACTOS DEL AUDIO:\n{transcripcion_lista}\n\nINSTRUCCIÓN:\n{prompt_con_skill}"
                try:
                    texto, modelo_usado = llamar_chat_openai_compatible("groq", gr_key, prompt_final, esperar_json=esperar_json, max_tokens=max_tokens)
                    return texto, f"Groq ({modelo_usado})"
                except Exception as e_413:
                    if "413" in str(e_413) or "too large" in str(e_413).lower():
                        prompt_mini = compactar_transcripcion(prompt_final, max_chars=7000)
                        texto, modelo_usado = llamar_chat_openai_compatible("groq", gr_key, prompt_mini, esperar_json=esperar_json, max_tokens=max_tokens)
                        return texto, f"Groq ({modelo_usado} · compactado)"
                    raise e_413
            except Exception as e_gr:
                errores.append(f"Groq: {e_gr}")

        elif motor == "deepseek":
            ds_key = user_config.get("deepseek_key", "").strip()
            if not ds_key:
                errores.append("DeepSeek Beta: sin llave de API")
                continue
            try:
                prompt_final = prompt_con_skill
                if audio_path:
                    trans_key = user_config.get("groq_key", "").strip() or user_config.get("openai_key", "").strip()
                    trans_prov = "groq" if user_config.get("groq_key", "").strip() else "openai"
                    if trans_key:
                        transcripcion = transcribir_audio_whisper_api(audio_path, trans_prov, trans_key)
                        transcripcion_lista = compactar_transcripcion(transcripcion, max_chars=24000)
                        prompt_final = f"TRANSCRIPCIÓN CON TIEMPOS EXACTOS DEL AUDIO:\n{transcripcion_lista}\n\nINSTRUCCIÓN:\n{prompt_con_skill}"
                    else:
                        prompt_final = f"Analiza y responde según la instrucción:\n{prompt_con_skill}"
                texto, modelo_usado = llamar_chat_openai_compatible("deepseek", ds_key, prompt_final, esperar_json=esperar_json, max_tokens=max_tokens)
                return texto, f"DeepSeek Beta ({modelo_usado})"
            except Exception as e_ds:
                errores.append(f"DeepSeek Beta: {e_ds}")

        elif motor == "openai":
            oa_key = user_config.get("openai_key", "").strip()
            if not oa_key:
                errores.append("OpenAI: sin API Key")
                continue
            try:
                prompt_final = prompt_con_skill
                if audio_path:
                    transcripcion = transcribir_audio_whisper_api(audio_path, "openai", oa_key)
                    transcripcion_lista = compactar_transcripcion(transcripcion, max_chars=24000)
                    prompt_final = f"TRANSCRIPCIÓN CON TIEMPOS EXACTOS DEL AUDIO:\n{transcripcion_lista}\n\nINSTRUCCIÓN:\n{prompt_con_skill}"
                texto, modelo_usado = llamar_chat_openai_compatible("openai", oa_key, prompt_final, esperar_json=esperar_json, max_tokens=max_tokens)
                return texto, f"OpenAI ({modelo_usado})"
            except Exception as e_oa:
                errores.append(f"OpenAI: {e_oa}")

    resumen = " | ".join(errores)
    raise Exception(f"No se pudo completar con ningún motor IA. Revisa tus llaves en la barra lateral (⚙️ Opciones). Detalle: {resumen}")

# --- COLORES, FUENTES, PRESETS Y LAYOUTS ---
COLORES_SUBTITULOS = {
    "Amarillo viral": "&H0000FFFF",
    "Blanco limpio": "&H00FFFFFF",
    "Verde neón": "&H0055FF33",
    "Cian eléctrico": "&H00FFFF00",
    "Rosa aesthetic": "&H00CC99FF",
    "Dorado cine": "&H0037AFD4",
    "Naranja fuego": "&H000088FF",
}

FUENTES_SUBTITULOS = {
    "Impacto Bold (Arial Black)": "Arial Black",
    "Clásico Viral (Impact)": "Impact",
    "Limpio Moderno (DejaVu Sans)": "DejaVu Sans",
    "Editorial (Liberation Sans)": "Liberation Sans",
    "Nítido (Verdana)": "Verdana",
    "Dinámico (Trebuchet MS)": "Trebuchet MS",
}

PRESETS_SUBTITULOS = {
    "🔥 TikTok Clásico": {"color": "Amarillo viral", "tamano": 22, "x_pct": 50, "y_pct": 82, "fuente": "Impacto Bold (Arial Black)"},
    "🎯 Gancho Arriba": {"color": "Cian eléctrico", "tamano": 24, "x_pct": 50, "y_pct": 18, "fuente": "Clásico Viral (Impact)"},
    "✨ Centro Dramático": {"color": "Blanco limpio", "tamano": 23, "x_pct": 50, "y_pct": 50, "fuente": "Limpio Moderno (DejaVu Sans)"},
}

LAYOUTS_VIDEO = [
    "Pantalla completa (9:16)",
    "Imagen entera + fondo blur (9:16)",
    "Cuadrado centrado + fondo blur (9:16)",
    "Horizontal original (16:9)",
    "Cuadrado (1:1)"
]

# --- FUNCIONES DE STREAM DIRECTO (SIN DESCARGAR VIDEO COMPLETO), SUBTÍTULOS E IA ---

def _obtener_cookies_path() -> str:
    cookies_usuario = USER_BASE / "cookies.txt"
    cookies_global = Path("cookies.txt")
    if cookies_usuario.exists():
        return str(cookies_usuario)
    if cookies_global.exists():
        return str(cookies_global)
    return ""

def obtener_stream_directo_url(url: str) -> str:
    """Obtiene la URL directa del stream sin descargar el video completo a disco."""
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--no-playlist",
        "--extractor-args", "youtube:player_client=web_safari,android,web",
        "-g",
        "-f", "best[height<=1080][ext=mp4]/best[ext=mp4]/best",
    ]
    cookies_path = _obtener_cookies_path()
    if cookies_path:
        cmd += ["--cookies", cookies_path]
    cmd.append(url)

    resultado = subprocess.run(cmd, capture_output=True, text=True)
    if resultado.returncode != 0 or not resultado.stdout.strip():
        cmd_av = [
            sys.executable, "-m", "yt_dlp",
            "--no-playlist",
            "--extractor-args", "youtube:player_client=web_safari,android,web",
            "-g",
            "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best",
        ]
        if cookies_path:
            cmd_av += ["--cookies", cookies_path]
        cmd_av.append(url)
        res_av = subprocess.run(cmd_av, capture_output=True, text=True)
        if res_av.returncode != 0 or not res_av.stdout.strip():
            err_msg = res_av.stderr.strip() or resultado.stderr.strip()
            raise Exception(f"No se pudo acceder al stream en vivo del enlace:\n{err_msg}")
        return res_av.stdout.strip().splitlines()[0].strip()

    return resultado.stdout.strip().splitlines()[0].strip()

def extraer_audio(fuente_video: str, proj_id: str, min_inicio: float = 0.0, min_fin: float = 0.0) -> str:
    """Extrae solo el audio ligero (MP3 32k) directo desde un archivo local o URL de stream."""
    audio_path = WORK_DIR / f"audio_{proj_id}.mp3"
    if audio_path.exists():
        audio_path.unlink()
    cmd = ["ffmpeg", "-y"]
    if min_inicio > 0:
        cmd += ["-ss", str(min_inicio * 60)]
    cmd += ["-i", fuente_video]
    if min_fin > min_inicio:
        cmd += ["-t", str((min_fin - min_inicio) * 60)]
    cmd += ["-vn", "-ac", "1", "-ar", "16000", "-acodec", "libmp3lame", "-b:a", "32k", str(audio_path)]

    resultado = subprocess.run(cmd, capture_output=True, text=True)
    if resultado.returncode != 0:
        raise Exception(f"Error al extraer el audio con FFmpeg:\n{resultado.stderr}")
    return str(audio_path)

def obtener_duracion_video(fuente_video: str) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", fuente_video
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        return round(float(res.stdout.strip()), 2)
    except Exception:
        return 60.0

def obtener_dimensiones_video(fuente_video: str):
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0:s=x", fuente_video
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        w, h = res.stdout.strip().split("x")
        return int(w), int(h)
    except Exception:
        return 1080, 1920

def agrupar_en_subtitulos_cortos(texto_con_tiempos: str, max_palabras: int = 4) -> list:
    bloques = []
    for linea in texto_con_tiempos.splitlines():
        linea = linea.strip()
        if not linea.startswith("[") or "]" not in linea:
            continue
        rango_str, frase = linea[1:].split("]", 1)
        frase = frase.strip()
        if not frase or "-" not in rango_str:
            continue
        try:
            ini_s = float(rango_str.split("-")[0].replace("s", "").strip())
            fin_s = float(rango_str.split("-")[1].replace("s", "").strip())
        except ValueError:
            continue

        palabras = frase.split()
        if not palabras:
            continue

        dur_total = max(0.4, fin_s - ini_s)
        num_chunks = max(1, (len(palabras) + max_palabras - 1) // max_palabras)
        paso_dur = dur_total / num_chunks

        for idx_bloque, i in enumerate(range(0, len(palabras), max_palabras)):
            sub_txt = " ".join(palabras[i:i + max_palabras])
            b_ini = round(ini_s + (idx_bloque * paso_dur), 2)
            b_fin = round(min(fin_s, b_ini + paso_dur), 2)
            if b_fin <= b_ini:
                b_fin = round(b_ini + 0.4, 2)
            bloques.append({"start": b_ini, "end": b_fin, "text": sub_txt})
    return bloques

def generar_subtitulos_desde_video(fuente_video: str, cfg: dict, max_palabras: int = 4) -> list:
    gr_key = cfg.get("groq_key", "").strip()
    oa_key = cfg.get("openai_key", "").strip()
    if gr_key:
        prov, llave = "groq", gr_key
    elif oa_key:
        prov, llave = "openai", oa_key
    else:
        raise Exception("Agrega una Groq API Key u OpenAI API Key en ⚙️ Opciones para generar subtítulos automáticos.")

    audio_tmp = extraer_audio(fuente_video, f"sub_{uuid.uuid4().hex[:8]}")
    try:
        transcripcion = transcribir_audio_whisper_api(audio_tmp, prov, llave)
        return agrupar_en_subtitulos_cortos(transcripcion, max_palabras=max_palabras)
    finally:
        if os.path.exists(audio_tmp):
            try:
                os.remove(audio_tmp)
            except Exception:
                pass

def generar_ass_con_posicion(
    subtitulos: list,
    ass_path: str,
    ancho_vid: int,
    alto_vid: int,
    fuente: str,
    tamano: int,
    color_ass: str,
    x_pct: int,
    y_pct: int
):
    pos_x = int((max(5, min(95, x_pct)) / 100.0) * ancho_vid)
    pos_y = int((max(8, min(92, y_pct)) / 100.0) * alto_vid)
    escala_font = max(12, int(round(tamano * (alto_vid / 1280.0) * 1.45)))

    header = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        f"PlayResX: {ancho_vid}\n"
        f"PlayResY: {alto_vid}\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{fuente},{escala_font},{color_ass},&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,5,20,20,20,1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )

    def fmt_ass(seg_val: float) -> str:
        seg_val = max(0.0, float(seg_val))
        h = int(seg_val // 3600)
        m = int((seg_val % 3600) // 60)
        s = int(seg_val % 60)
        cs = int(round((seg_val - int(seg_val)) * 100))
        if cs >= 100:
            cs = 99
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    eventos = []
    for item in subtitulos:
        txt_limpio = str(item.get("text", "")).replace("{", "").replace("}", "").replace("\n", " ").strip()
        if not txt_limpio:
            continue
        ini_ass = fmt_ass(item.get("start", 0.0))
        fin_ass = fmt_ass(item.get("end", 1.0))
        eventos.append(f"Dialogue: 0,{ini_ass},{fin_ass},Default,,0,0,0,,{{\\pos({pos_x},{pos_y})}}{txt_limpio}")

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(eventos) + "\n")

def quemar_subtitulos_en_video(
    input_video: str,
    output_video: str,
    subtitulos: list,
    fuente_nombre: str,
    tamano: int,
    color_ass: str,
    x_pct: int,
    y_pct: int
):
    if not subtitulos:
        raise Exception("No hay subtítulos para quemar.")

    w_vid, h_vid = obtener_dimensiones_video(input_video)
    ass_path = str(WORK_DIR / f"subs_{uuid.uuid4().hex[:8]}.ass")
    fuente_real = FUENTES_SUBTITULOS.get(fuente_nombre, "Arial Black")
    generar_ass_con_posicion(subtitulos, ass_path, w_vid, h_vid, fuente_real, tamano, color_ass, x_pct, y_pct)

    ass_ffmpeg = ass_path.replace("\\", "/").replace(":", "\\:")
    cmd = [
        "ffmpeg", "-y",
        "-i", input_video,
        "-vf", f"ass='{ass_ffmpeg}'",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "copy",
        output_video
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise Exception(f"Error al quemar subtítulos:\n{res.stderr}")
    finally:
        if os.path.exists(ass_path):
            try:
                os.remove(ass_path)
            except Exception:
                pass

def prompt_clips_pro(instruccion_usuario: str, num_clips: int, duracion_objetivo: str) -> str:
    return f"""
    Eres el asistente IA de edición de video estilo Nexus Clips.
    Analiza este audio y extrae los {num_clips} mejores momentos que cumplan EXACTAMENTE con lo que pide el creador.

    INSTRUCCIÓN DEL CREADOR: "{instruccion_usuario}"
    DURACIÓN OBJETIVO POR CLIP: {duracion_objetivo}

    REGLAS:
    - Los cortes deben empezar y terminar en frases completas.
    - Devuelve exclusivamente un JSON válido con una lista bajo la clave "clips".
    - Sé conciso en "motivo" y "subtitulos" (máximo 3 frases cortas por clip).
    - Cada clip debe incluir:
      - "titulo": título/gancho corto
      - "gancho_visual": texto ultra corto (3 a 6 palabras en MAYÚSCULAS)
      - "start": segundo exacto de inicio en el audio (float)
      - "end": segundo exacto de fin en el audio (float)
      - "motivo": razón breve de por qué este momento funciona
      - "puntaje_viral": entero del 1 al 100
      - "descripcion_redes": copy corto para TikTok/Shorts con hashtags
      - "subtitulos": lista de 2 a 3 frases cortas con "start", "end" y "text".
    """

def procesar_clips(texto_json: str, offset_seg: float = 0.0) -> list:
    limpio = texto_json.strip()
    if limpio.startswith("```"):
        lineas = limpio.splitlines()
        if len(lineas) >= 3:
            limpio = "\n".join(lineas[1:-1]).strip()
    data = json.loads(limpio)
    clips = data.get("clips", []) if isinstance(data, dict) else []
    resultado = []
    for c in clips:
        if not isinstance(c, dict):
            continue
        start_val = round(float(c.get("start", 0.0)) + float(offset_seg or 0.0), 2)
        end_val = round(float(c.get("end", start_val + 20.0)) + float(offset_seg or 0.0), 2)
        if end_val <= start_val:
            end_val = round(start_val + 20.0, 2)
        resultado.append({
            "titulo": str(c.get("titulo", "Clip viral")).strip(),
            "gancho_visual": str(c.get("gancho_visual", "")).strip(),
            "start": start_val,
            "end": end_val,
            "motivo": str(c.get("motivo", "Momento con buena retención.")).strip(),
            "puntaje_viral": int(c.get("puntaje_viral", 85)),
            "descripcion_redes": str(c.get("descripcion_redes", "")).strip(),
            "subtitulos": c.get("subtitulos", []) if isinstance(c.get("subtitulos"), list) else []
        })
    return resultado

def buscar_momentos_ia(audio_path: str, instruccion_usuario: str, num_clips: int, duracion_objetivo: str, offset_seg: float = 0.0):
    if not instruccion_usuario.strip():
        instruccion_usuario = "Elige automáticamente los momentos con mayor retención, gancho inicial y potencial viral."

    prompt = prompt_clips_pro(instruccion_usuario, num_clips, duracion_objetivo)
    tokens_salida = 3600 if num_clips > 5 else 2600
    texto_json, motor_usado = ejecutar_ia_con_respaldo(prompt, audio_path=audio_path, esperar_json=True, max_tokens=tokens_salida)
    clips = procesar_clips(texto_json, offset_seg)
    if not clips:
        raise Exception("La IA no devolvió clips válidos. Inténtalo de nuevo o cambia el motor en ⚙️ Opciones.")
    return clips, motor_usado

def analizar_clip_para_redes_ia(fuente_video: str, tono: str, contexto_extra: str = ""):
    audio_temp = extraer_audio(fuente_video, f"tk_{datetime.now().strftime('%H%M%S')}")
    prompt = f"""
    Eres un director creativo experto en viralidad de TikTok y YouTube Shorts.
    Analiza este clip y genera el mejor empaque viral posible.
    TONO DESEADO: "{tono}"
    CONTEXTO ADICIONAL DEL CREADOR (si hay): "{contexto_extra}"

    Devuelve exclusivamente un JSON válido con:
- "gancho_visual": frase explosiva de 3 a 6 palabras (en MAYÚSCULAS) para colocar en grande arriba del video.
- "titulos": lista de 5 títulos virales cortos para TikTok y YouTube Shorts (máximo 95 caracteres cada uno, con emojis).
- "descripcion": descripción corta con un llamado a la acción (CTA) que provoque comentarios.
- "hashtags": cadena con 5 a 8 hashtags relevantes y de alto alcance.
    """
    try:
        texto_json, motor_usado = ejecutar_ia_con_respaldo(prompt, audio_path=audio_temp, esperar_json=True)
    finally:
        if os.path.exists(audio_temp):
            try:
                os.remove(audio_temp)
            except Exception:
                pass
    return json.loads(texto_json), motor_usado

def buscar_tendencias_tiktok_ia(nicho: str, region: str, detalle_extra: str = ""):
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    prompt = f"""
    Hoy es {fecha_hoy}. Genera un resumen conciso y directo (sin rodeos) sobre qué temas y ganchos funcionan hoy en TikTok.
    NICHO: {nicho}
    PAÍS / REGIÓN: {region}
    ENFOQUE EXTRA: {detalle_extra if detalle_extra.strip() else "Lo más viral y con mayor retención actual"}

    Responde en español con formato limpio:
1. **🔥 Top 5 Temas en tendencia** (1 línea por tema).
2. **🎣 5 Ganchos (Hooks) de 3 segundos** (cortos y listos para usar).
3. **🎬 3 Ideas de clips** (1 línea por idea).
4. **🤖 Prompt molde para el Chat IA** (una frase exacta de máximo 2 líneas para buscar clips en videos largos).
    """
    return ejecutar_ia_con_respaldo(prompt, esperar_json=False, usar_google_search=True)

def clonar_formula_viral_ia(tiktok_url: str):
    proj_id = f"clon_{datetime.now().strftime('%H%M%S')}"
    stream_url = obtener_stream_directo_url(tiktok_url)
    dur = obtener_duracion_video(stream_url)
    a_path = extraer_audio(stream_url, proj_id)

    prompt = f"""
    Eres un experto en ingeniería inversa de videos virales de TikTok.
    Acabas de recibir el audio de un TikTok viral de {dur} segundos.
    Analízalo y extrae su FÓRMULA VIRAL EXACTA.

    Devuelve exclusivamente un JSON válido con estas claves:
- "gancho_3s": qué estrategia y frase exacta usó en los primeros 3 segundos para frenar el scroll.
- "ritmo_cortes": cómo mantiene la atención (ritmo, cambios de energía, suspenso).
- "duracion_ideal": duración recomendada para replicar esta fórmula (ej. "25 a 40 segundos").
- "tono": tono emocional dominante.
- "cta": qué llamado a la acción usó al final.
- "prompt_molde": una instrucción clara en español (de 2 a 3 líneas) lista para pegar en un buscador de clips IA y encontrar momentos con EXACTAMENTE esta misma fórmula en videos largos.
- "guion_estructura": plantilla breve de 4 pasos (Gancho -> Desarrollo -> Giro -> Cierre) para crear un video o título similar.
    """
    try:
        texto_json, motor_usado = ejecutar_ia_con_respaldo(prompt, audio_path=a_path, esperar_json=True)
    finally:
        if os.path.exists(a_path):
            try:
                os.remove(a_path)
            except Exception:
                pass

    datos = json.loads(texto_json)
    datos["stream_url"] = stream_url
    return datos, motor_usado

def formatear_tiempo_srt(segundos: float) -> str:
    segundos = max(0.0, float(segundos))
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segs = int(segundos % 60)
    ms = int((segundos - int(segundos)) * 1000)
    return f"{horas:02d}:{minutos:02d}:{segs:02d},{ms:03d}"

def generar_srt_clip(subtitulos: list, srt_filename: str):
    lineas = []
    for idx, seg in enumerate(subtitulos, start=1):
        lineas.append(f"{idx}\n{formatear_tiempo_srt(seg['start'])} --> {formatear_tiempo_srt(seg['end'])}\n{seg['text']}\n")
    with open(srt_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))

def renderizar_clip(
    fuente_video: str,
    start: float,
    end: float,
    output_path: str,
    layout: str,
    usar_subtitulos: bool,
    color_sub: str = "&H00FFFFFF",
    tamano_sub: int = 18,
    srt_filename: str = None,
    calidad: str = "HD (720p)",
    con_marca_agua: bool = False
):
    duracion = max(1.0, end - start)
    usar_sub = usar_subtitulos and srt_filename and os.path.exists(srt_filename)
    sub_style = f"FontName=Arial Black,FontSize={tamano_sub},PrimaryColour={color_sub},OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=55"
    srt_esc = srt_filename.replace("\\", "/").replace(":", "\\:") if srt_filename else ""
    sub_filter = f"subtitles='{srt_esc}':force_style='{sub_style}'" if usar_sub else ""
    watermark_filter = "drawtext=text='Mi Clipper':fontcolor=white@0.55:fontsize=24:box=1:boxcolor=black@0.35:boxborderw=6:x=w-tw-20:y=20"

    if con_marca_agua:
        w_v, h_v = 540, 960
        crf_val = "26"
    elif calidad == "Full HD (1080p)":
        w_v, h_v = 1080, 1920
        crf_val = "20"
    else:
        w_v, h_v = 720, 1280
        crf_val = "22"

    cmd = ["ffmpeg", "-y", "-ss", str(start), "-i", fuente_video, "-t", str(duracion)]

    if layout == "Imagen entera + fondo blur (9:16)":
        fc = (
            "[0:v]split[main][bg];"
            f"[bg]scale={w_v}:{h_v}:force_original_aspect_ratio=increase,crop={w_v}:{h_v},boxblur=20:5[bg_b];"
            f"[main]scale={w_v}:-2[fg];"
            "[bg_b][fg]overlay=(W-w)/2:(H-h)/2"
        )
        if usar_sub:
            fc += f",{sub_filter}"
        if con_marca_agua:
            fc += f",{watermark_filter}"
        cmd += ["-filter_complex", fc]

    elif layout == "Cuadrado centrado + fondo blur (9:16)":
        fc = (
            "[0:v]split[main][bg];"
            f"[bg]scale={w_v}:{h_v}:force_original_aspect_ratio=increase,crop={w_v}:{h_v},boxblur=20:5[bg_b];"
            f"[main]crop=min(iw\\,ih):min(iw\\,ih),scale={w_v}:{w_v}[fg];"
            "[bg_b][fg]overlay=(W-w)/2:(H-h)/2"
        )
        if usar_sub:
            fc += f",{sub_filter}"
        if con_marca_agua:
            fc += f",{watermark_filter}"
        cmd += ["-filter_complex", fc]

    else:
        filtros = []
        if layout == "Pantalla completa (9:16)":
            filtros.append(f"crop=ih*9/16:ih,scale={w_v}:{h_v}")
        elif layout == "Cuadrado (1:1)":
            filtros.append(f"crop=min(iw\\,ih):min(iw\\,ih),scale={w_v}:{w_v}")
        if usar_sub:
            filtros.append(sub_filter)
        if con_marca_agua:
            filtros.append(watermark_filter)
        if filtros:
            cmd += ["-vf", ",".join(filtros)]

    cmd += [
        "-c:v", "libx264", "-preset", "fast", "-crf", crf_val,
        "-c:a", "aac", "-b:a", "128k",
        output_path
    ]
    resultado = subprocess.run(cmd, capture_output=True, text=True)
    if resultado.returncode != 0:
        raise Exception(f"Error al renderizar con FFmpeg:\n{resultado.stderr}")

def editar_video_ffmpeg(input_path: str, output_path: str, start: float, end: float, velocidad: float, volumen: float, brillo: float, contraste: float, texto_hook: str):
    duracion = max(0.5, end - start)
    vf = []
    af = []

    if velocidad != 1.0:
        vf.append(f"setpts={round(1.0 / velocidad, 4)}*PTS")
        af.append(f"atempo={velocidad}")

    if brillo != 0.0 or contraste != 1.0:
        vf.append(f"eq=brightness={brillo}:contrast={contraste}")

    if texto_hook.strip():
        texto_limpio = texto_hook.strip().replace(":", "\\:").replace("'", "")
        vf.append(
            f"drawtext=text='{texto_limpio}':fontcolor=yellow:fontsize=46:"
            f"box=1:boxcolor=black@0.75:boxborderw=16:x=(w-text_w)/2:y=110"
        )

    if volumen != 1.0:
        af.append(f"volume={volumen}")

    cmd = ["ffmpeg", "-y", "-ss", str(start), "-i", input_path, "-t", str(duracion)]
    if vf:
        cmd += ["-vf", ",".join(vf)]
    if af:
        cmd += ["-af", ",".join(af)]

    cmd += [
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k",
        output_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise Exception(f"Error al editar el video:\n{res.stderr}")

def subir_video_tiktok_api(access_token: str, video_path: str, titulo: str):
    file_size = os.path.getsize(video_path)
    init_url = "[https://open.tiktokapis.com/v2/post/publish/inbox/video/init/](https://open.tiktokapis.com/v2/post/publish/inbox/video/init/)"
    payload = json.dumps({
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": file_size,
            "chunk_size": file_size,
            "total_chunk_count": 1
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        init_url,
        data=payload,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": BROWSER_UA
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        init_data = json.loads(resp.read().decode("utf-8"))

    upload_url = init_data.get("data", {}).get("upload_url")
    if not upload_url:
        raise Exception(f"TikTok no devolvió URL de subida: {init_data}")

    with open(video_path, "rb") as f:
        video_bytes = f.read()

    put_req = urllib.request.Request(
        upload_url,
        data=video_bytes,
        headers={
            "Content-Type": "video/mp4",
            "Content-Range": f"bytes 0-{file_size - 1}/{file_size}",
            "User-Agent": BROWSER_UA
        },
        method="PUT"
    )
    with urllib.request.urlopen(put_req, timeout=120) as put_resp:
        if put_resp.status not in (200, 201, 206):
            raise Exception(f"Error al subir archivo a TikTok (HTTP {put_resp.status})")
    return True

def ui_resultados(st_mod, clips_encontrados, video_path, proj_id, clips_dir, work_dir, es_pro, user_config, guardar_cfg_cb):
    st_mod.markdown('<span class="step-pill">PASO 3 · RESULTADOS</span>', unsafe_allow_html=True)
    st_mod.markdown("### Tus clips sugeridos")

    for i, clip in enumerate(clips_encontrados):
        with st_mod.expander(f"🎬 Clip #{i+1}: {clip['titulo']}  ·  🔥 {clip['puntaje_viral']}/100", expanded=True):
            col_info, col_render = st_mod.columns([1.8, 1.2])
            with col_info:
                st_mod.markdown(f'<span class="viral-badge">🔥 Viralidad {clip["puntaje_viral"]}/100</span>', unsafe_allow_html=True)
                st_mod.write(f"**Por qué funciona:** {clip['motivo']}")

                if es_pro:
                    if clip.get("gancho_visual"):
                        st_mod.markdown(f"**🎯 Gancho visual sugerido:** `{clip['gancho_visual']}`")
                    if clip.get("descripcion_redes"):
                        st_mod.info(f"**Magic Post (Copy para TikTok / YouTube):**\n\n{clip['descripcion_redes']}")

                    t1, t2 = st_mod.columns(2)
                    inicio = t1.number_input("Inicio (seg)", value=float(clip["start"]), key=f"start_{i}")
                    fin = t2.number_input("Fin (seg)", value=float(clip["end"]), key=f"end_{i}")

                    o1, o2 = st_mod.columns(2)
                    layout_clip = o1.selectbox("📐 Encuadre", LAYOUTS_VIDEO, index=0, key=f"lay_{i}")
                    calidad_clip = o2.selectbox("📺 Calidad de descarga", ["HD (720p)", "Full HD (1080p)"], index=1, key=f"cal_{i}")

                    s1, s2, s3 = st_mod.columns(3)
                    usar_sub = s1.checkbox("💬 Con subtítulos", value=True, key=f"usub_{i}")
                    color_nombre = s2.selectbox("🎨 Color subtítulos", list(COLORES_SUBTITULOS.keys()), index=0, key=f"col_{i}")
                    tamano_sub = s3.slider("🔠 Tamaño letra", 14, 28, 20, key=f"tam_{i}")
                    color_ass = COLORES_SUBTITULOS[color_nombre]
                else:
                    inicio = float(clip["start"])
                    fin = float(clip["end"])
                    layout_clip = "Pantalla completa (9:16)"
                    calidad_clip = "480p (Free)"
                    usar_sub = False
                    color_ass = "&H00FFFFFF"
                    tamano_sub = 18
                    st_mod.caption("🔒 Recorte manual, reencuadre, subtítulos de colores/tamaño y descarga HD/Full HD sin marca de agua están disponibles desde el **Plan Pro**.")

            with col_render:
                out_file = str(Path(clips_dir) / f"{proj_id}_clip_{i+1}.mp4")

                if st_mod.button(f"✂️ Crear Clip #{i+1}", type="primary", use_container_width=True, key=f"render_{i}"):
                    try:
                        with st_mod.spinner("Renderizando clip…"):
                            srt_temp = None
                            if usar_sub and clip.get("subtitulos"):
                                srt_temp = str(Path(work_dir) / f"temp_sub_{i+1}.srt")
                                generar_srt_clip(clip["subtitulos"], srt_temp)

                            renderizar_clip(
                                video_path,
                                inicio, fin, out_file,
                                layout=layout_clip,
                                usar_subtitulos=usar_sub,
                                color_sub=color_ass,
                                tamano_sub=tamano_sub,
                                srt_filename=srt_temp,
                                calidad=calidad_clip,
                                con_marca_agua=(not es_pro)
                            )
                            if srt_temp and os.path.exists(srt_temp):
                                os.remove(srt_temp)
                        st_mod.success("¡Clip listo!")
                    except Exception as e:
                        st_mod.error(str(e))

                if os.path.exists(out_file):
                    st_mod.video(out_file)
                    etiqueta_dl = f"⬇️ Descargar {calidad_clip}" if es_pro else "⬇️ Descargar (con marca de agua)"
                    with open(out_file, "rb") as f:
                        st_mod.download_button(
                            label=etiqueta_dl,
                            data=f,
                            file_name=f"clip_{i+1}_{proj_id}.mp4",
                            mime="video/mp4",
                            use_container_width=True,
                            key=f"dl_{i}"
                        )

# --- BARRA DE NAVEGACIÓN SUPERIOR SIEMPRE VISIBLE ---
nivel_plan_tmp, _ = obtener_estado_plan(st.session_state["usuario"]) if st.session_state.get("usuario") else ("FREE", "Plan Free")
es_super_pro_tmp = (nivel_plan_tmp == "SUPER_PRO")
usuario_es_admin_tmp = es_admin(st.session_state["usuario"]) if st.session_state.get("usuario") else False

opciones_menu = ["💬 Inicio (Chat IA)", "✂️ Editor y Redes", "📈 Tendencias TikTok", "👥 Comunidad", "📁 Mis Proyectos"]
if not es_super_pro_tmp and not usuario_es_admin_tmp:
    opciones_menu.append("💎 Planes / Key")
if usuario_es_admin_tmp:
    opciones_menu.append("👑 Panel Admin")

if st.session_state["pagina_actual"] not in opciones_menu:
    st.session_state["pagina_actual"] = opciones_menu[0]

nav_cols = st.columns(len(opciones_menu) + 1)
for idx, op in enumerate(opciones_menu):
    es_activa = (st.session_state["pagina_actual"] == op)
    if nav_cols[idx].button(
        op,
        key=f"top_nav_{idx}",
        type="primary" if es_activa else "secondary",
        use_container_width=True
    ):
        st.session_state["pagina_actual"] = op
        st.rerun()

if nav_cols[-1].button("🚪 Salir", key="top_nav_logout", use_container_width=True):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

# --- ESTADO DEL USUARIO ACTUAL (FREE / PRO / SUPER_PRO / ADMIN) ---
nivel_plan, texto_plan = obtener_estado_plan(st.session_state["usuario"])
es_pro = nivel_plan in ("PRO", "SUPER_PRO")
es_super_pro = (nivel_plan == "SUPER_PRO")
usuario_es_admin = es_admin(st.session_state["usuario"])

# --- RUTAS Y ARCHIVOS SEPARADOS POR USUARIO ---
USER_HASH = hashlib.md5(st.session_state["usuario"].encode()).hexdigest()[:12]
USER_BASE = Path("user_data") / USER_HASH
WORK_DIR = USER_BASE / "workspace"
CLIPS_DIR = USER_BASE / "clips_generados"
EDITED_DIR = USER_BASE / "clips_editados"
USER_CONFIG_FILE = USER_BASE / "config_usuario.json"
PROJECTS_FILE = USER_BASE / "proyectos.json"

WORK_DIR.mkdir(parents=True, exist_ok=True)
CLIPS_DIR.mkdir(parents=True, exist_ok=True)
EDITED_DIR.mkdir(parents=True, exist_ok=True)

def cargar_json(path: Path, default):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def guardar_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

user_config = cargar_json(USER_CONFIG_FILE, {})
proyectos = cargar_json(PROJECTS_FILE, [])

# ==============================================================================
# SKILLS DE AGENTE (INSTRUCCIONES DE ESTILO / SUBAGENTE)
# ==============================================================================
SKILLS_DISPONIBLES = {
    "⚡ Viral Sniper (Ganchos rápidos y retención)": "Prioriza cortes con gancho agresivo en los primeros 2 segundos, giros rápidos y frases que detienen el scroll.",
    "🎬 Storyteller / Subagente Narrativo": "Actúa como subagente narrativo: busca arcos completos con inicio, tensión y remate claro, sin cortar ideas a medias.",
    "🔥 Debate / Polémica / Contraste": "Enfócate en opiniones fuertes, comparaciones extremas, errores comunes y momentos que provoquen comentarios.",
    "🎓 Educativo / Valor Directo": "Extrae explicaciones claras, pasos prácticos, datos sorprendentes y conclusiones accionables."
}

def obtener_instruccion_skill() -> str:
    skill_sel = user_config.get("skill_ia", list(SKILLS_DISPONIBLES.keys())[0])
    return SKILLS_DISPONIBLES.get(skill_sel, "")

# --- BARRA LATERAL (ENGRANAJE "OPCIONES" + DEEPSEEK BETA + SKILL + ACTUALIZACIONES) ---
total_clips_creados = len(list(CLIPS_DIR.glob("*.mp4"))) + len(list(EDITED_DIR.glob("*.mp4")))

with st.sidebar:
    st.markdown('<div class="brand-logo">⚡ Mi Clipper IA</div>', unsafe_allow_html=True)
    st.caption(f"Studio Pro · v{VERSION_ACTUAL}")
    st.caption(f"👤 {st.session_state['usuario']}")
    if es_super_pro:
        st.success(f"🚀 {texto_plan}")
    elif es_pro:
        st.info(f"💎 {texto_plan}")
    else:
        st.warning("🆓 Plan Free (con marca de agua)")

    st.divider()
    with st.expander("⚙️ Opciones", expanded=False):
        opciones_motor = [
            "⚡ Ultra Rápido (Groq → DeepSeek → Gemini)",
            "DeepSeek · API Beta",
            "Solo Groq (Llama 3)",
            "Solo Gemini",
            "Automático (Gemini → Groq → DeepSeek → OpenAI)",
            "Solo OpenAI (GPT-4o-mini)"
        ]
        motor_actual = user_config.get("motor_ia", opciones_motor[0])
        if motor_actual not in opciones_motor:
            motor_actual = opciones_motor[0]

        motor_sel = st.selectbox("🧠 Motor:", opciones_motor, index=opciones_motor.index(motor_actual))

        lista_skills = list(SKILLS_DISPONIBLES.keys())
        skill_actual = user_config.get("skill_ia", lista_skills[0])
        if skill_actual not in lista_skills:
            skill_actual = lista_skills[0]
        skill_sel = st.selectbox("🧩 Skill / Subagente:", lista_skills, index=lista_skills.index(skill_actual))

        st.divider()
        st.markdown("**DeepSeek · con tu llave de API** <span class='beta-badge'>Beta</span>", unsafe_allow_html=True)
        st.caption("Trabaja con los modelos de DeepSeek: las skills y subagentes van igual que con Claude. Se cobra por uso, del saldo de tu cuenta de DeepSeek.")
        k_deepseek = st.text_input(
            "Añadir llave de DeepSeek",
            value=user_config.get("deepseek_key", ""),
            type="password",
            placeholder="sk-..."
        )
        st.caption("Está en beta: puedes probarlo, pero puede tener errores. Si te topas con uno, repórtalo en la Comunidad, en Ayuda.")

        st.divider()
        k_groq = st.text_input("Groq API Key:", value=user_config.get("groq_key", ""), type="password", placeholder="gsk_...")
        k_gemini = st.text_input("Gemini API Key:", value=user_config.get("api_key", ""), type="password", placeholder="AIza...")
        k_openai = st.text_input("OpenAI API Key:", value=user_config.get("openai_key", ""), type="password", placeholder="sk-...")

        if st.button("💾 Guardar opciones", type="primary", use_container_width=True):
            user_config["motor_ia"] = motor_sel
            user_config["skill_ia"] = skill_sel
            user_config["deepseek_key"] = k_deepseek.strip()
            user_config["api_key"] = k_gemini.strip()
            user_config["groq_key"] = k_groq.strip()
            user_config["openai_key"] = k_openai.strip()
            st.session_state.pop("gemini_agotado", None)
            st.session_state.pop("groq_modelos_lista", None)
            guardar_json(USER_CONFIG_FILE, user_config)
            st.success("¡Opciones guardadas!")

    if proyectos:
        st.divider()
        st.caption("PROYECTOS RECIENTES")
        for p in proyectos[:4]:
            if st.button(f"🎬 {p['nombre'][:22]}", key=f"side_p_{p['id']}", use_container_width=True):
                st.session_state["proyecto_activo"] = p
                st.session_state["ir_a_resultados"] = True
                st.session_state["pagina_actual"] = "💬 Inicio (Chat IA)"
                st.rerun()

    st.divider()
    if st.button("🔄 Buscar actualizaciones", use_container_width=True):
        st.session_state.pop("update_checked", None)
        st.session_state.pop("nueva_version", None)
        revisar_actualizacion()
        if "nueva_version" in st.session_state:
            st.rerun()
        else:
            st.toast(f"Ya tienes la última versión (v{VERSION_ACTUAL}).", icon="✅")

pagina = st.session_state["pagina_actual"]

# ==============================================================================
# PÁGINA 1: INICIO / CHAT IA
# ==============================================================================
if pagina == "💬 Inicio (Chat IA)":
    st.markdown("""
    <div class="hero-box">
        <div class="hero-title">¿Qué creamos hoy? ⚡</div>
        <div class="hero-sub">Analiza enlaces directo en vivo sin descargar el vídeo completo y genera clips virales.</div>
    </div>
    """, unsafe_allow_html=True)

    etiqueta_kpi_plan = "SUPER PRO" if es_super_pro else ("PRO" if es_pro else "FREE")
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="stat-card"><div class="stat-num">{total_clips_creados}</div><div class="stat-label">Clips Renderizados</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="stat-card"><div class="stat-num">{len(proyectos)}</div><div class="stat-label">Proyectos</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="stat-card"><div class="stat-num">{etiqueta_kpi_plan}</div><div class="stat-label">Tu Plan Actual</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="stat-card"><div class="stat-num">{"FULL HD" if es_pro else "480p"}</div><div class="stat-label">Calidad Máxima</div></div>', unsafe_allow_html=True)

    if not es_pro:
        st.info("🆓 Estás en **Plan Free**: tus clips se crearán con marca de agua pequeña (`Mi Clipper`) y opciones básicas. Sube a **Plan Pro** o **Super Pro** en **💎 Planes / Key**.")

    st.write("")

    if st.session_state.pop("ir_a_resultados", False) and "proyecto_activo" in st.session_state:
        p = st.session_state["proyecto_activo"]
        st.session_state["proj_id"] = p["id"]
        st.session_state["video_path"] = p.get("video_path") or p.get("stream_url", "")
        st.session_state["audio_path"] = p["audio_path"]
        st.session_state["clips_encontrados"] = p["clips"]
        st.session_state["nombre_proyecto"] = p["nombre"]

    # --- PASO 1 ---
    with st.container(border=True):
        st.markdown('<span class="step-pill">PASO 1 · PROCESAR EN VIVO</span>', unsafe_allow_html=True)
        st.markdown("### Conecta tu vídeo (sin descargar el archivo completo)")
        tab_link, tab_file = st.tabs(["🔗 Enlace directo (YouTube / Twitch / TikTok)", "📁 Subir desde mi PC"])

        col_r1, col_r2, col_r3 = st.columns([2, 1, 1])
        modo_rango = col_r1.radio("Rango del vídeo:", ["Todo el vídeo", "Solo una parte (vídeos largos)"], horizontal=True)
        min_ini, min_fin = 0.0, 0.0
        if modo_rango == "Solo una parte (vídeos largos)":
            min_ini = col_r2.number_input("Inicio (min)", min_value=0.0, value=0.0, step=1.0)
            min_fin = col_r3.number_input("Fin (min)", min_value=0.0, value=10.0, step=1.0)

        with tab_link:
            url_input = st.text_input("Pega el link aquí:", placeholder="[https://www.youtube.com/watch?v=](https://www.youtube.com/watch?v=)...")
            if st.button("⚡ Analizar enlace directo", type="primary", key="btn_import_url"):
                if not url_input:
                    st.warning("Pega un enlace primero.")
                else:
                    try:
                        proj_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                        with st.spinner("Obteniendo stream y extrayendo audio ligero en vivo..."):
                            stream_url = obtener_stream_directo_url(url_input.strip())
                            a_path = extraer_audio(stream_url, proj_id, min_ini, min_fin)
                        st.session_state["proj_id"] = proj_id
                        st.session_state["video_path"] = stream_url
                        st.session_state["audio_path"] = a_path
                        st.session_state["offset_seg"] = min_ini * 60
                        st.session_state["nombre_proyecto"] = f"Stream {proj_id}"
                        st.session_state.pop("clips_encontrados", None)
                        st.success("¡Stream conectado y audio listo sin descargar el vídeo completo! Configura el Paso 2 abajo.")
                    except Exception as e:
                        st.error(str(e))

        with tab_file:
            archivo = st.file_uploader("Arrastra tu MP4, MOV o MKV", type=["mp4", "mov", "mkv"])
            if archivo and st.button("⚙️ Preparar archivo", type="primary", key="btn_import_file"):
                try:
                    proj_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                    v_path = str(WORK_DIR / f"video_{proj_id}.mp4")
                    with open(v_path, "wb") as f:
                        f.write(archivo.read())
                    with st.spinner("Extrayendo audio ligero para la IA..."):
                        a_path = extraer_audio(v_path, proj_id, min_ini, min_fin)
                    st.session_state["proj_id"] = proj_id
                    st.session_state["video_path"] = v_path
                    st.session_state["audio_path"] = a_path
                    st.session_state["offset_seg"] = min_ini * 60
                    st.session_state["nombre_proyecto"] = archivo.name
                    st.session_state.pop("clips_encontrados", None)
                    st.success("¡Archivo listo! Ahora configura el Paso 2 abajo.")
                except Exception as e:
                    st.error(str(e))

    # --- PASO 2 ---
    if "audio_path" in st.session_state:
        with st.container(border=True):
            st.markdown('<span class="step-pill">PASO 2 · INTELIGENCIA ARTIFICIAL</span>', unsafe_allow_html=True)
            st.markdown("### Dile al chat qué momentos buscar")

            c1, c2, c3, c4, c5 = st.columns(5)
            if c1.button("✨ Automático", use_container_width=True):
                st.session_state["prompt_chat"] = "Encuentra los mejores momentos con mayor gancho inicial y potencial viral."
            if c2.button("😂 Graciosos", use_container_width=True):
                st.session_state["prompt_chat"] = "Busca los momentos más graciosos, bromas, risas y reacciones divertidas."
            if c3.button("🧠 Consejos", use_container_width=True):
                st.session_state["prompt_chat"] = "Extrae cada consejo práctico, explicación de valor o dato clave."
            if c4.button("🔥 Polémica", use_container_width=True):
                st.session_state["prompt_chat"] = "Encuentra las opiniones más polémicas, debates o declaraciones fuertes."
            if c5.button("📖 Historias", use_container_width=True):
                st.session_state["prompt_chat"] = "Busca las mejores anécdotas o historias completas de principio a fin."

            instruccion = st.text_area(
                "Instrucción personalizada (opcional):",
                value=st.session_state.get("prompt_chat", ""),
                placeholder="p. ej. los momentos más graciosos, cada consejo sobre dinero, o una fórmula clonada desde Tendencias TikTok…"
            )

            max_clips = 10 if es_super_pro else (6 if es_pro else 3)
            a1, a2 = st.columns(2)
            num_clips = a1.slider(f"🎞️ Cantidad de clips (máx {max_clips} en tu plan)", 1, max_clips, min(3, max_clips))
            duracion_obj = a2.selectbox("⏱️ Duración", ["15 a 30 segundos", "30 a 60 segundos", "60 a 90 segundos"], index=1)

            if st.button("🚀 Buscar momentos con IA", type="primary", use_container_width=True):
                try:
                    t0 = time.time()
                    with st.spinner("⚡ Analizando audio y detectando los mejores clips…"):
                        clips, motor_usado = buscar_momentos_ia(
                            st.session_state["audio_path"],
                            instruccion,
                            num_clips,
                            duracion_obj,
                            st.session_state.get("offset_seg", 0.0)
                        )
                        st.session_state["clips_encontrados"] = clips

                        nuevo_proj = {
                            "id": st.session_state["proj_id"],
                            "nombre": st.session_state.get("nombre_proyecto", "Proyecto sin título"),
                            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "video_path": st.session_state["video_path"],
                            "audio_path": st.session_state["audio_path"],
                            "clips": clips
                        }
                        proyectos = [p for p in proyectos if p["id"] != nuevo_proj["id"]]
                        proyectos.insert(0, nuevo_proj)
                        guardar_json(PROJECTS_FILE, proyectos)

                    st.success(f"¡Listo en {time.time() - t0:.1f}s! Encontré {len(clips)} momentos virales usando **{motor_usado}**.")
                except Exception as e:
                    st.error(str(e))

    # --- PASO 3 ---
    if "clips_encontrados" in st.session_state:
        ui_resultados(
            st,
            st.session_state["clips_encontrados"],
            st.session_state["video_path"],
            st.session_state.get("proj_id", "local"),
            CLIPS_DIR,
            WORK_DIR,
            es_pro,
            user_config,
            lambda: guardar_json(USER_CONFIG_FILE, user_config)
        )

# ==============================================================================
# PÁGINA 2: EDITOR DE VIDEO (VISTA PREVIA EN VIVO) + SUBTÍTULOS + REDES
# ==============================================================================
elif pagina == "✂️ Editor y Redes":
    st.markdown("""
    <div class="hero-box">
        <div class="hero-title">Editor Studio & Publicación 🎵</div>
        <div class="hero-sub">Recorta, ajusta brillo/contraste en vivo, genera y mueve subtítulos, y publica en tus redes.</div>
    </div>
    """, unsafe_allow_html=True)

    if not es_pro:
        with st.container(border=True):
            st.warning("🔒 **Función disponible desde el Plan Pro**")
            st.markdown("""
            Con **Plan Pro** o **Super Pro** desbloqueas:
- ✂️ Editor avanzado (recortar, velocidad, brillo y contraste con vista previa en vivo)
- 💬 Generador de subtítulos con posición libre, tamaño, tipografía y descarga `.SRT`
- ✨ Generador automático de **5 Títulos Virales + Descripción + Hashtags con IA**
- 🚀 Publicación en **TikTok y YouTube** con el texto ya escrito
            """)
            if st.button("💎 Ver Planes Pro / Super Pro", type="primary"):
                st.session_state["pagina_actual"] = "💎 Planes / Key"
                st.rerun()
        st.stop()

    clips_disponibles = sorted(list(CLIPS_DIR.glob("*.mp4")) + list(EDITED_DIR.glob("*.mp4")), key=os.path.getmtime, reverse=True)
    opciones_video = [str(p) for p in clips_disponibles]

    with st.container(border=True):
        col_sel1, col_sel2 = st.columns([2, 1])
        video_elegido = None
        with col_sel1:
            if opciones_video:
                video_elegido = st.selectbox("🎬 Elige un clip de tu biblioteca:", opciones_video, format_func=lambda x: Path(x).name)
            else:
                st.info("Aún no tienes clips generados. Sube un MP4 a la derecha o crea uno en Inicio.")
        with col_sel2:
            subido_extra = st.file_uploader("O sube otro MP4", type=["mp4", "mov"])
            if subido_extra:
                ruta_extra = str(WORK_DIR / f"extra_{subido_extra.name}")
                with open(ruta_extra, "wb") as f:
                    f.write(subido_extra.read())
                video_elegido = ruta_extra

    if video_elegido and os.path.exists(video_elegido):
        dur_total = obtener_duracion_video(video_elegido)

        st.session_state.setdefault("sub_x_pct", 50)
        st.session_state.setdefault("sub_y_pct", 82)
        st.session_state.setdefault("sub_tam_val", 22)
        st.session_state.setdefault("sub_fuente_val", list(FUENTES_SUBTITULOS.keys())[0])
        st.session_state.setdefault("sub_color_val", "Amarillo viral")

        with st.container(border=True):
            st.markdown('<span class="step-pill">IA AUTOMÁTICA · GANCHO Y TÍTULOS</span>', unsafe_allow_html=True)
            st.markdown("### Que la IA escuche tu clip y cree el Gancho + Títulos")
            g1, g2 = st.columns([1.2, 2])
            tono_video = g1.selectbox("Estilo / Tono viral", ["Curioso / Misterio", "Gracioso / Dinámico", "Polémico / Debate", "Educativo / Directo"])
            contexto_extra = g2.text_input("Nota extra para la IA (opcional):", placeholder="Ej: Enfócate en el giro del final...")

            if st.button("✨ Analizar este clip con IA (Auto-Gancho + 5 Títulos)", type="primary", use_container_width=True):
                try:
                    with st.spinner("⚡ Creando Gancho visual y Títulos..."):
                        res_ia, motor_usado = analizar_clip_para_redes_ia(video_elegido, tono_video, contexto_extra)
                        st.session_state["tiktok_ia"] = res_ia
                        st.session_state["hook_auto"] = res_ia.get("gancho_visual", "")
                    st.success(f"¡Gancho visual y títulos generados con **{motor_usado}**!")
                except Exception as e:
                    st.error(str(e))

        with st.container(border=True):
            st.markdown('<span class="step-pill">EDITOR DE VIDEO Y SUBTÍTULOS</span>', unsafe_allow_html=True)
            col_prev, col_edit = st.columns([1.05, 1.45])

            with col_edit:
                tab_ed_video, tab_ed_subs = st.tabs(["🎛️ Video, Brillo y Contraste", "💬 Subtítulos, Posición y Letras"])

                with tab_ed_video:
                    r1, r2 = st.columns(2)
                    ed_ini = r1.number_input("Recortar inicio (seg)", min_value=0.0, max_value=dur_total, value=0.0, step=0.5, key="ed_ini_val")
                    ed_fin = r2.number_input("Recortar fin (seg)", min_value=0.5, max_value=dur_total, value=dur_total, step=0.5, key="ed_fin_val")

                    e1, e2 = st.columns(2)
                    velocidad = e1.select_slider("Velocidad", options=[0.75, 1.0, 1.25, 1.5, 2.0], value=1.0, key="ed_vel_val")
                    volumen = e2.slider("Volumen", 0.0, 2.0, 1.0, 0.1, key="ed_vol_val")

                    b_col, c_col = st.columns(2)
                    brillo = b_col.slider("☀️ Brillo (en vivo)", -0.5, 0.5, 0.0, 0.02, key="ed_bri_val")
                    contraste = c_col.slider("🌗 Contraste (en vivo)", 0.4, 2.0, 1.0, 0.05, key="ed_con_val")

                    texto_hook = st.text_input(
                        "🎯 Texto Gancho (Hook) arriba del video:",
                        value=st.session_state.get("hook_auto", ""),
                        placeholder="Escribe un gancho o genéralo con IA arriba...",
                        key="ed_hook_val"
                    )

                    btn_rapido, btn_full = st.columns(2)
                    if btn_rapido.button("⚡ Probar muestra (5s)", use_container_width=True):
                        try:
                            muestra_path = str(EDITED_DIR / f"muestra_{datetime.now().strftime('%H%M%S')}_{Path(video_elegido).name}")
                            fin_muestra = min(ed_fin, ed_ini + 5.0)
                            with st.spinner("Generando muestra rápida de 5s..."):
                                editar_video_ffmpeg(
                                    video_elegido, muestra_path, ed_ini, fin_muestra,
                                    velocidad, volumen, brillo, contraste, texto_hook
                                )
                            st.session_state["video_editado_actual"] = muestra_path
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

                    if btn_full.button("✂️ Aplicar edición y quemar Gancho", type="primary", use_container_width=True):
                        try:
                            nombre_editado = str(EDITED_DIR / f"editado_{datetime.now().strftime('%H%M%S')}_{Path(video_elegido).name}")
                            with st.spinner("Aplicando edición en el video..."):
                                editar_video_ffmpeg(
                                    video_elegido, nombre_editado, ed_ini, ed_fin,
                                    velocidad, volumen, brillo, contraste, texto_hook
                                )
                            st.session_state["video_editado_actual"] = nombre_editado
                            st.success("¡Video editado con éxito!")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

                with tab_ed_subs:
                    st.markdown("**Recetas rápidas de subtítulos:**")
                    p_cols = st.columns(len(PRESETS_SUBTITULOS))
                    for idx_p, (nombre_p, cfg_p) in enumerate(PRESETS_SUBTITULOS.items()):
                        if p_cols[idx_p].button(nombre_p, key=f"preset_sub_{idx_p}", use_container_width=True):
                            st.session_state["sub_color_val"] = cfg_p["color"]
                            st.session_state["sub_tam_val"] = cfg_p["tamano"]
                            st.session_state["sub_x_pct"] = cfg_p["x_pct"]
                            st.session_state["sub_y_pct"] = cfg_p["y_pct"]
                            st.session_state["sub_fuente_val"] = cfg_p["fuente"]
                            st.rerun()

                    g_c1, g_c2 = st.columns([1.6, 1])
                    max_pal_sub = g_c1.slider("Palabras por bloque de subtítulo", 2, 8, 4, key="sub_max_pal_slider")
                    with g_c2:
                        st.write("")
                        if st.button("🎙️ Generar subtítulos", type="primary", use_container_width=True, key="btn_generar_subs_auto"):
                            try:
                                with st.spinner("Transcribiendo audio y generando subtítulos..."):
                                    subs_gen = generar_subtitulos_desde_video(video_elegido, user_config, max_palabras=max_pal_sub)
                                st.session_state["subs_lista_ed"] = subs_gen
                                st.session_state["subs_texto_ed"] = json.dumps(subs_gen, indent=2, ensure_ascii=False)
                                st.success(f"¡{len(subs_gen)} subtítulos generados!")
                            except Exception as e:
                                st.error(str(e))

                    st.divider()
                    f_c1, f_c2, f_c3 = st.columns([1.5, 1.1, 1.1])
                    fuente_sel = f_c1.selectbox("🔤 Tipo de letra", list(FUENTES_SUBTITULOS.keys()), key="sub_fuente_val")
                    color_sel = f_c2.selectbox("🎨 Color", list(COLORES_SUBTITULOS.keys()), key="sub_color_val")
                    tamano_sel = f_c3.slider("🔍 Agrandar / Achicar", 12, 42, key="sub_tam_val")

                    st.markdown("**📍 Mover subtítulo en el video:**")
                    at_1, at_2, at_3 = st.columns(3)
                    if at_1.button("⬆️ Arriba", key="pos_arriba", use_container_width=True):
                        st.session_state["sub_y_pct"] = 18
                        st.rerun()
                    if at_2.button("⏺️ Centro", key="pos_centro", use_container_width=True):
                        st.session_state["sub_y_pct"] = 50
                        st.rerun()
                    if at_3.button("⬇️ Abajo", key="pos_abajo", use_container_width=True):
                        st.session_state["sub_y_pct"] = 82
                        st.rerun()

                    pos_c1, pos_c2 = st.columns(2)
                    x_pct_sel = pos_c1.slider("Horizontal (Izq ↔ Der %)", 10, 90, key="sub_x_pct")
                    y_pct_sel = pos_c2.slider("Vertical (Arriba ↕ Abajo %)", 10, 90, key="sub_y_pct")

                    texto_sub_prueba = st.text_input(
                        "Texto de muestra en vista previa:",
                        value=(st.session_state.get("subs_lista_ed", [{}])[0].get("text") if st.session_state.get("subs_lista_ed") else "ASÍ SE VERÁ TU SUBTÍTULO"),
                        key="sub_muestra_txt"
                    )

                    if "subs_texto_ed" in st.session_state:
                        subs_json_raw = st.text_area(
                            "Editar segmentos de subtítulos (JSON):",
                            value=st.session_state["subs_texto_ed"],
                            height=140,
                            key="ta_subs_editor_json"
                        )
                    else:
                        subs_json_raw = None

                    q_c1, q_c2 = st.columns(2)
                    with q_c1:
                        if st.button("🔥 Quemar subtítulos en el video", type="primary", use_container_width=True, key="btn_quemar_subs_pos"):
                            try:
                                if subs_json_raw:
                                    lista_final = json.loads(subs_json_raw)
                                    st.session_state["subs_texto_ed"] = subs_json_raw
                                    st.session_state["subs_lista_ed"] = lista_final
                                elif texto_sub_prueba.strip():
                                    lista_final = [{"start": 0.0, "end": max(1.0, dur_total), "text": texto_sub_prueba.strip()}]
                                else:
                                    raise Exception("Genera subtítulos o escribe un texto primero.")

                                salida_sub_vid = str(EDITED_DIR / f"subtitulado_{datetime.now().strftime('%H%M%S')}_{Path(video_elegido).name}")
                                with st.spinner("Quemando subtítulos con posición y estilo en el video..."):
                                    quemar_subtitulos_en_video(
                                        video_elegido,
                                        salida_sub_vid,
                                        lista_final,
                                        fuente_nombre=fuente_sel,
                                        tamano=tamano_sel,
                                        color_ass=COLORES_SUBTITULOS[color_sel],
                                        x_pct=x_pct_sel,
                                        y_pct=y_pct_sel
                                    )
                                st.session_state["video_editado_actual"] = salida_sub_vid
                                st.success("¡Subtítulos quemados en el video!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"No se pudieron quemar los subtítulos: {e}")

                    with q_c2:
                        if subs_json_raw:
                            try:
                                datos_srt = json.loads(subs_json_raw)
                                ruta_srt_dl = str(WORK_DIR / f"subtitulos_{USER_HASH}.srt")
                                generar_srt_clip(datos_srt, ruta_srt_dl)
                                with open(ruta_srt_dl, "rb") as f_srt:
                                    st.download_button(
                                        "⬇️ Descargar .SRT",
                                        data=f_srt,
                                        file_name=f"{Path(video_elegido).stem}.srt",
                                        mime="text/plain",
                                        use_container_width=True,
                                        key="btn_descargar_srt_editor"
                                    )
                            except Exception:
                                st.caption("Revisa la sintaxis del JSON para descargar .SRT.")

            with col_prev:
                st.markdown("#### 📺 Vista previa en vivo")
                video_a_mostrar = st.session_state.get("video_editado_actual", video_elegido)
                if not os.path.exists(video_a_mostrar):
                    video_a_mostrar = video_elegido

                ass_hex = COLORES_SUBTITULOS.get(color_sel, "&H0000FFFF").replace("&H", "").strip()
                if len(ass_hex) == 8:
                    hex_css = f"#{ass_hex[6:8]}{ass_hex[4:6]}{ass_hex[2:4]}"
                else:
                    hex_css = "#facc15"

                css_brillo = max(0.1, 1.0 + (brillo * 1.4))
                filtro_css = f"brightness({css_brillo:.2f}) contrast({contraste:.2f})"
                font_css = FUENTES_SUBTITULOS.get(fuente_sel, "Arial Black")
                tam_preview_px = max(12, int(round(tamano_sel * 0.95)))

                hook_overlay_html = ""
                if texto_hook.strip():
                    hook_overlay_html = f"""
                    <div style="
                        position:absolute; top:8%; left:50%; transform:translateX(-50%);
                        z-index:12; background:rgba(0,0,0,0.78); color:#facc15;
                        padding:6px 14px; border-radius:10px; font-weight:800;
                        font-size:0.95rem; text-align:center; max-width:90%;
                        pointer-events:none;
                    ">{texto_hook.strip()}</div>
                    """

                sub_overlay_html = ""
                if texto_sub_prueba.strip():
                    sub_overlay_html = f"""
                    <div style="
                        position:absolute; left:{x_pct_sel}%; top:{y_pct_sel}%;
                        transform:translate(-50%, -50%);
                        z-index:15; color:{hex_css}; font-family:'{font_css}', sans-serif;
                        font-size:{tam_preview_px}px; font-weight:800;
                        text-shadow: 0 2px 6px rgba(0,0,0,0.95), 0 0 2px #000;
                        text-align:center; max-width:88%; line-height:1.15;
                        pointer-events:none;
                    ">{texto_sub_prueba.strip()}</div>
                    """

                st.markdown(f"""
                <style>
                    .preview-stage-{USER_HASH} {{
                        position: relative;
                        width: 100%;
                        border-radius: 14px;
                        overflow: hidden;
                        background: #05050a;
                        border: 1px solid rgba(139, 92, 246, 0.35);
                    }}
                    .preview-stage-{USER_HASH} video {{
                        width: 100% !important;
                        display: block;
                        filter: {filtro_css} !important;
                        transition: filter 0.12s ease;
                    }}
                </style>
                <div class="preview-stage-{USER_HASH}">
                    {hook_overlay_html}
                    {sub_overlay_html}
                """, unsafe_allow_html=True)

                if video_a_mostrar == video_elegido and (ed_ini > 0 or ed_fin < dur_total):
                    st.video(video_a_mostrar, start_time=int(ed_ini), end_time=int(ed_fin))
                else:
                    st.video(video_a_mostrar)

                st.markdown("</div>", unsafe_allow_html=True)
                st.caption(
                    f"Brillo: {brillo:+.2f} · Contraste: {contraste:.2f} · "
                    f"Subtítulo en ({x_pct_sel}%, {y_pct_sel}%) · Tamaño {tamano_sel}"
                )

        with st.container(border=True):
            st.markdown('<span class="step-pill">PUBLICAR EN TIKTOK Y YOUTUBE</span>', unsafe_allow_html=True)
            titulo_final = ""
            if "tiktok_ia" in st.session_state:
                datos_tk = st.session_state["tiktok_ia"]
                titulo_elegido = st.radio("🏆 Elige uno de los 5 títulos generados por la IA:", datos_tk["titulos"])
                caption_sugerido = f"{titulo_elegido}\n\n{datos_tk['descripcion']}\n\n{datos_tk['hashtags']}"
                titulo_final = st.text_area("📝 Texto final para TikTok / YouTube Shorts:", value=caption_sugerido, height=130)
            else:
                titulo_final = st.text_area("📝 Texto para TikTok / YouTube (usa el botón de IA arriba para generarlo solo):", height=100)

            video_final_subir = st.session_state.get("video_editado_actual", video_elegido)
            if not os.path.exists(video_final_subir):
                video_final_subir = video_elegido

            b1, b2, b3 = st.columns(3)
            with b1:
                with open(video_final_subir, "rb") as f:
                    st.download_button(
                        "⬇️ Descargar HD sin marca",
                        data=f,
                        file_name=Path(video_final_subir).name,
                        mime="video/mp4",
                        type="primary",
                        use_container_width=True
                    )
            with b2:
                st.link_button("🎵 Publicar en TikTok Studio", "[https://www.tiktok.com/tiktokstudio/upload](https://www.tiktok.com/tiktokstudio/upload)", use_container_width=True)
            with b3:
                st.link_button("▶️ Publicar en YouTube Studio", "[https://studio.youtube.com/channel/UC/videos/upload](https://studio.youtube.com/channel/UC/videos/upload)", use_container_width=True)

            with st.expander("🔌 Opcional: Subida directa a TikTok por API"):
                tk_tok = st.text_input("Tu TikTok Access Token:", value=user_config.get("tiktok_token", ""), type="password")
                if st.button("🚀 Subir directo a TikTok (API)"):
                    if not tk_tok.strip():
                        st.warning("Ingresa tu TikTok Access Token.")
                    else:
                        user_config["tiktok_token"] = tk_tok.strip()
                        guardar_json(USER_CONFIG_FILE, user_config)
                        try:
                            with st.spinner("Subiendo video a tu TikTok..."):
                                subir_video_tiktok_api(tk_tok.strip(), video_final_subir, titulo_final)
                            st.success("¡Enviado a tu cuenta de TikTok! Revisa tus borradores.")
                        except Exception as e:
                            st.error(f"Error al subir vía API: {e}")

# ==============================================================================
# PÁGINA 3: RADAR DE TENDENCIAS TIKTOK + CLONADOR VIRAL (EXCLUSIVO SUPER PRO)
# ==============================================================================
elif pagina == "📈 Tendencias TikTok":
    st.markdown("""
    <div class="hero-box">
        <div class="hero-title">Radar de Tendencias TikTok 📈</div>
        <div class="hero-sub">Descubre qué está explotando hoy en tiempo real o clona la fórmula exacta de cualquier TikTok viral.</div>
    </div>
    """, unsafe_allow_html=True)

    if not es_super_pro:
        with st.container(border=True):
            st.warning("🔒 **Función exclusiva del Plan SUPER PRO**")
            st.markdown("""
            Sube al **Plan Super Pro** para desbloquear:
- 🔎 **Buscador de Tendencias en Vivo (Groq / DeepSeek / Gemini / OpenAI):** qué temas, formatos y ganchos explotan HOY en tu nicho y país.
- 🧬 **Clonador de Fórmula Viral:** pega el link de cualquier TikTok viral, extrae su gancho de 3 segundos, ritmo y CTA, y úsalo como molde en tus propios videos con un clic.
- 🎞️ Hasta **10 clips** por video.
            """)
            if st.button("🚀 Subir a Plan Super Pro", type="primary"):
                st.session_state["pagina_actual"] = "💎 Planes / Key"
                st.rerun()
        st.stop()

    tab_vivo, tab_clonar = st.tabs(["🔎 Buscador de Tendencias en Vivo", "🧬 Clonador de Fórmula Viral"])

    with tab_vivo:
        with st.container(border=True):
            st.markdown('<span class="step-pill">RADAR IA MULTI-MOTOR EN VIVO</span>', unsafe_allow_html=True)
            st.markdown("### ¿Qué está explotando hoy en TikTok?")
            t1, t2 = st.columns(2)
            nicho = t1.selectbox(
                "🎯 Elige tu nicho:",
                ["Misterio / Terror / True Crime", "Humor / Entretenimiento", "Finanzas / Negocios / Cripto", "Gaming / Streamers", "Noticias / Polémica", "Salud / Fitness", "Tecnología / IA", "Historias / Podcasts"]
            )
            region = t2.selectbox(
                "🌎 País / Región:",
                ["Perú", "Latinoamérica (General)", "México", "Colombia", "Argentina", "España", "Estados Unidos (Español)", "Estados Unidos (Inglés)"]
            )
            extra_trend = st.text_input("Tema específico (opcional):", placeholder="Ej: historias de terror cortas, reacciones de streamers, consejos de ahorro...")

            if st.button("📡 Escanear tendencias de hoy", type="primary", use_container_width=True):
                try:
                    t0 = time.time()
                    with st.spinner(f"⚡ Escaneando tendencias de {nicho} en {region}..."):
                        resultado_trend, motor_usado = buscar_tendencias_tiktok_ia(nicho, region, extra_trend)
                        st.session_state["resultado_tendencias"] = resultado_trend
                        st.session_state["motor_tendencias"] = f"{motor_usado} · {time.time() - t0:.1f}s"
                except Exception as e:
                    st.error(str(e))

        if "resultado_tendencias" in st.session_state:
            with st.container(border=True):
                st.caption(f"Generado con: **{st.session_state.get('motor_tendencias', 'IA')}**")
                st.markdown(st.session_state["resultado_tendencias"])

    with tab_clonar:
        with st.container(border=True):
            st.markdown('<span class="step-pill">INGENIERÍA INVERSA VIRAL</span>', unsafe_allow_html=True)
            st.markdown("### Clona la fórmula de un TikTok en tendencia")
            url_tk = st.text_input("🔗 Pega el link del TikTok viral aquí:", placeholder="[https://www.tiktok.com/@usuario/video/](https://www.tiktok.com/@usuario/video/)...")

            if st.button("🧬 Analizar y extraer fórmula viral", type="primary", use_container_width=True):
                if not url_tk.strip():
                    st.warning("Pega un enlace de TikTok primero.")
                else:
                    try:
                        with st.spinner("⚡ Conectando al stream de TikTok y extrayendo fórmula viral..."):
                            formula, motor_usado = clonar_formula_viral_ia(url_tk.strip())
                            st.session_state["formula_clonada"] = formula
                        st.success(f"¡Fórmula viral extraída con **{motor_usado}**!")
                    except Exception as e:
                        st.error(str(e))

        if "formula_clonada" in st.session_state:
            f = st.session_state["formula_clonada"]
            with st.container(border=True):
                col_v, col_f = st.columns([1, 1.6])
                with col_v:
                    if f.get("stream_url"):
                        st.video(f["stream_url"])
                with col_f:
                    st.markdown(f"**🎣 Gancho (primeros 3 seg):** {f.get('gancho_3s', '')}")
                    st.markdown(f"**⚡ Ritmo y cortes:** {f.get('ritmo_cortes', '')}")
                    st.markdown(f"**⏱️ Duración ideal:** {f.get('duracion_ideal', '')}")
                    st.markdown(f"**🎭 Tono:** {f.get('tono', '')}")
                    st.markdown(f"**💬 Llamado a la acción (CTA):** {f.get('cta', '')}")
                    st.info(f"**📋 Estructura / Guion molde:**\n\n{f.get('guion_estructura', '')}")
                    st.markdown("**🤖 Prompt molde listo para tus videos largos:**")
                    st.code(f.get("prompt_molde", ""), language="text")

                    if st.button("🎯 Usar esta fórmula en Inicio (Chat IA)", type="primary", use_container_width=True):
                        st.session_state["prompt_chat"] = f.get("prompt_molde", "")
                        st.session_state["pagina_actual"] = "💬 Inicio (Chat IA)"
                        st.rerun()

# ==============================================================================
# PÁGINA 3B: COMUNIDAD (OPINIONES, COMENTARIOS, ESTADÍSTICAS Y VOTACIÓN)
# ==============================================================================
elif pagina == "👥 Comunidad":
    st.markdown("""
    <div class="hero-box">
        <div class="hero-title">Comunidad Clipper IA 👥</div>
        <div class="hero-sub">Comparte tus opiniones, pide ideas, comenta los clips de otros creadores y vota qué sigue.</div>
    </div>
    """, unsafe_allow_html=True)

    datos_comm = obtener_datos_comunidad()
    nombre_actual = obtener_nombre_comunidad(st.session_state["usuario"])

    col_feed, col_stats = st.columns([2.2, 1])

    with col_feed:
        with st.container(border=True):
            st.markdown("### ✍️ Nueva publicación o opinión")
            c_cat, c_tit = st.columns([1, 2])
            cat_post = c_cat.selectbox("Categoría", ["General", "Mejoras", "Lo que hice", "Dudas"])
            tit_post = c_tit.text_input("Título corto", placeholder="Ej: Mi truco para ganchos en TikTok...")
            txt_post = st.text_area("Comparte tu opinión, duda o experiencia:", placeholder="Escribe aquí lo que opinas o qué quieres compartir con la comunidad...", height=95)

            if st.button("📢 Publicar en la Comunidad", type="primary", use_container_width=True):
                if not txt_post.strip():
                    st.warning("Escribe un mensaje antes de publicar.")
                else:
                    titulo_final_post = tit_post.strip() if tit_post.strip() else f"Opinión de {nombre_actual}"
                    crear_post_comunidad(
                        st.session_state["usuario"],
                        nombre_actual,
                        cat_post,
                        titulo_final_post,
                        txt_post
                    )
                    st.success("¡Publicado en la comunidad!")
                    st.rerun()

        st.write("")
        filtro_cat = st.radio(
            "Filtrar publicaciones:",
            ["Todos", "General", "Mejoras", "Lo que hice", "Dudas"],
            horizontal=True
        )

        posts_list = datos_comm["posts"]
        if filtro_cat != "Todos":
            posts_list = [p for p in posts_list if p[3] == filtro_cat]

        if not posts_list:
            st.info("Aún no hay publicaciones en esta categoría. ¡Sé el primero en opinar arriba!")
        else:
            for post_id, a_email, a_nombre, cat, tit, cont, likes_cnt, f_post in posts_list:
                inicial = (a_nombre[:1] or "U").upper()
                lista_coms = datos_comm["comentarios_por_post"].get(post_id, [])

                with st.container(border=True):
                    h_c1, h_c2 = st.columns([5, 1])
                    with h_c1:
                        st.markdown(f"""
                        <div style="display:flex; align-items:center; gap:12px;">
                            <div class="avatar-circle">{inicial}</div>
                            <div>
                                <div style="font-weight:700; color:#ffffff;">{a_nombre}</div>
                                <div style="font-size:0.8rem; color:#94a3b8;">hace · {f_post} · <b>{cat}</b></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with h_c2:
                        st.caption(f"🏷️ {cat}")

                    st.markdown(f"**{tit}**")
                    st.write(cont)

                    b_like, b_com_info = st.columns([1.2, 4])
                    if b_like.button(f"👍 {likes_cnt}", key=f"like_post_{post_id}"):
                        dar_like_post(post_id)
                        st.rerun()
                    b_com_info.caption(f"💬 {len(lista_coms)} comentarios")

                    with st.expander(f"💬 Comentarios ({len(lista_coms)})", expanded=len(lista_coms) > 0):
                        for _, c_autor, c_texto, c_fecha in lista_coms:
                            st.markdown(f"**{c_autor}** _{c_fecha}_: {c_texto}")

                        com_input = st.text_input(
                            "Escribe un comentario...",
                            key=f"com_in_{post_id}",
                            placeholder="Comparte tu opinión o respuesta..."
                        )
                        if st.button("Enviar comentario", key=f"com_btn_{post_id}"):
                            if com_input.strip():
                                agregar_comentario_comunidad(post_id, nombre_actual, com_input)
                                st.rerun()
                            else:
                                st.warning("Escribe un comentario primero.")

    with col_stats:
        with st.container(border=True):
            inicial_yo = (nombre_actual[:1] or "U").upper()
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:0.5rem;">
                <div class="avatar-circle">{inicial_yo}</div>
                <div>
                    <div style="font-weight:800; font-size:1.15rem;">Comunidad Clipper</div>
                    <div style="font-size:0.8rem; color:#94a3b8;">Opiniones, ideas y clips de usuarios</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.caption("Comparte lo que creas, pregunta lo que no te sale y opina sobre las mejoras del Studio.")

            st.divider()
            st1, st2, st3 = st.columns(3)
            st1.markdown(f'<div class="comm-stat-box"><div class="comm-stat-val">{datos_comm["total_miembros"]}</div><div class="comm-stat-lbl">Miembros</div></div>', unsafe_allow_html=True)
            st2.markdown(f'<div class="comm-stat-box"><div class="comm-stat-val">{len(datos_comm["posts"])}</div><div class="comm-stat-lbl">Publicaciones</div></div>', unsafe_allow_html=True)
            st3.markdown(f'<div class="comm-stat-box"><div class="comm-stat-val">{datos_comm["total_comentarios"]}</div><div class="comm-stat-lbl">Comentarios</div></div>', unsafe_allow_html=True)

            st.write("")
            avatars_html = ""
            for m_email, m_apodo in datos_comm["miembros_rows"][:8]:
                m_nom = (m_apodo or m_email.split("@")[0])[:1].upper()
                avatars_html += f'<span class="mini-avatar">{m_nom}</span>'
            if avatars_html:
                st.markdown(f"<div style='margin-bottom:0.7rem;'>{avatars_html}</div>", unsafe_allow_html=True)

            if st.button("👤 Tu perfil en la comunidad", use_container_width=True):
                st.session_state["editar_perfil_comm"] = not st.session_state.get("editar_perfil_comm", False)

            if st.session_state.get("editar_perfil_comm"):
                nuevo_apodo = st.text_input("Tu nombre visible:", value=nombre_actual, key="input_apodo_comm")
                if st.button("Guardar nombre", type="primary", use_container_width=True):
                    if nuevo_apodo.strip():
                        guardar_apodo_comunidad(st.session_state["usuario"], nuevo_apodo)
                        st.session_state["editar_perfil_comm"] = False
                        st.success("¡Nombre actualizado!")
                        st.rerun()

        st.write("")
        with st.container(border=True):
            st.markdown("#### 🗳️ Vota qué sigue")
            st.caption("Un voto por opción. Puedes cambiarlo cuando quieras.")
            opciones_voto = [
                "Subtítulos animados palabra por palabra",
                "Publicar directo en YouTube Shorts",
                "Más plantillas de ganchos virales"
            ]
            votos_actuales = datos_comm["votos"]
            for idx_v, op_v in enumerate(opciones_voto):
                cant_v = votos_actuales.get(op_v, 0)
                if st.button(f"{op_v}  —  **{cant_v}**", key=f"voto_btn_{idx_v}", use_container_width=True):
                    votar_encuesta(st.session_state["usuario"], op_v)
                    st.rerun()

# ==============================================================================
# PÁGINA 4: MIS PROYECTOS
# ==============================================================================
elif pagina == "📁 Mis Proyectos":
    st.markdown("""
    <div class="hero-box">
        <div class="hero-title">Tus Proyectos 📁</div>
        <div class="hero-sub">Abre cualquiera de tus videos analizados anteriormente sin volver a gastar IA.</div>
    </div>
    """, unsafe_allow_html=True)

    busqueda = st.text_input("🔍 Buscar proyectos…", placeholder="Escribe el nombre del proyecto")
    filtrados = [p for p in proyectos if busqueda.lower() in p["nombre"].lower()]
    if not filtrados:
        st.info("Aún no tienes proyectos guardados. Crea tu primer proyecto en Inicio.")
    else:
        for p in filtrados:
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.markdown(f"**🎬 {p['nombre']}** — `{len(p['clips'])} clips` · _{p['fecha']}_")
                if c2.button("Abrir", type="primary", key=f"open_{p['id']}", use_container_width=True):
                    st.session_state["proyecto_activo"] = p
                    st.session_state["ir_a_resultados"] = True
                    st.session_state["pagina_actual"] = "💬 Inicio (Chat IA)"
                    st.rerun()
                if c3.button("🗑️ Borrar", key=f"del_{p['id']}", use_container_width=True):
                    proyectos = [x for x in proyectos if x["id"] != p["id"]]
                    guardar_json(PROJECTS_FILE, proyectos)
                    st.rerun()

# ==============================================================================
# PÁGINA 5: PLANES (PRO Y SUPER PRO) + YAPE + CANJE DE KEY
# ==============================================================================
elif pagina == "💎 Planes / Key":
    st.markdown("""
    <div class="hero-box">
        <div class="hero-title">Consigue los clips de tu vídeo ⚡</div>
        <div class="hero-sub">Elige Plan Pro o Super Pro, paga con Yape y activa tu cuenta al instante con tu Key.</div>
    </div>
    """, unsafe_allow_html=True)

    es_anual = st.toggle("Descuento anual (61%)", value=True, key="toggle_descuento_anual")

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        with st.container(border=True):
            st.markdown('<span class="step-pill">💎 PLAN PRO</span>', unsafe_allow_html=True)
            if es_anual:
                st.markdown("""
                <div class="price-box">
                    <span style="text-decoration:line-through; color:#94a3b8;">$19.00</span>
                    <span style="font-size:2rem; font-weight:800; color:#ffffff; margin-left:6px;">$7.50</span>
                    <span style="color:#cbd5e1;">/mes</span>
                    <span class="discount-pill">61% OFF</span>
                    <div style="color:#94a3b8; font-size:0.85rem;">Facturación anual · $89.99/año</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="price-box">
                    <span style="font-size:2rem; font-weight:800; color:#ffffff;">$19.00</span>
                    <span style="color:#cbd5e1;">/mes</span>
                    <div style="color:#94a3b8; font-size:0.85rem;">Facturación mensual</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("""
            <div class="benefit-item">✅ Hasta 6 clips por video encontrados y ordenados</div>
            <div class="benefit-item">✅ Descarga en HD y Full HD sin marca de agua</div>
            <div class="benefit-item">✅ Recorta, reencuadra y cambia subtítulos (colores y tamaño)</div>
            <div class="benefit-item">✅ Publica en TikTok y YouTube con Títulos IA</div>
            <div class="benefit-item" style="color:#64748b;">❌ Sin Radar de Tendencias TikTok ni Clonador Viral</div>
            """, unsafe_allow_html=True)

    with col_p2:
        with st.container(border=True):
            st.markdown('<span class="step-pill">🚀 PLAN SUPER PRO · RECOMENDADO</span>', unsafe_allow_html=True)
            if es_anual:
                st.markdown("""
                <div class="super-box">
                    <span style="text-decoration:line-through; color:#94a3b8;">$29.00</span>
                    <span style="font-size:2rem; font-weight:800; color:#ffffff; margin-left:6px;">$11.50</span>
                    <span style="color:#cbd5e1;">/mes</span>
                    <span class="discount-pill">61% OFF</span>
                    <div style="color:#94a3b8; font-size:0.85rem;">Facturación anual · $138.00/año</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="super-box">
                    <span style="font-size:2rem; font-weight:800; color:#ffffff;">$29.00</span>
                    <span style="color:#cbd5e1;">/mes</span>
                    <div style="color:#94a3b8; font-size:0.85rem;">Facturación mensual</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("""
            <div class="benefit-item">✅ <b>Todo lo incluido en Plan Pro</b></div>
            <div class="benefit-item">✅ Hasta <b>10 clips</b> por video en Full HD sin marca</div>
            <div class="benefit-item">✅ <b>Buscador de Tendencias TikTok en Vivo</b> (Google Search + IA)</div>
            <div class="benefit-item">✅ <b>Clonador de Fórmula Viral</b> (ingeniería inversa de TikToks)</div>
            <div class="benefit-item">✅ Prioridad en nuevas funciones del Studio</div>
            """, unsafe_allow_html=True)

    st.write("")
    with st.container(border=True):
        col_yape, col_key = st.columns(2)
        with col_yape:
            st.markdown(f"""
            <div class="yape-card">
                <div style="font-size:0.85rem; color:#e9d5ff; font-weight:700;">PAGA CON YAPE</div>
                <div style="font-size:1.55rem; font-weight:800; color:#ffffff; margin:0.4rem 0;">{YAPE_NUMERO}</div>
                <div style="font-size:0.85rem; color:#cbd5e1;">Yapea el monto de tu plan elegido y envíanos la captura por WhatsApp para recibir tu Key al instante.</div>
            </div>
            """, unsafe_allow_html=True)
            st.write("")
            msg_wa = urllib.parse.quote(
                f"Hola! Acabo de yapear para activar mi plan en Mi Clipper IA Studio. Mi correo registrado es: {st.session_state['usuario']}"
            )
            st.link_button(
                "📲 Enviar captura de Yape por WhatsApp",
                f"[https://wa.me/](https://wa.me/){YAPE_WHATSAPP}?text={msg_wa}",
                use_container_width=True
            )

        with col_key:
            st.markdown("#### 🔑 ¿Ya tienes tu Key?")
            st.caption("Ingresa la clave que te enviamos tras tu pago por Yape:")
            key_input = st.text_input("Key de activación", placeholder="Ej: PRO-A1B2-C3D4 o SPRO-A1B2-C3D4", key="input_canjear_key").strip().upper()
            if st.button("🚀 Activar mi Plan", type="primary", use_container_width=True):
                if not key_input:
                    st.warning("Escribe tu key primero.")
                else:
                    ok, msg = canjear_key(st.session_state["usuario"], key_input)
                    if ok:
                        st.success(msg)
                        time.sleep(1.2)
                        st.rerun()
                    else:
                        st.error(msg)

# ==============================================================================
# PÁGINA 6: PANEL ADMIN (GENERAR KEYS PRO / SUPER PRO Y GESTIONAR USUARIOS)
# ==============================================================================
elif pagina == "👑 Panel Admin" and usuario_es_admin:
    st.markdown("""
    <div class="hero-box">
        <div class="hero-title">Panel de Administrador 👑</div>
        <div class="hero-sub">Genera keys de Plan Pro o Super Pro para tus clientes de Yape y administra sus accesos.</div>
    </div>
    """, unsafe_allow_html=True)

    tab_keys, tab_users = st.tabs(["🔑 Generar y ver Keys", "👥 Usuarios registrados"])

    with tab_keys:
        with st.container(border=True):
            st.markdown("#### ✨ Generar nueva Key de licencia")
            col_t, col_d, col_adm, col_b = st.columns([1.4, 1.5, 1.1, 1])
            tipo_sel = col_t.selectbox("Tipo de Plan:", ["PRO", "SUPER_PRO"], format_func=lambda x: "💎 Plan Pro" if x == "PRO" else "🚀 Plan Super Pro")
            opciones_duracion = {
                "Mensual (30 días)": 30,
                "Trimestral (90 días)": 90,
                "Anual (365 días)": 365,
                "Ilimitado (De por vida)": 0
            }
            seleccion = col_d.selectbox("Duración:", list(opciones_duracion.keys()))
            with col_adm:
                st.write("")
                st.write("")
                incluir_admin = st.checkbox("👑 +Admin", value=False)
            with col_b:
                st.write("")
                st.write("")
                if st.button("⚡ Generar Key", type="primary", use_container_width=True):
                    nueva_clave = generar_nueva_key(opciones_duracion[seleccion], plan_tipo=tipo_sel, da_admin=incluir_admin)
                    st.session_state["ultima_key_generada"] = nueva_clave

            if "ultima_key_generada" in st.session_state:
                st.success("¡Key generada! Cópiala y envíasela al cliente por WhatsApp:")
                st.code(st.session_state["ultima_key_generada"], language="text")

        with st.container(border=True):
            st.markdown("#### 📋 Historial de Keys")
            keys = listar_keys()
            if not keys:
                st.info("Aún no has generado ninguna key.")
            else:
                for clave, dias, p_tipo, da_adm, usada_por, f_crea, f_uso in keys:
                    dur_txt = "Ilimitado" if dias == 0 else f"{dias} días"
                    plan_badge = "🚀 **SUPER PRO**" if p_tipo == "SUPER_PRO" else "💎 **PRO**"
                    adm_badge = " · 👑 **+ADMIN**" if da_adm else ""
                    if usada_por:
                        st.markdown(f"🔴 **`{clave}`** · {plan_badge} · `{dur_txt}`{adm_badge} · Usada por **{usada_por}** ({f_uso})")
                    else:
                        st.markdown(f"🟢 **`{clave}`** · {plan_badge} · `{dur_txt}`{adm_badge} · **Disponible** _(creada {f_crea})_")

    with tab_users:
        with st.container(border=True):
            st.markdown("#### 👥 Gestión manual de usuarios")
            usuarios = listar_usuarios()
            if not usuarios:
                st.info("No hay usuarios registrados todavía.")
            else:
                for email_u, activo_u, tipo_u, expira_u, es_adm_u in usuarios:
                    c1, c2, c3, c4, c5, c6 = st.columns([2.1, 1.4, 0.85, 0.95, 0.8, 0.95])
                    if es_admin_super(email_u):
                        estado = "👑 SUPER ADMIN"
                    elif es_adm_u:
                        estado = f"👑 ADMIN ({tipo_u})"
                    elif activo_u:
                        estado = f"🚀 Super Pro ({expira_u})" if tipo_u == "SUPER_PRO" else f"💎 Pro ({expira_u})"
                    else:
                        estado = "🆓 Free"

                    c1.markdown(f"**{email_u}**")
                    c2.markdown(estado)
                    if not es_admin_super(email_u):
                        if c3.button("💎 Pro", key=f"pro_{email_u}", use_container_width=True):
                            actualizar_acceso_manual(email_u, "PRO", 30)
                            st.rerun()
                        if c4.button("🚀 S.Pro", key=f"spro_{email_u}", use_container_width=True):
                            actualizar_acceso_manual(email_u, "SUPER_PRO", 30)
                            st.rerun()
                        if c5.button("🚫 Free", key=f"rev_{email_u}", use_container_width=True):
                            actualizar_acceso_manual(email_u, "FREE")
                            st.rerun()
                        if es_adm_u:
                            if c6.button("Quitar 👑", key=f"no_adm_{email_u}", use_container_width=True):
                                cambiar_rol_admin(email_u, False)
                                st.rerun()
                        else:
                            if c6.button("Dar 👑", key=f"si_adm_{email_u}", use_container_width=True):
                                cambiar_rol_admin(email_u, True)
                                st.rerun()
