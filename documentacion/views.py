from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login, logout
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from .models import Project, Artefacto, Fase, SubArtefacto
from .forms import ProjectForm, ArtefactoForm, CustomUserCreationForm
from core.ia import generar_subartefacto_con_prompt

# ===== TIPOS DE ARTEFACTOS DEFINIDOS DIRECTAMENTE =====

ARTEFACTOS_TEXTO = [
    "Historia de Usuario",
    "caja negra",
    "smoke"
]

ARTEFACTOS_MERMAID = [
    "Diagrama de flujo",
    "Diagrama de clases",
    "Diagrama de Entidad-Relacion",
    "Diagrama de secuencia",
    "Diagrama de estado",
    "Diagrama de C4"
]

ARTEFACTOS_VALIDOS = set(ARTEFACTOS_TEXTO + ARTEFACTOS_MERMAID)

# ===== UTILIDAD PARA LIMPIAR BLOQUES MERMAID =====

def limpiar_mermaid(texto):
    texto = texto.strip()
    if texto.startswith("```mermaid"):
        texto = texto.replace("```mermaid", "", 1).strip()
    if texto.endswith("```"):
        texto = texto[:texto.rfind("```")].strip()
    return texto

# ========================= DASHBOARD =========================

@login_required
def dashboard(request):
    proyectos = Project.objects.filter(propietario=request.user).order_by('-creado')
    return render(request, 'documentacion/dashboard.html', {'proyectos': proyectos})

# ===================== CREAR Y EDITAR PROYECTOS =====================

@login_required
def crear_proyecto(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            proyecto = form.save(commit=False)
            proyecto.propietario = request.user
            proyecto.save()

            fases_con_subartefactos = {
                "Análisis Requisitos": ["Historia de Usuario", "Diagrama de flujo"],
                "Diseño": ["Diagrama de clases", "Diagrama de Entidad-Relacion"],
                "Desarrollo": ["Diagrama de secuencia", "Diagrama de estado"],
                "Pruebas": ["caja negra", "smoke"],
                "Despliegue": ["Diagrama de C4"]
            }

            for nombre_fase, subartefactos in fases_con_subartefactos.items():
                fase = Fase.objects.create(proyecto=proyecto, nombre=nombre_fase)
                SubArtefacto.objects.bulk_create([
                    SubArtefacto(fase=fase, nombre=nombre_sub) for nombre_sub in subartefactos
                ])

            return redirect('dashboard')
    else:
        form = ProjectForm()
    return render(request, 'documentacion/crear_proyecto.html', {'form': form})

@login_required
def editar_proyecto(request, pk):
    proyecto = get_object_or_404(Project, pk=pk, propietario=request.user)
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

# ===================== REGISTRO Y SESIÓN =====================

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()

            # Autenticar con username y password1 para obtener el backend
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "No se pudo iniciar sesión automáticamente. Intenta iniciar sesión manualmente.")
                return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})

def cerrar_sesion(request):
    logout(request)
    return redirect('home')

# ===================== DETALLE PROYECTO =====================

@login_required
def detalle_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Project, id=proyecto_id, propietario=request.user)
    fases = proyecto.fases.prefetch_related('subartefactos')
    artefactos = proyecto.artefactos.select_related('fase', 'subartefacto')
    return render(request, 'documentacion/detalle_proyecto.html', {
        'proyecto': proyecto,
        'fases': fases,
        'artefactos': artefactos
    })

# ===================== ARTEFACTOS =====================

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
                if artefacto.get_tipo_display() in ARTEFACTOS_TEXTO:
                    contenido = generar_subartefacto_con_prompt(
                        tipo=artefacto.get_tipo_display(),
                        nombre_proyecto=proyecto.nombre,
                        descripcion=proyecto.descripcion
                    )
                else:
                    contenido = generar_subartefacto_con_prompt(
                        tipo=artefacto.get_tipo_display(),
                        texto=proyecto.descripcion
                    )
                    contenido = limpiar_mermaid(contenido)
                artefacto.contenido = contenido
            except Exception as e:
                import traceback
                artefacto.contenido = f"[ERROR IA] {str(e)}\n{traceback.format_exc()}"
            artefacto.save()
            return redirect('detalle_proyecto', proyecto_id=proyecto.id)
    else:
        form = ArtefactoForm(initial={'titulo': titulo_default})
    
    return render(request, 'documentacion/crear_artefacto.html', {
        'form': form,
        'proyecto': proyecto
    })

@login_required
def editar_artefacto(request, artefacto_id):
    artefacto = get_object_or_404(Artefacto, id=artefacto_id, proyecto__propietario=request.user)
    proyecto = artefacto.proyecto

    if request.method == 'POST':
        form = ArtefactoForm(request.POST, instance=artefacto)
        regenerar = 'regenerar' in request.POST

        if form.is_valid():
            artefacto = form.save(commit=False)

            if regenerar:
                try:
                    if artefacto.titulo in ARTEFACTOS_TEXTO:
                        contenido = generar_subartefacto_con_prompt(
                            tipo=artefacto.titulo,
                            nombre_proyecto=proyecto.nombre,
                            descripcion=proyecto.descripcion
                        )
                    else:
                        contenido = generar_subartefacto_con_prompt(
                            tipo=artefacto.titulo,
                            texto=proyecto.descripcion
                        )
                        contenido = limpiar_mermaid(contenido)

                    artefacto.contenido = contenido
                    artefacto.generado_por_ia = True
                    messages.success(request, 'Artefacto regenerado correctamente con IA.')
                except Exception as e:
                    import traceback
                    artefacto.contenido = f"[ERROR IA] {str(e)}\n{traceback.format_exc()}"
                    messages.error(request, '❌ Error al regenerar con IA.')
            else:
                messages.success(request, 'Artefacto actualizado correctamente.')

            artefacto.save()
            return redirect('ver_artefacto', artefacto_id=artefacto.id)
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = ArtefactoForm(instance=artefacto)

    return render(request, 'documentacion/editar_artefacto.html', {
        'form': form,
        'artefacto': artefacto
    })

#para eliminar artefacto
@login_required
def eliminar_artefacto(request, artefacto_id):
    artefacto = get_object_or_404(Artefacto, id=artefacto_id, proyecto__propietario=request.user)
    proyecto_id = artefacto.proyecto.id
    artefacto.delete()
    messages.success(request, "Artefacto eliminado correctamente.")
    return redirect('detalle_proyecto', proyecto_id=proyecto_id)

# ===================== VER ARTEFACTOS =====================

@login_required
def ver_artefacto(request, artefacto_id):
    artefacto = get_object_or_404(Artefacto, id=artefacto_id)
    is_mermaid = artefacto.titulo in ARTEFACTOS_MERMAID
    return render(request, 'documentacion/ver_artefacto.html', {
        'artefacto': artefacto,
        'is_mermaid': is_mermaid
    })

#@login_required
#def ver_artefacto2(request, artefacto_id):
#    artefacto = get_object_or_404(Artefacto, id=artefacto_id, proyecto__propietario=request.user)
#    is_mermaid = artefacto.titulo in ARTEFACTOS_MERMAID
#    return render(request, 'documentacion/ver_artefacto2.html', {
#        'artefacto': artefacto,
#        'is_mermaid': is_mermaid
#    })

# ===================== GENERACIÓN AUTOMÁTICA =====================

@login_required
def generar_artefacto(request, proyecto_id, subartefacto_nombre):
    proyecto = get_object_or_404(Project, id=proyecto_id, propietario=request.user)
    subartefacto = get_object_or_404(SubArtefacto, fase__proyecto=proyecto, nombre=subartefacto_nombre)

    if subartefacto.nombre not in ARTEFACTOS_VALIDOS:
        return JsonResponse({"error": "Tipo de artefacto inválido."}, status=400)

    artefacto_existente = Artefacto.objects.filter(
        proyecto=proyecto,
        titulo=subartefacto.nombre
    ).first()
    if artefacto_existente:
        return redirect('ver_artefacto', artefacto_id=artefacto_existente.id)

    try:
        if subartefacto.nombre in ARTEFACTOS_TEXTO:
            contenido = generar_subartefacto_con_prompt(
                tipo=subartefacto.nombre,
                nombre_proyecto=proyecto.nombre,
                descripcion=proyecto.descripcion
            )
        else:
            contenido = generar_subartefacto_con_prompt(
                tipo=subartefacto.nombre,
                texto=proyecto.descripcion
            )
            contenido = limpiar_mermaid(contenido)
    except Exception as e:
        import traceback
        contenido = f"[ERROR IA] {str(e)}\n{traceback.format_exc()}"

    artefacto = Artefacto.objects.create(
        proyecto=proyecto,
        fase=subartefacto.fase,
        subartefacto=subartefacto,
        titulo=subartefacto.nombre,
        contenido=contenido,
        generado_por_ia=True
    )
    return redirect('ver_artefacto', artefacto_id=artefacto.id)

@login_required
def generar_subartefacto_modal(request, proyecto_id):
    subartefacto_nombre = request.GET.get("subartefacto", "")
    proyecto = get_object_or_404(Project, id=proyecto_id, propietario=request.user)

    try:
        if subartefacto_nombre in ARTEFACTOS_TEXTO:
            contenido = generar_subartefacto_con_prompt(
                tipo=subartefacto_nombre,
                nombre_proyecto=proyecto.nombre,
                descripcion=proyecto.descripcion
            )
        else:
            contenido = generar_subartefacto_con_prompt(
                tipo=subartefacto_nombre,
                texto=proyecto.descripcion
            )
            contenido = limpiar_mermaid(contenido)

        tipo = "mermaid" if subartefacto_nombre in ARTEFACTOS_MERMAID else "texto"
    except Exception as e:
        import traceback
        contenido = f"[ERROR IA] {str(e)}\n{traceback.format_exc()}"
        tipo = "error"

    return JsonResponse({
        "tipo": tipo,
        "contenido": contenido,
        "titulo": subartefacto_nombre
    })
