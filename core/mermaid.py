from unidecode import unidecode

# Diccionario con los diagramas predefinidos
DIAGRAMAS = {
    "diagrama_caso_uso": """
        graph TD
            Usuario -->|Inicia sesión| Sistema
            Usuario -->|Registra proyecto| Sistema
            Sistema -->|Genera artefactos| IA
    """,

    "diagrama_clases": """
        classDiagram
            class Usuario {
                +String nombre
                +String email
            }
            class Proyecto {
                +String nombre
                +List artefactos
            }
            Usuario --> Proyecto
    """,

    "diagrama_entidad_relacion": """
        erDiagram
            USUARIO ||--o{ PROYECTO : tiene
            PROYECTO ||--|{ ARTEFACTO : contiene
            ARTEFACTO {
                string tipo
                text contenido
            }
    """,

    "diagrama_colaboracion": """
        sequenceDiagram
            actor Usuario
            participant Sistema
            Usuario->>Sistema: Solicita generación
            Sistema-->>Usuario: Retorna resultado
    """,

    "diagrama_actividades": """
        graph TD
            Inicio --> Analisis
            Analisis --> Diseño
            Diseño --> Desarrollo
            Desarrollo --> Pruebas
            Pruebas --> Despliegue
            Despliegue --> Fin
    """,

    "diagrama_c4": """
        graph TD
            Cliente[Cliente] --> App[Aplicación Web]
            App --> BBDD[(Base de Datos)]
            App --> IA[Motor IA]
    """
}

def generar_diagrama_mermaid(tipo: str) -> str:
    """
    Genera un diagrama en formato Mermaid según el tipo especificado.
    """
    if not tipo:
        return "[ERROR] Debes especificar un tipo de diagrama."

    tipo_normalizado = unidecode(tipo.lower().replace(" ", "_"))

    return DIAGRAMAS.get(tipo_normalizado, "[ERROR] Tipo de diagrama no válido.")
