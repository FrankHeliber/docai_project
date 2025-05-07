from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Artefacto, EvaluacionCoherencia
from .forms import ProjectForm, ArtefactoForm
from django.contrib.auth.decorators import login_required
#from django.contrib.auth.forms import UserCreationForm
from .models import Project, Fase, SubArtefacto  # 👈 importa Fase y SubArtefacto
from .forms import CustomUserCreationForm  # no UserCreationForm
from django.contrib.auth import login
from django.contrib.auth import logout
from core.ia import generar_artefacto_con_ia
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest

@login_required
def dashboard(request):
    proyectos = Project.objects.filter(propietario=request.user)
    return render(request, 'documentacion/dashboard.html', {'proyectos': proyectos})

def crear_proyecto(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            proyecto = form.save(commit=False)
            proyecto.propietario = request.user
            proyecto.save()

            # Crear automáticamente las fases y subartefactos 👇
            fases_con_subartefactos = {
                "Análisis Requisitos": ["Historia de Usuario", "Caso de Uso"],
                "Diseño": ["Diagrama Clases", "Diagrama de Entidad - Relación"],
                "Desarrollo": ["Diagrama de Colaboración", "Diagrama de Actividades"],
                "Pruebas": ["Caja Negra", "Smoke"],
                "Despliegue": ["Diagrama de C4"]
            }

            for nombre_fase, subartefactos in fases_con_subartefactos.items():
                fase = Fase.objects.create(proyecto=proyecto, nombre=nombre_fase)
                for nombre_sub in subartefactos:
                    SubArtefacto.objects.create(fase=fase, nombre=nombre_sub)

            return redirect('dashboard')
    else:
        form = ProjectForm()
    return render(request, 'documentacion/crear_proyecto.html', {'form': form})

# codigo nuevo 
SUBARTEFACTOS_MERMAID = [
    "Caso de Uso",
    "Diagrama Clases",
    "Diagrama de Entidad - Relación",
    "Diagrama de Colaboración",
    "Diagrama de Actividades",
    "Diagrama de C4"
]

#codigo nuevo 
@login_required
def crear_artefacto(request, proyecto_id):
    proyecto = get_object_or_404(Project, id=proyecto_id, propietario=request.user)
    titulo_default = request.GET.get('subartefacto', '')

    if not titulo_default:
        return HttpResponseBadRequest("Subartefacto no especificado.")

    if request.method == 'POST':
        form = ArtefactoForm(request.POST)
        if form.is_valid():
            artefacto = form.save(commit=False)
            artefacto.proyecto = proyecto
            artefacto.generado_por_ia = True
            artefacto.titulo = titulo_default

            if titulo_default in SUBARTEFACTOS_MERMAID:
                artefacto.contenido = generar_contenido_mermaid(titulo_default)
            else:
                artefacto.contenido = generar_artefacto_con_ia(
                    tipo=titulo_default,
                    nombre_proyecto=proyecto.nombre,
                    descripcion=proyecto.descripcion
                )

            artefacto.save()
            return redirect('detalle_proyecto', proyecto_id=proyecto.id)
    else:
        form = ArtefactoForm(initial={'titulo': titulo_default})

    return render(request, 'documentacion/crear_artefacto.html', {
        'form': form,
        'proyecto': proyecto
    })

@login_required
def detalle_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Project, id=proyecto_id, propietario=request.user)
    artefactos = proyecto.artefactos.all()
    fases = proyecto.fases.prefetch_related('subartefactos')  # 👈 importante
    return render(request, 'documentacion/detalle_proyecto.html', {
        'proyecto': proyecto,
        'artefactos': artefactos,
        'fases': fases  # 👈 pasa las fases
    })

@login_required
def ver_artefacto(request, artefacto_id):
    artefacto = get_object_or_404(Artefacto, id=artefacto_id)
    return render(request, 'documentacion/ver_artefacto.html', {
        'artefacto': artefacto
    })

#def ver_artefacto(request, artefacto_id):
#    artefacto = get_object_or_404(Artefacto, id=artefacto_id)
#    evaluaciones = artefacto.evaluaciones.all()
#    return render(request, 'documentacion/ver_artefacto.html', {
#        'artefacto': artefacto,
#        'evaluaciones': evaluaciones
#    })

def cerrar_sesion(request):
    logout(request)
    return redirect('home')  # o la página que desees


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']  # guardar email
            user.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def lista_proyectos(request):
    proyectos = Project.objects.filter(propietario=request.user)
    return render(request, 'documentacion/dashboard.html', {'proyectos': proyectos})
# codigo para editar proyecto
def editar_proyecto(request, pk):
    proyecto = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=proyecto)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProjectForm(instance=proyecto)
    return render(request, 'documentacion/editar_proyecto.html', {'form': form, 'proyecto': proyecto})
# PARA ELIMINAR PROYECTO 
@require_POST
@login_required
def eliminar_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Project, id=proyecto_id, propietario=request.user)
    proyecto.delete()
    return redirect('dashboard')

#codigo nuevo 
def generar_contenido_mermaid(titulo):
    ejemplos = {
        "Caso de Uso": """
```mermaid
%% Diagrama de caso de uso
graph TD
    Usuario -->|Solicita| Sistema
    Sistema -->|Responde| Usuario
```""",
        "Diagrama Clases": """
```mermaid
classDiagram
    class Usuario {
        +string nombre
        +string email
        +login()
    }
    class Proyecto {
        +string nombre
        +crearArtefacto()
    }
    Usuario --> Proyecto
```""",
        "Diagrama de Actividades": """
```mermaid
flowchart TD
    Inicio --> ValidarDatos
    ValidarDatos -->|Datos válidos| GenerarArtefacto
    GenerarArtefacto --> Fin
    ValidarDatos -->|Error| MostrarError
    MostrarError --> Fin
```"""
    }

    return ejemplos.get(titulo, f"```mermaid\nflowchart TD\n    Start --> End\n```")
