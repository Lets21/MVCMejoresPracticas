from django.contrib import admin
from .models import Task, Paciente, Doctor, TipoUsuario, Medicamento

admin.site.register(Task)
admin.site.register(Paciente)
admin.site.register(Doctor)
admin.site.register(TipoUsuario)
admin.site.register(Medicamento)