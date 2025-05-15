from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Artefacto, Fase, SubArtefacto
from .forms import ProjectForm, ArtefactoForm, CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from core.ia import generar_subartefacto_con_ia, generar_contenido_gemini
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from core.mermaid import generar_diagrama_mermaid

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

            # Crear automáticamente las fases y subartefactos
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

SUBARTEFACTOS_MERMAID = [
    "Caso de Uso",
    "Diagrama Clases",
    "Diagrama de Entidad - Relación",
    "Diagrama de Colaboración",
    "Diagrama de Actividades",
    "Diagrama de C4"
]

@login_required
def crear_artefacto(request, proyecto_id):
    proyecto = get_object_or_404(Project, id=proyecto_id, propietario=request.user)
    titulo_default = request.GET.get('subartefacto', '')
    if request.method == 'POST':
        form = ArtefactoForm(request.POST)
        if form.is_valid():
            artefacto = form.save(commit=False)
            artefacto.proyecto = proyecto
            artefacto.generado_por_ia = True
            try:
                artefacto.contenido = generar_subartefacto_con_ia(
                    tipo=artefacto.get_tipo_display(),
                    nombre_proyecto=proyecto.nombre,
                    descripcion=proyecto.descripcion
                )
            except Exception:
                artefacto.contenido = "Error al generar contenido con IA."
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
    fases = proyecto.fases.prefetch_related('subartefactos')
    return render(request, 'documentacion/detalle_proyecto.html', {
        'proyecto': proyecto,
        'artefactos': artefactos,
        'fases': fases
    })

@login_required
def ver_artefacto(request, artefacto_id):
    artefacto = get_object_or_404(Artefacto, id=artefacto_id)
    return render(request, 'documentacion/ver_artefacto.html', {
        'artefacto': artefacto
    })

def cerrar_sesion(request):
    logout(request)
    return redirect('home')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
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

@require_POST
@login_required
def eliminar_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Project, id=proyecto_id, propietario=request.user)
    proyecto.delete()
    return redirect('dashboard')

@login_required
def generar_subartefacto_modal(request, proyecto_id):
    subartefacto_nombre = request.GET.get("subartefacto", "")
    proyecto = get_object_or_404(Project, id=proyecto_id, propietario=request.user)

    if subartefacto_nombre in SUBARTEFACTOS_MERMAID:
        contenido = generar_diagrama_mermaid()
        tipo = "mermaid"
    else:
        contenido = generar_subartefacto_con_ia(
            tipo=subartefacto_nombre,
            nombre_proyecto=proyecto.nombre,
            descripcion=proyecto.descripcion
        )
        tipo = "texto"

    return JsonResponse({
        "tipo": tipo,
        "contenido": contenido,
        "titulo": subartefacto_nombre
    })

@login_required
def generar_artefacto(request, proyecto_id, subartefacto_nombre,):
    proyecto = get_object_or_404(Project, id=proyecto_id, propietario=request.user)
    subartefacto = get_object_or_404(SubArtefacto, fase__proyecto=proyecto, nombre=subartefacto_nombre)

    # Verificar si ya existe un artefacto generado para este subartefacto
    artefacto_existente = Artefacto.objects.filter(proyecto=proyecto, titulo=subartefacto.nombre).first()
    if artefacto_existente:
        return redirect('ver_artefacto', artefacto_id=artefacto_existente.id)

    if subartefacto.nombre in SUBARTEFACTOS_MERMAID:
        from core.mermaid import generar_diagrama_mermaid
        contenido = generar_diagrama_mermaid(subartefacto.nombre)
    else:
        contenido = generar_subartefacto_con_ia(
            tipo=subartefacto.nombre,
            nombre_proyecto=proyecto.nombre,
            descripcion=proyecto.descripcion
        )

    artefacto = Artefacto.objects.create(
        proyecto=proyecto,
        titulo=subartefacto.nombre,
        contenido=contenido,
        generado_por_ia=True
    )

    return redirect('ver_artefacto', artefacto_id=artefacto.id)

def editar_artefacto(request, artefacto_id):
    artefacto = get_object_or_404(Artefacto, id=artefacto_id)
    if request.method == 'POST':
        form = ArtefactoForm(request.POST, instance=artefacto)
        if form.is_valid():
            form.save()
            return redirect('ver_artefacto', artefacto_id=artefacto.id)
    else:
        form = ArtefactoForm(instance=artefacto)
    return render(request, 'documentacion/editar_artefacto.html', {'form': form, 'artefacto': artefacto})
