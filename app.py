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
VERSION_ACTUAL = "1.4.8"
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
# BASE DE DATOS: USUARIOS, PLANES (FREE / PRO / SUPER_PRO), ROLES ADMIN Y KEYS
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
            es_admin INTEGER DEFAULT 0
        )
    """)
    for col_def in (
        "plan_activo INTEGER DEFAULT 0",
        "plan_tipo TEXT DEFAULT 'FREE'",
        "plan_expira TEXT",
        "es_admin INTEGER DEFAULT 0"
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

    conn.commit()
    conn.close()

def encriptar_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

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

def usuario_existe(email: str) -> bool:
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM usuarios WHERE email = ?", (email,))
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
        c.execute(
            "INSERT INTO usuarios (email, password, plan_activo, plan_tipo, plan_expira, es_admin) VALUES (?, ?, ?, ?, ?, ?)",
            (email, encriptar_password(password), activo, tipo, expira, admin_flag)
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

def enviar_codigo_gmail(destinatario: str, codigo: str):
    if "EMAIL_REMITENTE" not in st.secrets or "BREVO_API_KEY" not in st.secrets:
        raise Exception("Falta configurar EMAIL_REMITENTE y BREVO_API_KEY en los Secrets.")

    remitente = st.secrets["EMAIL_REMITENTE"].strip()
    api_key = st.secrets["BREVO_API_KEY"].strip()

    payload = json.dumps({
        "sender": {"name": "Mi Clipper IA Studio", "email": remitente},
        "to": [{"email": destinatario}],
        "subject": "⚡ Tu código de verificación - Mi Clipper IA Studio",
        "textContent": (
            f"Hola,\n\nTu código de verificación para crear tu cuenta en Mi Clipper IA Studio es:\n\n"
            f"    {codigo}\n\n"
            f"Ingrésalo en la web para activar tu cuenta.\n"
            f"Si no solicitaste este código, ignora este correo."
        )
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
# PANTALLA DE LOGIN / REGISTRO CON GMAIL
# ==============================================================================
if not st.session_state["autenticado"]:
    _, col_centro, _ = st.columns([1, 1.6, 1])
    with col_centro:
        st.markdown("""
        <div class="hero-box">
            <div class="hero-title">⚡ Mi Clipper IA Studio</div>
            <div class="hero-sub">Inicia sesión o crea tu cuenta con Gmail para empezar a crear clips virales.</div>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            tab_login, tab_registro = st.tabs(["🔐 Iniciar Sesión", "✨ Crear Cuenta"])

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
                                enviar_codigo_gmail(email_reg, codigo)
                            st.session_state["codigo_enviado"] = codigo
                            st.session_state["email_pendiente"] = email_reg
                            st.session_state["pass_pendiente"] = pass_reg
                            st.success("¡Código enviado! Revisa tu bandeja de entrada o la carpeta de Spam.")
                        except Exception as e:
                            st.error(f"Error al enviar el correo: {e}")

                if "codigo_enviado" in st.session_state:
                    st.divider()
                    codigo_ingresado = st.text_input("Ingresa el código de 6 dígitos").strip()

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
# MOTORES IA: GEMINI + GROQ + DEEPSEEK (BETA) + OPENAI
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
                    # Si tiene clave de Groq u OpenAI transcribe con Whisper; si no, lee audio/texto disponible
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

# --- COLORES Y LAYOUTS ---
COLORES_SUBTITULOS = {
    "Amarillo viral": "&H0000FFFF",
    "Blanco limpio": "&H00FFFFFF",
    "Verde neón": "&H0055FF33",
    "Cian eléctrico": "&H00FFFF00",
    "Rosa aesthetic": "&H00CC99FF",
    "Dorado cine": "&H0037AFD4",
    "Naranja fuego": "&H000088FF",
}

LAYOUTS_VIDEO = [
    "Pantalla completa (9:16)",
    "Imagen entera + fondo blur (9:16)",
    "Cuadrado centrado + fondo blur (9:16)",
    "Horizontal original (16:9)",
    "Cuadrado (1:1)"
]

# --- FUNCIONES DE VIDEO, IA, TENDENCIAS Y TIKTOK ---

def descargar_video(url: str, proj_id: str) -> str:
    output_path = WORK_DIR / f"video_{proj_id}.mp4"
    if output_path.exists():
        output_path.unlink()
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--no-playlist",
        "--extractor-args", "youtube:player_client=android,web",
        "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "-o", str(output_path),
        url
    ]
    resultado = subprocess.run(cmd, capture_output=True, text=True)
    if resultado.returncode != 0:
        raise Exception(f"No hemos podido importar este enlace:\n{resultado.stderr}")
    return str(output_path)

def extraer_audio(video_path: str, proj_id: str, min_inicio: float = 0.0, min_fin: float = 0.0) -> str:
    audio_path = WORK_DIR / f"audio_{proj_id}.mp3"
    if audio_path.exists():
        audio_path.unlink()
    cmd = ["ffmpeg", "-y"]
    if min_inicio > 0:
        cmd += ["-ss", str(min_inicio * 60)]
    cmd += ["-i", video_path]
    if min_fin > min_inicio:
        cmd += ["-t", str((min_fin - min_inicio) * 60)]
    cmd += ["-vn", "-ac", "1", "-ar", "16000", "-acodec", "libmp3lame", "-b:a", "32k", str(audio_path)]

    resultado = subprocess.run(cmd, capture_output=True, text=True)
    if resultado.returncode != 0:
        raise Exception(f"Error al preparar el audio con FFmpeg:\n{resultado.stderr}")
    return str(audio_path)

def obtener_duracion_video(video_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", video_path
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        return round(float(res.stdout.strip()), 2)
    except Exception:
        return 60.0

def buscar_momentos_ia(audio_path: str, instruccion_usuario: str, num_clips: int, duracion_objetivo: str, offset_seg: float = 0.0):
    if not instruccion_usuario.strip():
        instruccion_usuario = "Elige automáticamente los momentos con mayor retención, gancho inicial y potencial viral."

    prompt = f"""
    Eres el asistente IA de edición de video estilo Nexus Clips.
    Analiza este audio y extrae los {num_clips} mejores momentos que cumplan EXACTAMENTE con lo que pide el creador.

    INSTRUCCIÓN DEL CREADOR: "{instruccion_usuario}"
    DURACIÓN OBJETIVO POR CLIP: {duracion_objetivo}

    REGLAS:
- Los cortes deben empezar y terminar en frases completas.
- Devuelve exclusivamente un JSON válido con una lista bajo la clave "clips".
- Sé conciso en "motivo" y "subtitulos" (máximo 3 frases cortas por clip) para que la respuesta sea rápida y completa.
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

    tokens_salida = 3200 if num_clips > 5 else 2200
    texto_json, motor_usado = ejecutar_ia_con_respaldo(prompt, audio_path=audio_path, esperar_json=True, max_tokens=tokens_salida)
    clips = json.loads(texto_json)["clips"]
    if offset_seg > 0:
        for c in clips:
            c["start"] = round(float(c["start"]) + offset_seg, 2)
            c["end"] = round(float(c["end"]) + offset_seg, 2)
    return clips, motor_usado

def analizar_clip_para_redes_ia(video_path: str, tono: str, contexto_extra: str = ""):
    audio_temp = extraer_audio(video_path, f"tk_{datetime.now().strftime('%H%M%S')}")
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
    v_path = descargar_video(tiktok_url, proj_id)
    dur = obtener_duracion_video(v_path)
    a_path = extraer_audio(v_path, proj_id)

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
    datos["video_path"] = v_path
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
    video_path: str,
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
    sub_filter = f"subtitles={srt_filename}:force_style='{sub_style}'" if usar_sub else ""
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

    cmd = ["ffmpeg", "-y", "-ss", str(start), "-i", video_path, "-t", str(duracion)]

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
    init_url = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
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

# --- BARRA DE NAVEGACIÓN SUPERIOR SIEMPRE VISIBLE ---
opciones_menu = ["💬 Inicio (Chat IA)", "✂️ Editor y Redes", "📈 Tendencias TikTok", "📁 Mis Proyectos"]

if not es_super_pro and not usuario_es_admin:
    opciones_menu.append("💎 Planes / Key")

if usuario_es_admin:
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
        <div class="hero-sub">Convierte cualquier vídeo largo en clips virales listos para TikTok y YouTube Shorts.</div>
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
        st.session_state["video_path"] = p["video_path"]
        st.session_state["audio_path"] = p["audio_path"]
        st.session_state["clips_encontrados"] = p["clips"]
        st.session_state["nombre_proyecto"] = p["nombre"]

    # --- PASO 1 ---
    with st.container(border=True):
        st.markdown('<span class="step-pill">PASO 1 · IMPORTAR</span>', unsafe_allow_html=True)
        st.markdown("### Trae tu vídeo")
        tab_link, tab_file = st.tabs(["🔗 Enlace (YouTube / Twitch / TikTok)", "📁 Subir desde mi PC"])

        col_r1, col_r2, col_r3 = st.columns([2, 1, 1])
        modo_rango = col_r1.radio("Rango del vídeo:", ["Todo el vídeo", "Solo una parte (vídeos largos)"], horizontal=True)
        min_ini, min_fin = 0.0, 0.0
        if modo_rango == "Solo una parte (vídeos largos)":
            min_ini = col_r2.number_input("Inicio (min)", min_value=0.0, value=0.0, step=1.0)
            min_fin = col_r3.number_input("Fin (min)", min_value=0.0, value=10.0, step=1.0)

        with tab_link:
            url_input = st.text_input("Pega el link aquí:", placeholder="https://www.youtube.com/watch?v=...")
            if st.button("⬇️ Importar vídeo", type="primary", key="btn_import_url"):
                if not url_input:
                    st.warning("Pega un enlace primero.")
                else:
                    try:
                        proj_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                        with st.spinner("Descargando vídeo..."):
                            v_path = descargar_video(url_input, proj_id)
                        with st.spinner("Extrayendo audio ligero para la IA..."):
                            a_path = extraer_audio(v_path, proj_id, min_ini, min_fin)
                        st.session_state["proj_id"] = proj_id
                        st.session_state["video_path"] = v_path
                        st.session_state["audio_path"] = a_path
                        st.session_state["offset_seg"] = min_ini * 60
                        st.session_state["nombre_proyecto"] = f"Video {proj_id}"
                        st.session_state.pop("clips_encontrados", None)
                        st.success("¡Vídeo listo! Ahora configura el Paso 2 abajo.")
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
                    with st.spinner("⚡ Analizando vídeo y detectando los mejores clips…"):
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
        st.markdown('<span class="step-pill">PASO 3 · RESULTADOS</span>', unsafe_allow_html=True)
        st.markdown("### Tus clips sugeridos")

        for i, clip in enumerate(st.session_state["clips_encontrados"]):
            with st.expander(f"🎬 Clip #{i+1}: {clip['titulo']}  ·  🔥 {clip['puntaje_viral']}/100", expanded=True):
                col_info, col_render = st.columns([1.8, 1.2])
                with col_info:
                    st.markdown(f'<span class="viral-badge">🔥 Viralidad {clip["puntaje_viral"]}/100</span>', unsafe_allow_html=True)
                    st.write(f"**Por qué funciona:** {clip['motivo']}")

                    if es_pro:
                        if clip.get("gancho_visual"):
                            st.markdown(f"**🎯 Gancho visual sugerido:** `{clip['gancho_visual']}`")
                        st.info(f"**Magic Post (Copy para TikTok / YouTube):**\n\n{clip['descripcion_redes']}")

                        t1, t2 = st.columns(2)
                        inicio = t1.number_input("Inicio (seg)", value=float(clip["start"]), key=f"start_{i}")
                        fin = t2.number_input("Fin (seg)", value=float(clip["end"]), key=f"end_{i}")

                        o1, o2 = st.columns(2)
                        layout_clip = o1.selectbox("📐 Encuadre", LAYOUTS_VIDEO, index=0, key=f"lay_{i}")
                        calidad_clip = o2.selectbox("📺 Calidad de descarga", ["HD (720p)", "Full HD (1080p)"], index=1, key=f"cal_{i}")

                        s1, s2, s3 = st.columns(3)
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
                        st.caption("🔒 Recorte manual, reencuadre, subtítulos de colores/tamaño y descarga HD/Full HD sin marca de agua están disponibles desde el **Plan Pro**.")

                with col_render:
                    proj_id = st.session_state.get("proj_id", "local")
                    out_file = str(CLIPS_DIR / f"{proj_id}_clip_{i+1}.mp4")

                    if st.button(f"✂️ Crear Clip #{i+1}", type="primary", use_container_width=True, key=f"render_{i}"):
                        try:
                            with st.spinner("Renderizando clip…"):
                                srt_temp = None
                                if usar_sub and clip.get("subtitulos"):
                                    srt_temp = str(WORK_DIR / f"temp_sub_{i+1}.srt")
                                    generar_srt_clip(clip["subtitulos"], srt_temp)

                                renderizar_clip(
                                    st.session_state["video_path"],
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
                            st.success("¡Clip listo!")
                        except Exception as e:
                            st.error(str(e))

                    if os.path.exists(out_file):
                        st.video(out_file)
                        etiqueta_dl = f"⬇️ Descargar {calidad_clip}" if es_pro else "⬇️ Descargar (con marca de agua)"
                        with open(out_file, "rb") as f:
                            st.download_button(
                                label=etiqueta_dl,
                                data=f,
                                file_name=f"clip_{i+1}_{proj_id}.mp4",
                                mime="video/mp4",
                                use_container_width=True,
                                key=f"dl_{i}"
                            )

# ==============================================================================
# PÁGINA 2: EDITOR DE VIDEO + TÍTULOS IA + TIKTOK & YOUTUBE (PRO Y SUPER PRO)
# ==============================================================================
elif pagina == "✂️ Editor y Redes":
    st.markdown("""
    <div class="hero-box">
        <div class="hero-title">Editor Studio & Publicación 🎵</div>
        <div class="hero-sub">Recorta, quema ganchos visuales, genera Títulos IA y publica en TikTok y YouTube.</div>
    </div>
    """, unsafe_allow_html=True)

    if not es_pro:
        with st.container(border=True):
            st.warning("🔒 **Función disponible desde el Plan Pro**")
            st.markdown("""
            Con **Plan Pro** o **Super Pro** desbloqueas:
            - ✂️ Editor avanzado (recortar, velocidad, brillo, contraste y gancho visual)
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
            st.markdown('<span class="step-pill">EDITOR DE VIDEO</span>', unsafe_allow_html=True)
            col_prev, col_edit = st.columns([1, 1.4])
            with col_prev:
                st.markdown("#### 📺 Vista previa")
                video_a_mostrar = st.session_state.get("video_editado_actual", video_elegido)
                if not os.path.exists(video_a_mostrar):
                    video_a_mostrar = video_elegido
                st.video(video_a_mostrar)

            with col_edit:
                st.markdown("#### 🎛️ Ajustes antes de subir")
                r1, r2 = st.columns(2)
                ed_ini = r1.number_input("Recortar inicio (seg)", min_value=0.0, max_value=dur_total, value=0.0, step=0.5)
                ed_fin = r2.number_input("Recortar fin (seg)", min_value=0.5, max_value=dur_total, value=dur_total, step=0.5)

                e1, e2, e3 = st.columns(3)
                velocidad = e1.select_slider("Velocidad", options=[0.75, 1.0, 1.25, 1.5, 2.0], value=1.0)
                volumen = e2.slider("Volumen", 0.0, 2.0, 1.0, 0.1)
                contraste = e3.slider("Contraste", 0.5, 1.8, 1.0, 0.05)

                brillo = st.slider("Brillo", -0.3, 0.3, 0.0, 0.02)
                texto_hook = st.text_input(
                    "🎯 Texto Gancho (Hook) arriba del video:",
                    value=st.session_state.get("hook_auto", ""),
                    placeholder="Presiona el botón de IA arriba o escribe tu propio gancho..."
                )

                if st.button("✂️ Aplicar edición y quemar Gancho en el video", type="primary", use_container_width=True):
                    try:
                        nombre_editado = str(EDITED_DIR / f"editado_{datetime.now().strftime('%H%M%S')}_{Path(video_elegido).name}")
                        with st.spinner("Aplicando edición en Full HD..."):
                            editar_video_ffmpeg(
                                video_elegido, nombre_editado, ed_ini, ed_fin,
                                velocidad, volumen, brillo, contraste, texto_hook
                            )
                        st.session_state["video_editado_actual"] = nombre_editado
                        st.success("¡Video editado con éxito!")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

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
                st.link_button("🎵 Publicar en TikTok Studio", "https://www.tiktok.com/tiktokstudio/upload", use_container_width=True)
            with b3:
                st.link_button("▶️ Publicar en YouTube Studio", "https://studio.youtube.com/channel/UC/videos/upload", use_container_width=True)

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
            url_tk = st.text_input("🔗 Pega el link del TikTok viral aquí:", placeholder="https://www.tiktok.com/@usuario/video/...")

            if st.button("🧬 Analizar y extraer fórmula viral", type="primary", use_container_width=True):
                if not url_tk.strip():
                    st.warning("Pega un enlace de TikTok primero.")
                else:
                    try:
                        with st.spinner("⚡ Descargando TikTok y extrayendo fórmula viral..."):
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
                    if f.get("video_path") and os.path.exists(f["video_path"]):
                        st.video(f["video_path"])
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
                f"https://wa.me/{YAPE_WHATSAPP}?text={msg_wa}",
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
