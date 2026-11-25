import streamlit as st
import subprocess
import json
import os
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from google import genai
from google.genai import types

st.set_page_config(
    page_title="Inicio | Mi Clipper IA",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SISTEMA DE ACTUALIZACIONES AUTOMÁTICAS ---
VERSION_ACTUAL = "1.0.0"
# Cambia TU_USUARIO por tu nombre de usuario de GitHub
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

# --- ESTILO VISUAL INSPIRADO EN NEXUSCLIPS (PLUS JAKARTA SANS + HORIZON GLOW) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    .stApp {
        background:
            radial-gradient(circle at 50% -10%, rgba(124, 58, 237, 0.35) 0%, rgba(15, 12, 41, 0) 55%),
            radial-gradient(circle at 85% 20%, rgba(236, 72, 153, 0.18) 0%, rgba(15, 12, 41, 0) 45%),
            linear-gradient(180deg, #0b0b12 0%, #11111d 100%);
        color: #f4f4f8;
    }

    [data-testid="stSidebar"] {
        background: #0d0d16;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    .stExpander {
        background: rgba(255, 255, 255, 0.035) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 14px !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #7c3aed 0%, #db2777 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.55rem 1.2rem !important;
        box-shadow: 0 4px 18px rgba(124, 58, 237, 0.35);
        transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 24px rgba(219, 39, 119, 0.5);
    }

    .stButton > button {
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        background: rgba(255, 255, 255, 0.04) !important;
        color: #e4e4ec !important;
        font-weight: 500 !important;
    }
    .stButton > button:hover {
        border-color: #8b5cf6 !important;
        background: rgba(139, 92, 246, 0.15) !important;
        color: #ffffff !important;
    }

    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #ffffff 0%, #c084fc 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .hero-sub {
        text-align: center;
        color: #a1a1b5;
        font-size: 0.98rem;
        margin-bottom: 1.5rem;
    }

    .viral-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 700;
        background: rgba(16, 185, 129, 0.18);
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.35);
    }
</style>
""", unsafe_allow_html=True)

# --- RUTAS Y ARCHIVOS LOCALES ---
WORK_DIR = Path("workspace")
CLIPS_DIR = Path("clips_generados")
CONFIG_FILE = Path("config_clipper.json")
PROJECTS_FILE = Path("proyectos.json")
WORK_DIR.mkdir(exist_ok=True)
CLIPS_DIR.mkdir(exist_ok=True)

# --- ESTILOS DE SUBTÍTULOS Y ENCUADRES ---
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

# --- FUNCIONES DE VIDEO E IA ---

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
                st.error(f"Los servidores de Gemini están saturados en este momento. Intenta de nuevo en unos segundos.\nDetalle: {e}")
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

# --- NAVEGACIÓN LATERAL ---

with st.sidebar:
    st.markdown(f"## ⚡ Mi Clipper IA `v{VERSION_ACTUAL}`")
    pagina = st.radio(
        "Navegación",
        ["💬 Inicio (Chat IA)", "📁 Mis Proyectos", "⚙️ Ajustes y API Key"],
        label_visibility="collapsed"
    )

    st.divider()
    if config.get("api_key"):
        st.success("🔑 API Key activa y guardada")
    else:
        st.warning("⚠️ Falta guardar tu API Key en Ajustes")

    if st.button("🔄 Buscar actualizaciones", use_container_width=True):
        st.session_state.pop("update_checked", None)
        revisar_actualizacion()
        if "nueva_version" in st.session_state:
            st.rerun()
        else:
            st.toast("Ya tienes la última versión instalada.", icon="✅")

    if proyectos:
        st.divider()
        st.caption("Proyectos recientes")
        for p in proyectos[:5]:
            if st.button(f"🎬 {p['nombre'][:24]}", key=f"side_p_{p['id']}", use_container_width=True):
                st.session_state["proyecto_activo"] = p
                st.session_state["ir_a_resultados"] = True
                st.rerun()

# ==============================================================================
# PÁGINA 1: INICIO / CHAT IA
# ==============================================================================
if pagina == "💬 Inicio (Chat IA)":
    st.markdown('<div class="hero-title">¿Qué creamos hoy?</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Trae tu vídeo de YouTube, Twitch o tu PC, dile al chat qué momentos buscar y recibe tus clips listos para publicar.</div>', unsafe_allow_html=True)

    if st.session_state.pop("ir_a_resultados", False) and "proyecto_activo" in st.session_state:
        p = st.session_state["proyecto_activo"]
        st.session_state["proj_id"] = p["id"]
        st.session_state["video_path"] = p["video_path"]
        st.session_state["audio_path"] = p["audio_path"]
        st.session_state["clips_encontrados"] = p["clips"]
        st.session_state["nombre_proyecto"] = p["nombre"]

    # --- PASO 1: TRAER TU VÍDEO ---
    with st.container():
        st.markdown("#### 1️⃣ Trae tu vídeo")
        tab_link, tab_file = st.tabs(["🔗 Pega un enlace (YouTube / Twitch / TikTok)", "📁 Subir un archivo desde tu PC"])

        col_r1, col_r2, col_r3 = st.columns([2, 1, 1])
        modo_rango = col_r1.radio("¿Cuánto vídeo importamos?", ["Todo el vídeo", "Solo una parte (para vídeos largos)"], horizontal=True)
        min_ini = 0.0
        min_fin = 0.0
        if modo_rango == "Solo una parte (para vídeos largos)":
            min_ini = col_r2.number_input("Inicio (minutos)", min_value=0.0, value=0.0, step=1.0)
            min_fin = col_r3.number_input("Fin (minutos)", min_value=0.0, value=10.0, step=1.0)

        with tab_link:
            url_input = st.text_input("Enlace del vídeo:", placeholder="https://www.youtube.com/watch?v=...")
            if st.button("⬇️ Importar vídeo", type="primary", key="btn_import_url"):
                if not url_input:
                    st.warning("Pega un enlace primero.")
                else:
                    proj_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                    with st.spinner("Importando vídeo..."):
                        v_path = descargar_video(url_input, proj_id)
                    with st.spinner("Preparando audio para la IA..."):
                        a_path = extraer_audio(v_path, proj_id, min_ini, min_fin)
                    st.session_state["proj_id"] = proj_id
                    st.session_state["video_path"] = v_path
                    st.session_state["audio_path"] = a_path
                    st.session_state["offset_seg"] = min_ini * 60
                    st.session_state["nombre_proyecto"] = f"Video {proj_id}"
                    st.session_state.pop("clips_encontrados", None)
                    st.success("¡Ya lo tengo! Ahora dime qué quieres hacer con el vídeo.")

        with tab_file:
            archivo = st.file_uploader("Arrastra aquí tu archivo MP4, MOV o MKV", type=["mp4", "mov", "mkv"])
            if archivo and st.button("⚙️ Preparar archivo", type="primary", key="btn_import_file"):
                proj_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                v_path = str(WORK_DIR / f"video_{proj_id}.mp4")
                with open(v_path, "wb") as f:
                    f.write(archivo.read())
                with st.spinner("Preparando audio para la IA..."):
                    a_path = extraer_audio(v_path, proj_id, min_ini, min_fin)
                st.session_state["proj_id"] = proj_id
                st.session_state["video_path"] = v_path
                st.session_state["audio_path"] = a_path
                st.session_state["offset_seg"] = min_ini * 60
                st.session_state["nombre_proyecto"] = archivo.name
                st.session_state.pop("clips_encontrados", None)
                st.success("¡Ya lo tengo! Ahora dime qué quieres hacer con el vídeo.")

    # --- PASO 2: BRIEF CONVERSACIONAL ---
    if "audio_path" in st.session_state:
        st.divider()
        st.markdown("#### 2️⃣ Dile al chat qué momentos buscar y el estilo")

        c1, c2, c3, c4, c5 = st.columns(5)
        if c1.button("✨ Los elegimos solos", use_container_width=True):
            st.session_state["prompt_chat"] = "Encuentra los mejores momentos con mayor gancho inicial y potencial viral."
        if c2.button("😂 Momentos graciosos", use_container_width=True):
            st.session_state["prompt_chat"] = "Busca los momentos más graciosos, bromas, risas y reacciones divertidas."
        if c3.button("🧠 Mejores consejos", use_container_width=True):
            st.session_state["prompt_chat"] = "Extrae cada consejo práctico, explicación de valor o dato clave."
        if c4.button("🔥 Opiniones polémicas", use_container_width=True):
            st.session_state["prompt_chat"] = "Encuentra las opiniones más polémicas, debates o declaraciones fuertes."
        if c5.button("📖 Historias", use_container_width=True):
            st.session_state["prompt_chat"] = "Busca las mejores anécdotas o historias completas de principio a fin."

        instruccion = st.text_area(
            "¿Qué momentos buscamos? (si lo dejas en blanco, los elegimos nosotros)",
            value=st.session_state.get("prompt_chat", ""),
            placeholder="p. ej. los momentos más graciosos, cada consejo sobre dinero, las opiniones más polémicas…"
        )

        a1, a2, a3, a4 = st.columns(4)
        layout_global = a1.selectbox("📐 Encuadre", LAYOUTS_VIDEO, index=0)
        estilo_sub_global = a2.selectbox("💬 Estilo de subtítulos", list(ESTILOS_SUBTITULOS.keys()), index=1)
        num_clips = a3.slider("🎞️ Cuántos clips", 1, 10, 3)
        duracion_obj = a4.selectbox("⏱️ Duración", ["15 a 30 segundos", "30 a 60 segundos", "60 a 90 segundos"], index=1)

        if st.button("🚀 Empezar — Buscar momentos con IA", type="primary", use_container_width=True):
            api_key = config.get("api_key", "")
            if not api_key:
                st.error("Primero guarda tu Gemini API Key en la pestaña '⚙️ Ajustes y API Key' de la izquierda.")
            else:
                with st.spinner("Entendiendo tu vídeo y buscando los mejores momentos…"):
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

                st.success(f"¡Listo! Encontré {len(clips)} momentos listos para renderizar.")

    # --- PASO 3: RESULTADOS Y RENDERIZADO ---
    if "clips_encontrados" in st.session_state:
        st.divider()
        st.markdown("#### 3️⃣ Tus clips sugeridos")

        for i, clip in enumerate(st.session_state["clips_encontrados"]):
            with st.expander(f"Clip #{i+1}: {clip['titulo']}  |  Viralidad: {clip['puntaje_viral']}/100", expanded=True):
                col_info, col_render = st.columns([1.8, 1.2])
                with col_info:
                    st.markdown(f'<span class="viral-badge">🔥 Viralidad {clip["puntaje_viral"]}/100</span>', unsafe_allow_html=True)
                    st.write(f"**Por qué funciona:** {clip['motivo']}")
                    st.info(f"**Magic Post (Copy listo para redes):**\n\n{clip['descripcion_redes']}")

                    t1, t2 = st.columns(2)
                    inicio = t1.number_input("Inicio (seg)", value=float(clip["start"]), key=f"start_{i}")
                    fin = t2.number_input("Fin (seg)", value=float(clip["end"]), key=f"end_{i}")

                    o1, o2 = st.columns(2)
                    layout_clip = o1.selectbox(
                        "Encuadre de este clip",
                        LAYOUTS_VIDEO,
                        index=LAYOUTS_VIDEO.index(layout_global) if "layout_global" in locals() else 0,
                        key=f"lay_{i}"
                    )
                    estilo_clip = o2.selectbox(
                        "Subtítulos de este clip",
                        list(ESTILOS_SUBTITULOS.keys()),
                        index=list(ESTILOS_SUBTITULOS.keys()).index(estilo_sub_global) if "estilo_sub_global" in locals() else 1,
                        key=f"substyle_{i}"
                    )

                with col_render:
                    proj_id = st.session_state.get("proj_id", "local")
                    out_file = str(CLIPS_DIR / f"{proj_id}_clip_{i+1}.mp4")

                    if st.button(f"✂️ Crear Clip #{i+1}", type="primary", use_container_width=True, key=f"render_{i}"):
                        with st.spinner("Renderizando tu clip en HD…"):
                            srt_temp = None
                            if estilo_clip != "Sin subtítulos" and clip.get("subtitulos"):
                                srt_temp = f"temp_sub_{i+1}.srt"
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
                        st.success("¡Clip listo!")

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
# PÁGINA 2: MIS PROYECTOS
# ==============================================================================
elif pagina == "📁 Mis Proyectos":
    st.markdown('<div class="hero-title">Tus Proyectos</div>', unsafe_allow_html=True)
    busqueda = st.text_input("🔍 Buscar proyectos…", placeholder="Escribe el nombre del proyecto")

    filtrados = [p for p in proyectos if busqueda.lower() in p["nombre"].lower()]
    if not filtrados:
        st.info("Aún no tienes proyectos guardados. Crea tu primer proyecto en Inicio.")
    else:
        for p in filtrados:
            with st.container():
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.markdown(f"**🎬 {p['nombre']}** — `{len(p['clips'])} clips` · _{p['fecha']}_")
                if c2.button("Abrir", key=f"open_{p['id']}", use_container_width=True):
                    st.session_state["proyecto_activo"] = p
                    st.session_state["ir_a_resultados"] = True
                    st.rerun()
                if c3.button("🗑️ Borrar", key=f"del_{p['id']}", use_container_width=True):
                    proyectos = [x for x in proyectos if x["id"] != p["id"]]
                    guardar_json(PROJECTS_FILE, proyectos)
                    st.rerun()
                st.divider()

# ==============================================================================
# PÁGINA 3: AJUSTES Y API KEY
# ==============================================================================
elif pagina == "⚙️ Ajustes y API Key":
    st.markdown('<div class="hero-title">Ajustes</div>', unsafe_allow_html=True)
    st.markdown("#### 🔑 Clave de Inteligencia Artificial (Gemini)")
    nueva_key = st.text_input(
        "Gemini API Key",
        value=config.get("api_key", ""),
        type="password",
        placeholder="Pega aquí tu clave de Google AI Studio"
    )
    if st.button("💾 Guardar Key permanentemente", type="primary"):
        config["api_key"] = nueva_key.strip()
        guardar_json(CONFIG_FILE, config)
        st.success("¡Guardado! Tu API Key quedará lista cada vez que abras el programa.")

    st.divider()
    st.markdown("#### 🧹 Limpieza de archivos temporales")
    st.caption("Los clips que generes se guardan en la carpeta `clips_generados` dentro de `generador clips`.")
    if st.button("Vaciar carpeta workspace (videos descargados)"):
        for f in WORK_DIR.glob("*"):
            try:
                f.unlink()
            except Exception:
                pass
        st.success("Carpeta temporal limpiada.")
