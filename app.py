import streamlit as st
import subprocess
import json
import os
import sys
import time
import urllib.request
import urllib.error
import random
import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path
from google import genai
from google.genai import types

st.set_page_config(
    page_title="Mi Clipper IA Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILO VISUAL PREMIUM (NEXUS STUDIO VIBRANT DARK + NEON GLASS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Ocultar botón Deploy, menú de tres puntos y barra superior */
    #MainMenu {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stDecoration"] {display: none !important;}
    footer {visibility: hidden !important;}
    header[data-testid="stHeader"] {background: transparent !important;}

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
        font-size: 2.5rem;
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
        font-size: 1.5rem;
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
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# SISTEMA DE CUENTAS Y VERIFICACIÓN POR GMAIL (API DE BREVO)
# ==============================================================================
def init_db():
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            email TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

def encriptar_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

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
        c.execute(
            "INSERT INTO usuarios (email, password) VALUES (?, ?)",
            (email, encriptar_password(password))
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
            "content-type": "application/json"
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
# SISTEMA DE ACTUALIZACIONES AUTOMÁTICAS
# ==============================================================================
VERSION_ACTUAL = "1.2.0"
URL_VERSION_JSON = "https://raw.githubusercontent.com/andres261727/CLIPS-/main/version.json"

def revisar_actualizacion():
    if "update_checked" in st.session_state:
        return
    st.session_state["update_checked"] = True
    try:
        req = urllib.request.Request(URL_VERSION_JSON, headers={"Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("version") and data["version"] != VERSION_ACTUAL:
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
                del st.session_state["nueva_version"]
                time.sleep(1.5)
                st.rerun()
            except Exception as e:
                st.error(f"No se pudo actualizar: {e}")
    with col2:
        if st.button("Más tarde", use_container_width=True):
            del st.session_state["nueva_version"]
            st.rerun()

revisar_actualizacion()
if "nueva_version" in st.session_state:
    mostrar_popup_actualizacion(st.session_state["nueva_version"])

# --- RUTAS Y ARCHIVOS SEPARADOS POR USUARIO ---
USER_HASH = hashlib.md5(st.session_state["usuario"].encode()).hexdigest()[:12]
USER_BASE = Path("user_data") / USER_HASH
WORK_DIR = USER_BASE / "workspace"
CLIPS_DIR = USER_BASE / "clips_generados"
EDITED_DIR = USER_BASE / "clips_editados"
CONFIG_FILE = USER_BASE / "config_clipper.json"
PROJECTS_FILE = USER_BASE / "proyectos.json"

WORK_DIR.mkdir(parents=True, exist_ok=True)
CLIPS_DIR.mkdir(parents=True, exist_ok=True)
EDITED_DIR.mkdir(parents=True, exist_ok=True)

ESTILOS_SUBTITULOS = {
    "Sin subtítulos": None,
    "Dinámico (Letra grande amarilla)": "FontName=Arial Black,FontSize=20,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=1,Alignment=2,MarginV=55",
    "Minimalista (Blanco limpio)": "FontName=Arial,FontSize=17,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Alignment=2,MarginV=50",
    "Informativo (Caja oscura)": "FontName=Arial,FontSize=17,PrimaryColour=&H00FFFFFF,BackColour=&H99000000,BorderStyle=3,Outline=1,Alignment=2,MarginV=50",
    "Elegante (Dorado cine)": "FontName=Georgia,FontSize=17,PrimaryColour=&H0037AFD4,OutlineColour=&H00101010,BorderStyle=1,Outline=2,Alignment=2,MarginV=55",
    "Divertido (Verde neón / Gaming)": "FontName=Impact,FontSize=21,PrimaryColour=&H0055FF33,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Alignment=2,MarginV=55",
    "Aesthetic (Rosa suave)": "FontName=Verdana,FontSize=17,PrimaryColour=&H00CC99FF,OutlineColour=&H00201030,BorderStyle=1,Outline=2,Alignment=2,MarginV=55",
}

LAYOUTS_VIDEO = [
    "Pantalla completa (9:16)",
    "Imagen entera + fondo blur (9:16)",
    "Cuadrado centrado + fondo blur (9:16)",
    "Horizontal original (16:9)",
    "Cuadrado (1:1)"
]

# --- PERSISTENCIA ---

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

config = cargar_json(CONFIG_FILE, {})
proyectos = cargar_json(PROJECTS_FILE, [])

# --- FUNCIONES DE VIDEO, IA Y TIKTOK ---

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
        st.error(f"No hemos podido importar este enlace:\n{resultado.stderr}")
        st.stop()
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
    cmd += ["-vn", "-acodec", "libmp3lame", "-b:a", "64k", str(audio_path)]

    resultado = subprocess.run(cmd, capture_output=True, text=True)
    if resultado.returncode != 0:
        st.error(f"Error al preparar el audio con FFmpeg:\n{resultado.stderr}")
        st.stop()
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

def buscar_momentos_ia(api_key: str, audio_path: str, instruccion_usuario: str, num_clips: int, duracion_objetivo: str, offset_seg: float = 0.0):
    client = genai.Client(api_key=api_key)
    audio_file = client.files.upload(file=audio_path)
    while audio_file.state.name == "PROCESSING":
        time.sleep(2)
        audio_file = client.files.get(name=audio_file.name)

    if not instruccion_usuario.strip():
        instruccion_usuario = "Elige automáticamente los momentos con mayor retención, gancho inicial y potencial viral."

    prompt = f"""
    Eres el asistente IA de edición de video estilo Nexus Clips.
    Escucha este audio completo y extrae los {num_clips} mejores momentos que cumplan EXACTAMENTE con lo que pide el creador.

    INSTRUCCIÓN DEL CREADOR: "{instruccion_usuario}"
    DURACIÓN OBJETIVO POR CLIP: {duracion_objetivo}

    REGLAS:
- Los cortes deben empezar y terminar en frases completas.
- Devuelve exclusivamente un JSON con una lista bajo la clave "clips".
- Cada clip debe incluir:
  - "titulo": título/gancho corto y atractivo
  - "gancho_visual": texto ultra corto (3 a 6 palabras en MAYÚSCULAS) para poner arriba del video y atrapar atención
  - "start": segundo exacto de inicio en el audio (número float)
  - "end": segundo exacto de fin en el audio (número float)
  - "motivo": por qué este momento funciona bien
  - "puntaje_viral": entero del 1 al 100
  - "descripcion_redes": copy listo para TikTok/Shorts/Reels con hashtags
  - "subtitulos": lista de frases cortas (3 a 5 palabras) dentro del clip, cada una con "start" (relativo desde 0.0), "end" (relativo) y "text".
    """

    response = None
    for intento in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=[audio_file, prompt],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            break
        except Exception as e:
            if "503" in str(e) and intento < 2:
                time.sleep(5)
            else:
                try:
                    client.files.delete(name=audio_file.name)
                except Exception:
                    pass
                st.error(f"Error con Gemini (intenta de nuevo en unos segundos): {e}")
                st.stop()

    try:
        client.files.delete(name=audio_file.name)
    except Exception:
        pass

    clips = json.loads(response.text)["clips"]
    if offset_seg > 0:
        for c in clips:
            c["start"] = round(float(c["start"]) + offset_seg, 2)
            c["end"] = round(float(c["end"]) + offset_seg, 2)
    return clips

def analizar_clip_para_tiktok_ia(api_key: str, video_path: str, tono: str, contexto_extra: str = ""):
    audio_temp = extraer_audio(video_path, f"tk_{datetime.now().strftime('%H%M%S')}")
    client = genai.Client(api_key=api_key)
    audio_file = client.files.upload(file=audio_temp)
    while audio_file.state.name == "PROCESSING":
        time.sleep(1.5)
        audio_file = client.files.get(name=audio_file.name)

    prompt = f"""
    Eres un director creativo experto en viralidad de TikTok.
    Escucha el audio de este clip y genera el mejor empaque viral posible.
    TONO DESEADO: "{tono}"
    CONTEXTO ADICIONAL DEL CREADOR (si hay): "{contexto_extra}"

    Devuelve exclusivamente un JSON con:
- "gancho_visual": frase explosiva de 3 a 6 palabras (en MAYÚSCULAS) para colocar en grande arriba del video durante los primeros segundos y detener el scroll.
- "titulos": lista de 5 títulos virales cortos para TikTok (máximo 95 caracteres cada uno, con emojis estratégicos).
- "descripcion": descripción corta con un llamado a la acción (CTA) que provoque comentarios.
- "hashtags": cadena con 5 a 8 hashtags relevantes y de alto alcance.
    """

    response = None
    for intento in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=[audio_file, prompt],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            break
        except Exception as e:
            if "503" in str(e) and intento < 2:
                time.sleep(4)
            else:
                try:
                    client.files.delete(name=audio_file.name)
                except Exception:
                    pass
                st.error(f"Error al analizar el clip con IA: {e}")
                st.stop()

    try:
        client.files.delete(name=audio_file.name)
        if os.path.exists(audio_temp):
            os.remove(audio_temp)
    except Exception:
        pass

    return json.loads(response.text)

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

def renderizar_clip(video_path: str, start: float, end: float, output_path: str, layout: str, estilo_sub: str, srt_filename: str = None):
    duracion = max(1.0, end - start)
    sub_style = ESTILOS_SUBTITULOS.get(estilo_sub)
    usar_sub = (sub_style is not None) and srt_filename and os.path.exists(srt_filename)
    sub_filter = f"subtitles={srt_filename}:force_style='{sub_style}'" if usar_sub else ""

    cmd = ["ffmpeg", "-y", "-ss", str(start), "-i", video_path, "-t", str(duracion)]

    if layout == "Imagen entera + fondo blur (9:16)":
        fc = (
            "[0:v]split[main][bg];"
            "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg_b];"
            "[main]scale=1080:-2[fg];"
            "[bg_b][fg]overlay=(W-w)/2:(H-h)/2"
        )
        if usar_sub:
            fc += f",{sub_filter}"
        cmd += ["-filter_complex", fc]

    elif layout == "Cuadrado centrado + fondo blur (9:16)":
        fc = (
            "[0:v]split[main][bg];"
            "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg_b];"
            "[main]crop=min(iw\\,ih):min(iw\\,ih),scale=1080:1080[fg];"
            "[bg_b][fg]overlay=(W-w)/2:(H-h)/2"
        )
        if usar_sub:
            fc += f",{sub_filter}"
        cmd += ["-filter_complex", fc]

    else:
        filtros = []
        if layout == "Pantalla completa (9:16)":
            filtros.append("crop=ih*9/16:ih,scale=1080:1920")
        elif layout == "Cuadrado (1:1)":
            filtros.append("crop=min(iw\\,ih):min(iw\\,ih),scale=1080:1080")
        if usar_sub:
            filtros.append(sub_filter)
        if filtros:
            cmd += ["-vf", ",".join(filtros)]

    cmd += [
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        output_path
    ]
    resultado = subprocess.run(cmd, capture_output=True, text=True)
    if resultado.returncode != 0:
        st.error(f"Error al renderizar con FFmpeg:\n{resultado.stderr}")
        st.stop()

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
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        output_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        st.error(f"Error al editar el video:\n{res.stderr}")
        st.stop()

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
            "Content-Type": "application/json; charset=UTF-8"
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
            "Content-Range": f"bytes 0-{file_size - 1}/{file_size}"
        },
        method="PUT"
    )
    with urllib.request.urlopen(put_req, timeout=120) as put_resp:
        if put_resp.status not in (200, 201, 206):
            raise Exception(f"Error al subir archivo a TikTok (HTTP {put_resp.status})")
    return True

# --- BARRA LATERAL ---

total_clips_creados = len(list(CLIPS_DIR.glob("*.mp4"))) + len(list(EDITED_DIR.glob("*.mp4")))

with st.sidebar:
    st.markdown('<div class="brand-logo">⚡ Mi Clipper IA</div>', unsafe_allow_html=True)
    st.caption(f"Studio Pro · v{VERSION_ACTUAL}")
    st.caption(f"👤 {st.session_state['usuario']}")
    if st.button("🚪 Cerrar sesión", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
    st.divider()

    pagina = st.radio(
        "Navegación",
        ["💬 Inicio (Chat IA)", "✂️ Editor y TikTok", "📁 Mis Proyectos", "⚙️ Ajustes y API Key"],
        label_visibility="collapsed"
    )

    st.divider()
    if config.get("api_key"):
        st.success("🟢 Gemini IA conectada")
    else:
        st.warning("🟡 Falta Gemini API Key")

    if config.get("tiktok_token"):
        st.success("🎵 TikTok API lista")
    else:
        st.info("🎵 TikTok: modo Studio")

    if st.button("🔄 Buscar actualizaciones", use_container_width=True):
        st.session_state.pop("update_checked", None)
        revisar_actualizacion()
        if "nueva_version" in st.session_state:
            st.rerun()
        else:
            st.toast("Ya tienes la última versión instalada.", icon="✅")

    if proyectos:
        st.divider()
        st.caption("PROYECTOS RECIENTES")
        for p in proyectos[:4]:
            if st.button(f"🎬 {p['nombre'][:22]}", key=f"side_p_{p['id']}", use_container_width=True):
                st.session_state["proyecto_activo"] = p
                st.session_state["ir_a_resultados"] = True
                st.rerun()

# ==============================================================================
# PÁGINA 1: INICIO / CHAT IA
# ==============================================================================
if pagina == "💬 Inicio (Chat IA)":
    st.markdown("""
    <div class="hero-box">
        <div class="hero-title">¿Qué creamos hoy? ⚡</div>
        <div class="hero-sub">Convierte cualquier vídeo largo en clips virales con subtítulos, gancho visual y títulos IA listos para TikTok.</div>
    </div>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="stat-card"><div class="stat-num">{total_clips_creados}</div><div class="stat-label">Clips Renderizados</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="stat-card"><div class="stat-num">{len(proyectos)}</div><div class="stat-label">Proyectos Guardados</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="stat-card"><div class="stat-num">{"ON" if config.get("api_key") else "OFF"}</div><div class="stat-label">Motor Gemini 3.8</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="stat-card"><div class="stat-num">{"API" if config.get("tiktok_token") else "STUDIO"}</div><div class="stat-label">Modo TikTok</div></div>', unsafe_allow_html=True)

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
                    proj_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                    with st.spinner("Descargando vídeo..."):
                        v_path = descargar_video(url_input, proj_id)
                    with st.spinner("Extrayendo audio para la IA..."):
                        a_path = extraer_audio(v_path, proj_id, min_ini, min_fin)
                    st.session_state["proj_id"] = proj_id
                    st.session_state["video_path"] = v_path
                    st.session_state["audio_path"] = a_path
                    st.session_state["offset_seg"] = min_ini * 60
                    st.session_state["nombre_proyecto"] = f"Video {proj_id}"
                    st.session_state.pop("clips_encontrados", None)
                    st.success("¡Vídeo listo! Ahora configura el Paso 2 abajo.")

        with tab_file:
            archivo = st.file_uploader("Arrastra tu MP4, MOV o MKV", type=["mp4", "mov", "mkv"])
            if archivo and st.button("⚙️ Preparar archivo", type="primary", key="btn_import_file"):
                proj_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                v_path = str(WORK_DIR / f"video_{proj_id}.mp4")
                with open(v_path, "wb") as f:
                    f.write(archivo.read())
                with st.spinner("Extrayendo audio para la IA..."):
                    a_path = extraer_audio(v_path, proj_id, min_ini, min_fin)
                st.session_state["proj_id"] = proj_id
                st.session_state["video_path"] = v_path
                st.session_state["audio_path"] = a_path
                st.session_state["offset_seg"] = min_ini * 60
                st.session_state["nombre_proyecto"] = archivo.name
                st.session_state.pop("clips_encontrados", None)
                st.success("¡Archivo listo! Ahora configura el Paso 2 abajo.")

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
                placeholder="p. ej. los momentos más graciosos, cada consejo sobre dinero, las opiniones más polémicas…"
            )

            a1, a2, a3, a4 = st.columns(4)
            layout_global = a1.selectbox("📐 Encuadre", LAYOUTS_VIDEO, index=0)
            estilo_sub_global = a2.selectbox("💬 Subtítulos", list(ESTILOS_SUBTITULOS.keys()), index=1)
            num_clips = a3.slider("🎞️ Cantidad", 1, 10, 3)
            duracion_obj = a4.selectbox("⏱️ Duración", ["15 a 30 segundos", "30 a 60 segundos", "60 a 90 segundos"], index=1)

            if st.button("🚀 Buscar momentos con IA", type="primary", use_container_width=True):
                api_key = config.get("api_key", "")
                if not api_key:
                    st.error("Primero guarda tu Gemini API Key en '⚙️ Ajustes y API Key'.")
                else:
                    with st.spinner("La IA está escuchando tu vídeo y detectando los mejores clips…"):
                        clips = buscar_momentos_ia(
                            api_key,
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

                    st.success(f"¡Listo! Encontré {len(clips)} momentos virales.")

    # --- PASO 3 ---
    if "clips_encontrados" in st.session_state:
        st.markdown('<span class="step-pill">PASO 3 · RESULTADOS</span>', unsafe_allow_html=True)
        st.markdown("### Tus clips sugeridos")

        for i, clip in enumerate(st.session_state["clips_encontrados"]):
            with st.expander(f"🎬 Clip #{i+1}: {clip['titulo']}  ·  🔥 {clip['puntaje_viral']}/100", expanded=True):
                col_info, col_render = st.columns([1.8, 1.2])
                with col_info:
                    st.markdown(f'<span class="viral-badge">🔥 Viralidad {clip["puntaje_viral"]}/100</span>', unsafe_allow_html=True)
                    if clip.get("gancho_visual"):
                        st.markdown(f"**🎯 Gancho visual sugerido:** `{clip['gancho_visual']}`")
                    st.write(f"**Por qué funciona:** {clip['motivo']}")
                    st.info(f"**Magic Post (Copy para redes):**\n\n{clip['descripcion_redes']}")

                    t1, t2 = st.columns(2)
                    inicio = t1.number_input("Inicio (seg)", value=float(clip["start"]), key=f"start_{i}")
                    fin = t2.number_input("Fin (seg)", value=float(clip["end"]), key=f"end_{i}")

                    o1, o2 = st.columns(2)
                    layout_clip = o1.selectbox(
                        "Encuadre",
                        LAYOUTS_VIDEO,
                        index=LAYOUTS_VIDEO.index(layout_global) if "layout_global" in locals() else 0,
                        key=f"lay_{i}"
                    )
                    estilo_clip = o2.selectbox(
                        "Subtítulos",
                        list(ESTILOS_SUBTITULOS.keys()),
                        index=list(ESTILOS_SUBTITULOS.keys()).index(estilo_sub_global) if "estilo_sub_global" in locals() else 1,
                        key=f"substyle_{i}"
                    )

                with col_render:
                    proj_id = st.session_state.get("proj_id", "local")
                    out_file = str(CLIPS_DIR / f"{proj_id}_clip_{i+1}.mp4")

                    if st.button(f"✂️ Crear Clip #{i+1}", type="primary", use_container_width=True, key=f"render_{i}"):
                        with st.spinner("Renderizando clip en HD…"):
                            srt_temp = None
                            if estilo_clip != "Sin subtítulos" and clip.get("subtitulos"):
                                srt_temp = str(WORK_DIR / f"temp_sub_{i+1}.srt")
                                generar_srt_clip(clip["subtitulos"], srt_temp)

                            renderizar_clip(
                                st.session_state["video_path"],
                                inicio, fin, out_file,
                                layout=layout_clip,
                                estilo_sub=estilo_clip,
                                srt_filename=srt_temp
                            )
                            if srt_temp and os.path.exists(srt_temp):
                                os.remove(srt_temp)
                        st.success("¡Listo! Ya puedes abrirlo en '✂️ Editor y TikTok'.")

                    if os.path.exists(out_file):
                        st.video(out_file)
                        with open(out_file, "rb") as f:
                            st.download_button(
                                label="⬇️ Descargar MP4",
                                data=f,
                                file_name=f"clip_{i+1}_{proj_id}.mp4",
                                mime="video/mp4",
                                use_container_width=True,
                                key=f"dl_{i}"
                            )

# ==============================================================================
# PÁGINA 2: EDITOR DE VIDEO + AUTO GANCHO/TÍTULOS IA + TIKTOK
# ==============================================================================
elif pagina == "✂️ Editor y TikTok":
    st.markdown("""
    <div class="hero-box">
        <div class="hero-title">Editor Studio & TikTok 🎵</div>
        <div class="hero-sub">La IA escucha tu clip, crea el Gancho visual y los Títulos virales por ti, lo editas y lo subes directo.</div>
    </div>
    """, unsafe_allow_html=True)

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
            contexto_extra = g2.text_input("Nota extra para la IA (opcional — puedes dejarlo vacío):", placeholder="Ej: Enfócate en el giro del final...")

            if st.button("✨ Analizar este clip con IA (Auto-Gancho + 5 Títulos)", type="primary", use_container_width=True):
                api_key = config.get("api_key", "")
                if not api_key:
                    st.error("Guarda tu Gemini API Key en Ajustes primero.")
                else:
                    with st.spinner("La IA está escuchando tu clip para crear el Gancho visual y los Títulos..."):
                        res_ia = analizar_clip_para_tiktok_ia(api_key, video_elegido, tono_video, contexto_extra)
                        st.session_state["tiktok_ia"] = res_ia
                        st.session_state["hook_auto"] = res_ia.get("gancho_visual", "")
                    st.success("¡Gancho visual y títulos generados automáticamente!")

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
                    "🎯 Texto Gancho (Hook) arriba del video (rellenado por la IA):",
                    value=st.session_state.get("hook_auto", ""),
                    placeholder="Presiona el botón de IA arriba o escribe tu propio gancho..."
                )

                if st.button("✂️ Aplicar edición y quemar Gancho en el video", type="primary", use_container_width=True):
                    nombre_editado = str(EDITED_DIR / f"editado_{datetime.now().strftime('%H%M%S')}_{Path(video_elegido).name}")
                    with st.spinner("Aplicando edición con FFmpeg..."):
                        editar_video_ffmpeg(
                            video_elegido, nombre_editado, ed_ini, ed_fin,
                            velocidad, volumen, brillo, contraste, texto_hook
                        )
                    st.session_state["video_editado_actual"] = nombre_editado
                    st.success("¡Video editado con éxito!")
                    st.rerun()

        with st.container(border=True):
            st.markdown('<span class="step-pill">PUBLICAR EN TIKTOK</span>', unsafe_allow_html=True)
            titulo_final = ""
            if "tiktok_ia" in st.session_state:
                datos_tk = st.session_state["tiktok_ia"]
                titulo_elegido = st.radio("🏆 Elige uno de los 5 títulos generados por la IA:", datos_tk["titulos"])
                caption_sugerido = f"{titulo_elegido}\n\n{datos_tk['descripcion']}\n\n{datos_tk['hashtags']}"
                titulo_final = st.text_area("📝 Copy final para TikTok:", value=caption_sugerido, height=130)
            else:
                titulo_final = st.text_area("📝 Copy para TikTok (usa el botón de IA arriba para generarlo solo):", height=100)

            video_final_subir = st.session_state.get("video_editado_actual", video_elegido)
            if not os.path.exists(video_final_subir):
                video_final_subir = video_elegido

            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("🚀 Subir directo a TikTok (API)", type="primary", use_container_width=True):
                    tk_token = config.get("tiktok_token", "").strip()
                    if not tk_token:
                        st.warning("Falta tu Access Token de TikTok en Ajustes. Descarga el clip y súbelo en TikTok Studio.")
                    else:
                        try:
                            with st.spinner("Subiendo video a tu TikTok..."):
                                subir_video_tiktok_api(tk_token, video_final_subir, titulo_final)
                            st.success("¡Enviado a tu cuenta de TikTok! Revisa tu Bandeja de entrada / Borradores en la app.")
                        except Exception as e:
                            st.error(f"Error al subir vía API: {e}")

            with b2:
                with open(video_final_subir, "rb") as f:
                    st.download_button(
                        "⬇️ Descargar clip final",
                        data=f,
                        file_name=Path(video_final_subir).name,
                        mime="video/mp4",
                        use_container_width=True
                    )

            with b3:
                st.link_button("🌐 Abrir TikTok Studio", "https://www.tiktok.com/tiktokstudio/upload", use_container_width=True)

# ==============================================================================
# PÁGINA 3: MIS PROYECTOS
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
                    st.rerun()
                if c3.button("🗑️ Borrar", key=f"del_{p['id']}", use_container_width=True):
                    proyectos = [x for x in proyectos if x["id"] != p["id"]]
                    guardar_json(PROJECTS_FILE, proyectos)
                    st.rerun()

# ==============================================================================
# PÁGINA 4: AJUSTES Y API KEY
# ==============================================================================
elif pagina == "⚙️ Ajustes y API Key":
    st.markdown("""
    <div class="hero-box">
        <div class="hero-title">Ajustes del Studio ⚙️</div>
        <div class="hero-sub">Configura tus claves una sola vez para tu cuenta.</div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("#### 🔑 Clave de Inteligencia Artificial (Gemini)")
        nueva_key = st.text_input(
            "Gemini API Key",
            value=config.get("api_key", ""),
            type="password",
            placeholder="Pega aquí tu clave de Google AI Studio"
        )

        st.divider()
        st.markdown("#### 🎵 Conexión con tu cuenta de TikTok (API Oficial)")
        st.caption("Obtén tu Access Token en developers.tiktok.com con el permiso `video.upload`.")
        nuevo_tk_token = st.text_input(
            "TikTok Access Token",
            value=config.get("tiktok_token", ""),
            type="password",
            placeholder="Pega aquí tu Access Token de TikTok..."
        )

        if st.button("💾 Guardar todas las claves", type="primary"):
            config["api_key"] = nueva_key.strip()
            config["tiktok_token"] = nuevo_tk_token.strip()
            guardar_json(CONFIG_FILE, config)
            st.success("¡Claves guardadas!")

    with st.container(border=True):
        st.markdown("#### 🧹 Limpieza de archivos temporales")
        if st.button("Vaciar carpeta workspace (videos descargados)"):
            for f in WORK_DIR.glob("*"):
                try:
                    f.unlink()
                except Exception:
                    pass
            st.success("Carpeta temporal limpiada.")
