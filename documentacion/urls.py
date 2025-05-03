from django.urls import path
from . import views
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('proyecto/nuevo/', views.crear_proyecto, name='crear_proyecto'),
    path('proyectos/', views.dashboard, name='dashboard'),
    path('logout/', views.cerrar_sesion, name='logout'),  # 👈 importante
    path('proyecto/<int:proyecto_id>/', views.detalle_proyecto, name='detalle_proyecto'),
    path('proyecto/<int:proyecto_id>/artefacto/nuevo/', views.crear_artefacto, name='crear_artefacto'),
    path('artefacto/<int:artefacto_id>/', views.ver_artefacto, name='ver_artefacto'),
    path('proyecto/<int:pk>/editar/', views.editar_proyecto, name='editar_proyecto'), # este codigo se agrego para el editar

]