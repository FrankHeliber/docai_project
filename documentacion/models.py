from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    propietario = models.ForeignKey(User, on_delete=models.CASCADE)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Artefacto(models.Model):
    TIPOS = [
        ('REQ', 'Requisitos'),
        ('CU', 'Casos de Uso'),
        ('PROT', 'Prototipos'),
        ('PLAN', 'Plan de Proyecto'),
        ('DOC', 'Documentación Técnica'),
        ('REP', 'Reporte de Progreso'),
        ('MAN', 'Manual de Usuario'),
        ('MANT', 'Documentación de Mantenimiento'),
    ]

    proyecto = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="artefactos")
    tipo = models.CharField(max_length=10, choices=TIPOS)
    titulo = models.CharField(max_length=100)
    contenido = models.TextField()
    generado_por_ia = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} ({self.get_tipo_display()})"

class EvaluacionCoherencia(models.Model):
    artefacto = models.ForeignKey(Artefacto, on_delete=models.CASCADE, related_name="evaluaciones")
    puntuacion_bleu = models.FloatField(null=True, blank=True)
    puntuacion_rouge = models.FloatField(null=True, blank=True)
    puntuacion_manual = models.IntegerField(null=True, blank=True)  # Escala Likert
    comentarios = models.TextField(blank=True)
    evaluado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluación de {self.artefacto.titulo}"