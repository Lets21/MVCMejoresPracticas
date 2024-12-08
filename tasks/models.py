from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, time
from django.utils import timezone

# Create your models here.

class Paciente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    edad = models.IntegerField()
    condiciones_medicas = models.TextField()
    alergias = models.TextField()

    def __str__(self):
        return self.usuario.username

class Doctor(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    especialidad = models.CharField(max_length=100)

    def __str__(self):
        return f"Dr. {self.usuario.username} - {self.especialidad}"

class TipoUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    TIPOS = (
        ('admin', 'Administrador'),
        ('doctor', 'Doctor'),
        ('paciente', 'Paciente'),
    )
    tipo = models.CharField(max_length=20, choices=TIPOS)

    def __str__(self):
        return f"{self.usuario.username} - {self.tipo}"

class Task(models.Model):
  title = models.CharField(max_length=200)
  description = models.TextField(max_length=1000)
  created = models.DateTimeField(auto_now_add=True)
  datecompleted = models.DateTimeField(null=True, blank=True)
  important = models.BooleanField(default=False)
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  def __str__(self):
    return self.title + ' - ' + self.user.username

class Tratamiento(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    duracion = models.CharField(max_length=100)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    especialidad_requerida = models.CharField(max_length=100, default='General')
    condiciones_tratadas = models.TextField(help_text="Lista de condiciones separadas por comas", default='general')
    edad_minima = models.IntegerField(default=0)
    edad_maxima = models.IntegerField(default=120)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_condiciones_list(self):
        return [c.strip().lower() for c in self.condiciones_tratadas.split(',')]
    
    def es_adecuado_para_edad(self, edad):
        return self.edad_minima <= edad <= self.edad_maxima
    
    def get_medicamentos(self):
        return self.tratamientomedicamento_set.select_related('medicamento').all()
    
    def __str__(self):
        return self.nombre

class AsignacionTratamiento(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.CASCADE, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado')
    ], default='pendiente')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    requiere_crear_tratamiento = models.BooleanField(default=False)

    def get_medicamentos(self):
        return AsignacionTratamientoMedicamento.objects.filter(
            asignacion_tratamiento=self
        ).select_related(
            'medicamento',
            'medicamento_original'
        )

    def asignar_medicamentos(self):
        # Eliminar asignaciones previas
        AsignacionTratamientoMedicamento.objects.filter(asignacion_tratamiento=self).delete()
        
        # Obtener las alergias del paciente
        alergias_paciente = set(map(str.strip, self.paciente.alergias.lower().split(',')))
        
        for med_tratamiento in self.tratamiento.tratamientomedicamento_set.all():
            medicamento = med_tratamiento.medicamento
            contraindicaciones = set(map(str.strip, medicamento.contraindicaciones.lower().split(',')))
            
            # Verificar si hay conflicto con alergias
            if alergias_paciente.intersection(contraindicaciones):
                # Buscar sustituto
                sustituto = MedicamentoSustituto.objects.filter(
                    medicamento_original=medicamento
                ).first()
                
                if sustituto:
                    # Crear asignación con medicamento sustituto
                    AsignacionTratamientoMedicamento.objects.create(
                        asignacion_tratamiento=self,
                        medicamento=sustituto.medicamento_sustituto,
                        medicamento_original=medicamento,
                        dosis=med_tratamiento.dosis,
                        frecuencia=med_tratamiento.frecuencia,
                        es_sustituto=True
                    )
                    continue  # Pasar al siguiente medicamento
            
            # Si no hay alergia o no hay sustituto, asignar el medicamento original
            AsignacionTratamientoMedicamento.objects.create(
                asignacion_tratamiento=self,
                medicamento=medicamento,
                dosis=med_tratamiento.dosis,
                frecuencia=med_tratamiento.frecuencia,
                es_sustituto=False
            )

    def __str__(self):
        return f"{self.paciente} - {self.tratamiento}"

class Medicamento(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    componente_principal = models.CharField(max_length=200)
    contraindicaciones = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def asegurar_sustituto(self):
        # Verificar si ya tiene sustituto
        sustituto_existente = MedicamentoSustituto.objects.filter(
            medicamento_original=self
        ).exists()
        
        if not sustituto_existente:
            # Buscar un medicamento alternativo de características similares
            medicamento_alternativo = Medicamento.objects.exclude(
                id=self.id
            ).filter(
                nombre__icontains=self.nombre[:4]  # Buscar medicamentos similares
            ).first()
            
            if medicamento_alternativo:
                MedicamentoSustituto.objects.create(
                    medicamento_original=self,
                    medicamento_sustituto=medicamento_alternativo,
                    motivo_sustitucion=f"Sustituto automático para {self.nombre}"
                )
                return True
        return False

    def save(self, *args, **kwargs):
        es_nuevo = self._state.adding
        super().save(*args, **kwargs)
        if es_nuevo:
            self.asegurar_sustituto()

    def __str__(self):
        return self.nombre

class MedicamentoSustituto(models.Model):
    medicamento_original = models.ForeignKey(Medicamento, on_delete=models.CASCADE, related_name='sustitutos')
    medicamento_sustituto = models.ForeignKey(Medicamento, on_delete=models.CASCADE, related_name='original')
    motivo_sustitucion = models.TextField()
    
    def __str__(self):
        return f"{self.medicamento_original} -> {self.medicamento_sustituto}"

class TratamientoMedicamento(models.Model):
    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.CASCADE)
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    dosis = models.CharField(max_length=100, default='')
    frecuencia = models.CharField(max_length=100, default='')
    
    def __str__(self):
        return f"{self.tratamiento} - {self.medicamento}"

class AsignacionTratamientoMedicamento(models.Model):
    asignacion_tratamiento = models.ForeignKey(AsignacionTratamiento, on_delete=models.CASCADE)
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    medicamento_original = models.ForeignKey(Medicamento, null=True, blank=True, 
                                        on_delete=models.SET_NULL, 
                                        related_name='sustituciones')
    dosis = models.CharField(max_length=50)
    frecuencia = models.CharField(max_length=50)
    es_sustituto = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.medicamento.nombre} - {self.dosis}"

class Cita(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.TextField()
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('confirmada', 'Confirmada'),
            ('completada', 'Completada'),
            ('cancelada', 'Cancelada')
        ],
        default='pendiente'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        
        fecha_hora_cita = timezone.make_aware(
            datetime.combine(self.fecha, self.hora),
            timezone.get_current_timezone()
        )

        # Verificar que la fecha no sea en el pasado
        if fecha_hora_cita < timezone.now():
            raise ValidationError('No se pueden programar citas en fechas pasadas.')

        # Verificar disponibilidad del doctor
        citas_existentes = Cita.objects.filter(
            doctor=self.doctor,
            fecha=self.fecha,
            estado__in=['pendiente', 'confirmada']
        )
        if self.pk:
            citas_existentes = citas_existentes.exclude(pk=self.pk)

        for cita_existente in citas_existentes:
            diferencia = abs((fecha_hora_cita - timezone.make_aware(
                datetime.combine(cita_existente.fecha, cita_existente.hora),
                timezone.get_current_timezone()
            )).seconds) / 3600
            if diferencia < 1:
                raise ValidationError('El doctor ya tiene una cita programada cerca de este horario.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

def home(request):
    if request.user.is_authenticated:
        try:
            tipo_usuario = TipoUsuario.objects.get(usuario=request.user)
            if tipo_usuario.tipo == 'admin':
                return redirect('vista_admin')
            elif tipo_usuario.tipo == 'doctor':
                return redirect('vista_doctor')
            elif tipo_usuario.tipo == 'paciente':
                return redirect('vista_paciente')
            else:
                messages.error(request, 'Tipo de usuario desconocido.')
                return redirect('login')
        except ObjectDoesNotExist:
            messages.error(request, 'No se ha asignado un tipo de usuario a tu cuenta. Contacta con el administrador.')
            return redirect('logout')  # Redirige para cerrar sesión
    return redirect('login')
