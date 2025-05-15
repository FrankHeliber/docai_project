import os
from dotenv import load_dotenv
import google.generativeai as genai

# Cargar variables de entorno
load_dotenv()

# Configurar clave de API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("La clave de API GEMINI_API_KEY no está configurada en las variables de entorno.")

genai.configure(api_key=api_key)

# Modelo recomendado por Google para respuesta rápida
MODEL = "models/gemini-2.0-flash"

# Prompt base
PROMPT_BASE = """
Eres un experto en ingeniería de software. Tu tarea es generar el artefacto del tipo "{tipo}" para un proyecto llamado "{nombre_proyecto}". 
Aquí tienes una descripción del proyecto: {descripcion}

Genera el contenido del artefacto con un estilo profesional, claro, y coherente.
"""

def _generar_contenido(prompt: str) -> str:
    """Función interna para generar contenido a partir de un prompt dado."""
    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[ERROR] No se pudo generar contenido: {e}"

def generar_subartefacto_con_ia(tipo: str, nombre_proyecto: str, descripcion: str) -> str:
    """
    Genera un subartefacto utilizando IA.
    """
    if not tipo or not nombre_proyecto or not descripcion:
        return "[ERROR] Todos los campos son requeridos para generar el artefacto."

    prompt = PROMPT_BASE.format(
        tipo=tipo,
        nombre_proyecto=nombre_proyecto,
        descripcion=descripcion
    )
    return _generar_contenido(prompt)

def generar_contenido_gemini(prompt: str) -> str:
    """
    Genera contenido utilizando un prompt libre.
    """
    if not prompt:
        return "[ERROR] El prompt no puede estar vacío."
    return _generar_contenido(prompt)

def generar_subtareas(prompt_usuario: str) -> str:
    """
    Genera subtareas con IA a partir del prompt del usuario.
    """
    if not prompt_usuario:
        return "[ERROR] El prompt no puede estar vacío."
    return _generar_contenido(prompt_usuario)
