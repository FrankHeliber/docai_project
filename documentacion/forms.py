from django import forms
from .models import Project, Artefacto
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['nombre', 'descripcion']

class ArtefactoForm(forms.ModelForm):
    class Meta:
        model = Artefacto
        fields = ['tipo', 'titulo', 'contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={'rows': 6})
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo electrónico")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']