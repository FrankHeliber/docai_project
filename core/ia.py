import os
from dotenv import load_dotenv
import google.generativeai as genai

# Cargar variables de entorno
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("La clave de API GEMINI_API_KEY no está configurada.")

genai.configure(api_key=api_key)
MODEL = "models/gemini-2.0-flash"

# ===== PROMPTS PERSONALIZADOS =====

PROMPTS = {
    "Historia de Usuario": lambda nombre_proyecto, descripcion: (
        f"Dame historias de usuario enumeradas con HU y el número secuencial para un proyecto de software llamado '{nombre_proyecto}' y con la siguiente descripción '{descripcion}'. "
        "Con la estructura: Como, Quiero, Para. No le des formato a la respuesta. Ni uses lenguaje técnico."
    ),

    "Diagrama de flujo": lambda texto: {
        "Genera un solo diagrama de flujo donde estén todos los usuarios en ese mismo diagrama usando la sintaxis Markdown de Mermaid basado en las siguientes historias de usuario:\n\n"
        f"{texto}\n\n"
        "El diagrama debe mostrar el flujo principal de acciones y decisiones descritas en las historias, "
        "incluyendo un solo inicio, pasos de cada uno de los actores, decisiones y finalización. Usa nodos claros y conecta con flechas para mostrar el flujo.\n\n"
        "Devuelve sólo el bloque de código con sintaxis Mermaid listo para copiar y pegar, sin texto adicional ni explicaciones.\n\n"
        "Ejemplo de formato:\n"
        "Ten en cuenta no empezar con backticks ni terminar con backticks, ni empezar con la palabra mermaid, además no uses paréntesis\n"
        "flowchart TD\n"
        "    A[Inicio] --> B[Primer paso]\n"
        "    B --> C{¿Decisión?}\n"
        "    C -->|Sí| D[Acción 1]\n"
        "    C -->|No| E[Acción 2]\n"
        "    D --> F[Fin]\n"
        "    E --> F[Fin]"
    },

    "Diagrama de clases": lambda texto: {
        "Genera un diagrama de clases en sintaxis Mermaid basado en el siguiente texto:\n\n"
        f"{texto}\n\n"
        "Incluye las siguientes características:\n"
        "- Clases con nombres claros.\n"
        "- Atributos con tipo y visibilidad (+ público, - privado, # protegido).\n"
        "- Métodos con parámetros y visibilidad.\n"
        "- Relaciones entre clases: herencia (<|--), asociación (--), composición (*--), agregación (o--).\n"
        "- Multiplicidades cuando correspondan.\n"
        "-no utilices explicaciones del diagrama.\n"
        "classDiagram\n"
        "    class Usuario {\n"
        "        +nombre: String\n"
        "        +login()\n"
        "    }\n"
        "    class Cliente {\n"
        "        +id: Int\n"
        "        +realizarCompra()\n"
        "    }\n"
        "    Usuario <|-- Cliente\n"
        "    Cliente *-- Pedido : realiza\n"
        "    Pedido o-- Producto : contiene"
    },

    "Diagrama de Entidad-Relacion": lambda texto: (
        "Genera un diagrama entidad-relación (ER) en sintaxis Mermaid basado en el siguiente texto:\n\n"
        f"{texto}\n\n"
        "Por favor, sigue estas indicaciones:\n"
        "- Usa direction TB o LR.\n"
        "- Usa ||, |o, }o, }| para cardinalidades.\n"
        "- Usa erDiagram y bloques de entidad.\n"
        "- Ejemplo:\n"
        "erDiagram\n"
        "    CLIENTE {\n"
        "        int id\n"
        "        string nombre\n"
        "    }\n"
        "    PEDIDO {\n"
        "        int id\n"
        "        date fecha\n"
        "    }\n"
        "    CLIENTE ||--o{ PEDIDO : realiza\n"
        "    PEDIDO }o--|| PRODUCTO : contiene"
    ),

    "Diagrama de secuencia": lambda texto: (
        "Genera un diagrama de secuencia en sintaxis Mermaid basado en el siguiente texto:\n\n"
        f"{texto}\n\n"
        "Incluye actores, objetos, mensajes y retornos.\n"
        "-no utilices explicaciones del diagrama.\n"
        "Ejemplo:\n"
        "sequenceDiagram\n"
        "    participant Usuario\n"
        "    participant Sistema\n"
        "    Usuario->>Sistema: Solicita iniciar sesión\n"
        "    Sistema-->>Usuario: Muestra pantalla principal"
    ),

    "Diagrama de estado": lambda texto: (
        "Genera un diagrama de estados en sintaxis Mermaid basado en el siguiente texto:\n\n"
        "-no utilices explicaciones del diagrama.\n"
        f"{texto}\n\n"
        "Ejemplo:\n"
        "stateDiagram-v2\n"
        "    [*] --> Estado1\n"
        "    Estado1 --> Estado2: eventoA\n"
        "    Estado2 --> Estado3: eventoB\n"
        "    Estado3 --> [*]"
    ),

    "Diagrama de C4": lambda texto: (
        "Eres un ingeniero de software experto en modelado arquitectónico. Tu tarea es generar un diagrama C4 de nivel Contexto en sintaxis Mermaid usando la notación `C4Context`.\n\n"
        f"Basado en el siguiente texto del proyecto:\n{texto}\n\n"
        "Reglas para generar el código:\n"
        "- Comienza con `C4Context`\n"
        "- No uses la palabra `mermaid` ni el bloque de backticks (```) en ningún momento\n"
        "- Declara los elementos primero: `Person`, `System`, `System_Ext` (sin anidamientos)\n"
        "- Luego declara las relaciones con `Rel(...)` o `BiRel(...)`, siempre por fuera, nunca dentro de `Person` o `System`\n"
        "- Si usas `Enterprise_Boundary`, asegúrate de abrir `{` y cerrar `}` correctamente (sin llaves de más)\n"
        "- El código debe ser válido para Mermaid.js sin errores de sintaxis\n"
        "- Incluye etiquetas, descripciones y estilos si aporta claridad, pero manténlo legible\n\n"
        "Ejemplo válido:\n"
        "C4Context\n"
        "    Person(admin, \"Administrador\", \"Gestiona el sistema\")\n"
        "    System(sistema_web, \"Sistema Web\", \"Permite registrar y consultar datos\")\n"
        "    BiRel(admin, sistema_web, \"Usa\")\n"
        "    Enterprise_Boundary(empresa, \"Empresa\") {\n"
        "        Person(cliente, \"Cliente\", \"Utiliza la plataforma\")\n"
        "        System(servicio_api, \"API\", \"Expone funcionalidades REST\")\n"
        "        Rel(cliente, servicio_api, \"Consume\")\n"
        "    }"
    ),
        
    "caja negra": lambda nombre_proyecto, descripcion: (
        "Genera casos de prueba de caja negra detallados basados en el siguiente texto o historias de usuario:\n\n"
        f"{nombre_proyecto, descripcion}\n\n"
        "Para cada caso de prueba, estructura la información de la siguiente forma sin ningún formato enriquecido" 
        "(sin negritas, sin cursivas, sin listas con viñetas, solo texto plano):\n"
        "- Identificador: con formato PCN-01, PCN-02, PCN-03, ...\n"
        "- Nombre de la prueba de caja negra\n"
        "- Propósito\n"
        "- Prerrequisito\n"
        "- Datos de entrada\n"
        "- Pasos para realizar la prueba\n"
        "- Resultado esperado\n"
        "Devuelve sólo el texto claro y estructurado siguiendo este formato para cada caso de prueba, sin numeraciones o texto adicional fuera de la estructura."
    ),

    "smoke": lambda nombre_proyecto, descripcion: (
        "Genera pruebas smoke (pruebas rápidas y mínimas) para validar funcionalidad esencial según el siguiente texto:\n\n"
        f"{nombre_proyecto, descripcion}\n\n"
        "Devuelve sólo el texto claro y estructurado siguiendo este formato smoke, sin numeraciones o texto adicional fuera de la estructura."
        #"Incluye nombre de la prueba, propósito, pasos mínimos y resultado esperado. Usa formato plano y claro."
    ),
}

# ===== FUNCIONES DE GENERACIÓN =====

def _generar_contenido(prompt: str) -> str:
    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[ERROR] No se pudo generar contenido: {e}"

def generar_subartefacto_con_prompt(tipo: str, **kwargs) -> str:
    if tipo not in PROMPTS:
        raise ValueError (f"[ERROR] Tipo de artefacto desconocido: {tipo}")

    prompt_func = PROMPTS[tipo]
    prompt = prompt_func(**kwargs)
    return _generar_contenido(prompt)
