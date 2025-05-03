import os
from dotenv import load_dotenv
import google.generativeai as genai

# Cargar variables de entorno
load_dotenv()

# Configurar clave de API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Modelo que funciona con generateContent
MODEL = "models/gemini-1.5-pro-latest"

# Prompt base
PROMPT_BASE = """
Eres un experto en ingeniería de software. Tu tarea es generar el artefacto del tipo "{tipo}" para un proyecto llamado "{nombre_proyecto}". 
Aquí tienes una descripción del proyecto: {descripcion}

Genera el contenido del artefacto con un estilo profesional, claro, y coherente.
"""

# Función principal
def generar_artefacto_con_ia(tipo: str, nombre_proyecto: str, descripcion: str) -> str:
    prompt = PROMPT_BASE.format(
        tipo=tipo,
        nombre_proyecto=nombre_proyecto,
        descripcion=descripcion
    )

    try:
        response = genai.GenerativeModel(MODEL).generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[ERROR] No se pudo generar contenido: {e}"
