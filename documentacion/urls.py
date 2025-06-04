from django.urls import path
from . import views
from django.views.generic import TemplateView


urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),# pantilla de inicio 
    path('dashboard/', views.dashboard, name='dashboard'),# plantilla de dashboard
    path('proyecto/nuevo/', views.crear_proyecto, name='crear_proyecto'),# pantilla de crear proyecto
    path('proyecto/<int:pk>/editar/', views.editar_proyecto, name='editar_proyecto'),#editar proyecto
    path('proyecto/<int:proyecto_id>/', views.detalle_proyecto, name='detalle_proyecto'),#detalle de proyecto
    path('proyecto/<int:proyecto_id>/eliminar/', views.eliminar_proyecto, name='eliminar_proyecto'),#eliminar proyecto
    path('proyecto/<int:proyecto_id>/artefacto/nuevo/', views.crear_artefacto, name='crear_artefacto'),# crear artefacto
    path('ver_artefacto/<int:artefacto_id>/', views.ver_artefacto, name='ver_artefacto'), #visializar el artefacto
    path('artefacto/editar/<int:artefacto_id>/', views.editar_artefacto, name='editar_artefacto'),# editar artefacto
    #path('ver_artefacto2/<int:artefacto_id>/', views.ver_artefacto, name='ver_artefacto2'),  
    path('logout/', views.cerrar_sesion, name='logout'),  # Importante para cerrar sesión
    path('proyecto/<int:proyecto_id>/generar/<str:subartefacto_nombre>/', views.generar_artefacto, name='generar_artefacto'),
    path('artefacto/eliminar/<int:artefacto_id>/', views.eliminar_artefacto, name='eliminar_artefacto'),# eliminar artefacto
]