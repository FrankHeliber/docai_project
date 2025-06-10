from django import forms
from .models import Project, Artefacto
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

ARTEFACTOS_VALIDOS = [
    "Historia de Usuario",
    "caja negra",
    "smoke",
    "Diagrama de flujo",
    "Diagrama de clases",
    "Diagrama de Entidad-Relacion",
    "Diagrama de secuencia",
    "Diagrama de estado",
    "Diagrama de C4"
]

class ProjectForm(forms.ModelForm):
    """
    Formulario para crear o editar un proyecto.
    """
    nombre = forms.CharField(
        label='Nombre del Proyecto',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el nombre del proyecto'
        })
    )

    descripcion = forms.CharField(
        label='Descripción',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Ingrese una breve descripción del proyecto'
        })
    )

    class Meta:
        model = Project
        fields = ['nombre', 'descripcion']


class ArtefactoForm(forms.ModelForm):
    """
    Formulario para crear o editar un artefacto.
    """
    tipo = forms.ChoiceField(
        label='Tipo de Artefacto',
        choices=Artefacto.TIPO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    titulo = forms.CharField(
        label='Título del Artefacto',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese un título representativo'
        })
    )

    contenido = forms.CharField(
        label='Contenido',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Contenido generado o ingresado manualmente'
        })
    )

    class Meta:
        model = Artefacto
        fields = ['titulo', 'tipo', 'contenido']
 

class CustomUserCreationForm(UserCreationForm):
    """
    Formulario personalizado de registro de usuario con campo de email obligatorio.
    """
    email = forms.EmailField(
        required=True,
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )

    username = forms.CharField(
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese un nombre de usuario'
        })
    )

    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña'
        })
    )

    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme su contraseña'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
