from django.urls import path
from . import views
from django.views.generic import TemplateView


urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('proyecto/nuevo/', views.crear_proyecto, name='crear_proyecto'),
    path('proyecto/<int:proyecto_id>/', views.detalle_proyecto, name='detalle_proyecto'),
    path('proyecto/<int:proyecto_id>/artefacto/nuevo/', views.crear_artefacto, name='crear_artefacto'),
    path('artefacto/<int:artefacto_id>/', views.ver_artefacto, name='ver_artefacto'),
    path('proyecto/<int:pk>/editar/', views.editar_proyecto, name='editar_proyecto'),
    path('proyecto/<int:proyecto_id>/eliminar/', views.eliminar_proyecto, name='eliminar_proyecto'),
    path('logout/', views.cerrar_sesion, name='logout'),  # Importante para cerrar sesión
    #path('proyecto/<int:proyecto_id>/generar_subartefacto_modal/', views.generar_modal_subartefacto, name='generar_subartefacto_modal'),
    path('proyecto/<int:proyecto_id>/generar/<str:subartefacto_nombre>/', views.generar_artefacto, name='generar_artefacto'),
    path('artefacto/editar/<int:artefacto_id>/', views.editar_artefacto, name='editar_artefacto'),
]
