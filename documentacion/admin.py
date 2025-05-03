from django.contrib import admin
from .models import Project
from .models import Artefacto
from .models import EvaluacionCoherencia
# Register your models here.

admin.site.register(Project)
admin.site.register(Artefacto)
admin.site.register(EvaluacionCoherencia)