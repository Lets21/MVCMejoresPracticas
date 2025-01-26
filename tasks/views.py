from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Task, Paciente, Doctor, TipoUsuario, Tratamiento, AsignacionTratamiento, TratamientoMedicamento, MedicamentoSustituto, AsignacionTratamientoMedicamento, Medicamento, Cita, AsignadorConSustitutos, AsignadorOriginal
from django.db.models import Q
from django.contrib import messages
from .decorators import tipo_usuario_requerido
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from django.db.models import Count
from django.db.models import Q, F, Value
from django.db.models.functions import Lower
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

from .forms import TaskForm, PacienteRegistroForm, DoctorRegistroForm, TratamientoForm, MedicamentoForm, CitaForm, SignUpForm, TipoUsuarioForm

# Create your views here.


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        tipo_form = TipoUsuarioForm(request.POST)
        
        if form.is_valid() and tipo_form.is_valid():
            user = form.save()
            tipo = tipo_form.save(commit=False)
            tipo.usuario = user
            tipo.save()
            
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            
            messages.success(request, '¡Cuenta creada exitosamente!')
            return redirect('home')
    else:
        form = SignUpForm()
        tipo_form = TipoUsuarioForm()
    
    return render(request, 'registration/signup.html', {
        'form': form,
        'tipo_form': tipo_form
    })


@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'tasks/tasks.html', {
        'tasks': tasks,
        'title': 'Tareas Pendientes'
    })

@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(
        user=request.user, 
        datecompleted__isnull=False
    ).order_by('-datecompleted')
    
    return render(request, 'tasks/tasks.html', {
        'tasks': tasks,
        'title': 'Tareas Completadas'
    })


@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('tasks')
    else:
        form = TaskForm()
    return render(request, 'tasks/create_task.html', {
        'form': form,
        'title': 'Crear Tarea'
    })


def home(request):
    if request.user.is_authenticated:
        try:
            tipo_usuario = TipoUsuario.objects.get(usuario=request.user)
            tipo = tipo_usuario.tipo.lower()
            
            if tipo == 'admin':
                return redirect('vista_admin')
            elif tipo == 'doctor':
                return redirect('vista_doctor')
            elif tipo == 'paciente':
                return redirect('vista_paciente')
            else:
                messages.error(request, 'Tipo de usuario no reconocido.')
                return redirect('logout')
        except TipoUsuario.DoesNotExist:
            messages.error(request, 'No se ha asignado un tipo de usuario a tu cuenta.')
            return redirect('logout')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('login')
    return render(request, 'home.html')


@login_required
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        form = AuthenticationForm()
        return render(request, 'signin.html', {"form": form})
    else:
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Verificar si es el super administrador
            if username == 'super_administrador' and password == 'admin123':
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    user = User.objects.create_superuser(
                        username=username,
                        password=password
                    )
                    TipoUsuario.objects.create(usuario=user, tipo='admin')
                login(request, user)
                return redirect('vista_admin')
            
            # Autenticar al usuario
            user = form.get_user()
            tipo_usuario = TipoUsuario.objects.get(usuario=user)
            login(request, user)
            
            if tipo_usuario.tipo == 'paciente':
                return redirect('vista_paciente')
            elif tipo_usuario.tipo == 'doctor':
                return redirect('vista_doctor')
            else:
                return redirect('home')
        else:
            # Si el formulario no es válido, renderizar con errores
            messages.error(request, "Usuario o contraseña incorrectos.")
            return render(request, 'signin.html', {"form": form})

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('tasks')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_detail.html', {
        'task': task,
        'form': form,
        'title': task.title
    })

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

def registro_paciente(request):
    if request.method == 'POST':
        form = PacienteRegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            Paciente.objects.create(
                usuario=user,
                edad=form.cleaned_data['edad'],
                condiciones_medicas=form.cleaned_data['condiciones_medicas'],
                alergias=form.cleaned_data['alergias']
            )
            TipoUsuario.objects.create(usuario=user, tipo='paciente')
            login(request, user)
            return redirect('home')
    else:
        form = PacienteRegistroForm()
    return render(request, 'registro_paciente.html', {'form': form})

def registro_doctor(request):
    if request.method == 'POST':
        form = DoctorRegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            Doctor.objects.create(
                usuario=user,
                especialidad=form.cleaned_data['especialidad']
            )
            TipoUsuario.objects.create(usuario=user, tipo='doctor')
            login(request, user)
            return redirect('home')
    else:
        form = DoctorRegistroForm()
    return render(request, 'registro_doctor.html', {'form': form})

# Vista solo para doctores
@tipo_usuario_requerido(['doctor'])
def vista_doctor(request):
    doctor = request.user.doctor
    todas_asignaciones = AsignacionTratamiento.objects.filter(doctor=doctor).select_related(
        'paciente__usuario',
        'tratamiento'
    ).prefetch_related(
        'asignaciontratamientomedicamento_set__medicamento',
        'asignaciontratamientomedicamento_set__medicamento_original'
    )
    
    # Separar las asignaciones
    asignaciones_pendientes = todas_asignaciones.filter(requiere_crear_tratamiento=True)
    asignaciones_normales = todas_asignaciones.filter(requiere_crear_tratamiento=False)
    
    # Obtener las citas del doctor
    citas = Cita.objects.filter(doctor=doctor).select_related('paciente__usuario')
    
    return render(request, 'vista_doctor.html', {
        'asignaciones_pendientes': asignaciones_pendientes,
        'asignaciones_normales': asignaciones_normales,
        'citas': citas
    })

# Vista solo para pacientes
@login_required
@tipo_usuario_requerido(['paciente'])
def vista_paciente(request):
    paciente = request.user.paciente
    asignaciones = AsignacionTratamiento.objects.filter(
        paciente=paciente
    ).select_related(
        'doctor__usuario',
        'tratamiento'
    ).prefetch_related(
        'asignaciontratamientomedicamento_set__medicamento',
        'asignaciontratamientomedicamento_set__medicamento_original'
    )
    
    # Verificar si hay asignaciones activas
    asignaciones_activas = asignaciones.filter(
        estado__in=['pendiente', 'en_progreso']
    ).exists()
    
    citas = Cita.objects.filter(paciente=paciente)
    
    return render(request, 'vista_paciente.html', {
        'asignaciones': asignaciones,
        'asignaciones_activas': asignaciones_activas,
        'citas': citas
    })

# Vista solo para administradores
@tipo_usuario_requerido(['admin'])
def vista_admin(request):
    pacientes = Paciente.objects.all()
    doctores = Doctor.objects.all()
    tipos_usuario = TipoUsuario.objects.all()
    
    context = {
        'pacientes': pacientes,
        'doctores': doctores,
        'tipos_usuario': tipos_usuario
    }
    return render(request, 'vista_admin.html', context)

# Vista que pueden ver tanto doctores como administradores
@tipo_usuario_requerido(['doctor', 'admin'])
def vista_doctor_admin(request):
    # Lógica compartida
    return render(request, 'vista_doctor_admin.html')

@tipo_usuario_requerido(['admin'])
def editar_paciente(request, id):
    paciente = get_object_or_404(Paciente, id=id)
    
    if request.method == 'POST':
        form = PacienteRegistroForm(request.POST, instance=paciente.usuario)
        if form.is_valid():
            user = form.save()
            paciente.edad = form.cleaned_data['edad']
            paciente.condiciones_medicas = form.cleaned_data['condiciones_medicas']
            paciente.alergias = form.cleaned_data['alergias']
            paciente.save()
            return redirect('vista_admin')
    else:
        initial_data = {
            'username': paciente.usuario.username,
            'edad': paciente.edad,
            'condiciones_medicas': paciente.condiciones_medicas,
            'alergias': paciente.alergias
        }
        form = PacienteRegistroForm(initial=initial_data)
    
    return render(request, 'editar_paciente.html', {
        'form': form,
        'paciente': paciente
    })

@tipo_usuario_requerido(['admin'])
def eliminar_paciente(request, id):
    paciente = get_object_or_404(Paciente, id=id)
    if request.method == 'POST':
        usuario = paciente.usuario
        paciente.delete()
        usuario.delete()
        return redirect('vista_admin')
    return render(request, 'confirmar_eliminar.html', {
        'objeto': paciente,
        'tipo': 'paciente'
    })

@tipo_usuario_requerido(['admin'])
def editar_doctor(request, id):
    doctor = get_object_or_404(Doctor, id=id)
    
    if request.method == 'POST':
        form = DoctorRegistroForm(request.POST, instance=doctor.usuario)
        if form.is_valid():
            user = form.save()
            doctor.especialidad = form.cleaned_data['especialidad']
            doctor.save()
            return redirect('vista_admin')
    else:
        initial_data = {
            'username': doctor.usuario.username,
            'especialidad': doctor.especialidad
        }
        form = DoctorRegistroForm(initial=initial_data)
    
    return render(request, 'editar_doctor.html', {
        'form': form,
        'doctor': doctor
    })

@tipo_usuario_requerido(['admin'])
def eliminar_doctor(request, id):
    doctor = get_object_or_404(Doctor, id=id)
    if request.method == 'POST':
        usuario = doctor.usuario
        doctor.delete()
        usuario.delete()
        return redirect('vista_admin')
    return render(request, 'confirmar_eliminar.html', {
        'objeto': doctor,
        'tipo': 'doctor'
    })

@tipo_usuario_requerido(['admin'])
def crear_paciente(request):
    # Lista predefinida de condiciones médicas y alergias comunes
    condiciones_medicas = [
        'Hipertensión', 'Diabetes', 'Asma', 'Artritis',
        'Migraña', 'Epilepsia', 'Depresión', 'Ansiedad',
        'Gastritis', 'Úlcera', 'Dermatitis', 'Psoriasis',
        'Rinitis', 'Sinusitis', 'Bronquitis', 'Fibromialgia'
    ]
    
    alergias_comunes = [
        'Penicilina', 'Sulfatos', 'Aspirina', 'Látex',
        'Polen', 'Ácaros', 'Mariscos', 'Nueces',
        'Huevo', 'Leche', 'Soya', 'Trigo',
        'Ibuprofeno', 'Paracetamol', 'Amoxicilina'
    ]

    if request.method == 'POST':
        form = PacienteRegistroForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                Paciente.objects.create(
                    usuario=user,
                    edad=form.cleaned_data['edad'],
                    condiciones_medicas=form.cleaned_data['condiciones_medicas'],
                    alergias=form.cleaned_data['alergias']
                )
                TipoUsuario.objects.create(usuario=user, tipo='paciente')
                return redirect('vista_admin')
            except Exception as e:
                print(f"Error al crear paciente: {e}")
                user.delete()
                form.add_error(None, "Error al crear el paciente. Por favor, intente nuevamente.")
    else:
        form = PacienteRegistroForm()
    
    return render(request, 'crear_paciente.html', {
        'form': form,
        'error': form.errors,
        'condiciones_medicas': condiciones_medicas,
        'alergias_comunes': alergias_comunes
    })

@tipo_usuario_requerido(['admin'])
def crear_doctor(request):
    # Lista predefinida de especialidades médicas
    especialidades = [
        'Medicina General',
        'Cardiología',
        'Neurología',
        'Pediatría',
        'Ginecología',
        'Dermatología',
        'Oftalmología',
        'Otorrinolaringología',
        'Psiquiatría',
        'Endocrinología',
        'Gastroenterología',
        'Neumología',
        'Reumatología',
        'Urología',
        'Traumatología',
        'Oncología',
        'Hematología',
        'Nefrología',
        'Infectología',
        'Geriatría'
    ]

    if request.method == 'POST':
        form = DoctorRegistroForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                Doctor.objects.create(
                    usuario=user,
                    especialidad=form.cleaned_data['especialidad']
                )
                TipoUsuario.objects.create(usuario=user, tipo='doctor')
                return redirect('vista_admin')
            except Exception as e:
                print(f"Error al crear doctor: {e}")
                user.delete()
                form.add_error(None, "Error al crear el doctor. Por favor, intente nuevamente.")
    else:
        form = DoctorRegistroForm()
    
    return render(request, 'crear_doctor.html', {
        'form': form,
        'error': form.errors,
        'especialidades': especialidades
    })

@login_required
@tipo_usuario_requerido(['admin'])
def lista_tratamientos(request):
    tratamientos = Tratamiento.objects.prefetch_related(
        'tratamientomedicamento_set',
        'tratamientomedicamento_set__medicamento'
    ).all()
    return render(request, 'tratamientos/lista_tratamientos.html', {
        'tratamientos': tratamientos
    })

@tipo_usuario_requerido(['admin'])
def crear_tratamiento(request):
    # Listas predefinidas
    especialidades = [
        'Medicina General',
        'Cardiología',
        'Neurología',
        'Pediatría',
        'Ginecología',
        'Dermatología',
        'Oftalmología',
        'Otorrinolaringología',
        'Psiquiatría',
        'Endocrinología',
        'Gastroenterología',
        'Neumología',
        'Reumatología',
        'Urología',
        'Traumatología',
        'Oncología'
    ]
    
    condiciones_tratables = [
        'Hipertensión', 'Diabetes', 'Asma', 'Artritis',
        'Migraña', 'Epilepsia', 'Depresión', 'Ansiedad',
        'Gastritis', 'Úlcera', 'Dermatitis', 'Psoriasis',
        'Rinitis', 'Sinusitis', 'Bronquitis', 'Fibromialgia',
        'Obesidad', 'Osteoporosis', 'Arritmia', 'Colesterol alto'
    ]

    if request.method == 'POST':
        form = TratamientoForm(request.POST)
        if form.is_valid():
            tratamiento = form.save()
            
            # Procesar medicamentos seleccionados
            medicamentos_seleccionados = request.POST.getlist('medicamentos')
            for med_id in medicamentos_seleccionados:
                medicamento = Medicamento.objects.get(id=med_id)
                dosis = request.POST.get(f'dosis_{med_id}')
                frecuencia = request.POST.get(f'frecuencia_{med_id}')
                
                TratamientoMedicamento.objects.create(
                    tratamiento=tratamiento,
                    medicamento=medicamento,
                    dosis=dosis,
                    frecuencia=frecuencia
                )
            
            return redirect('lista_tratamientos')
    else:
        form = TratamientoForm()

    return render(request, 'tratamientos/crear_tratamiento.html', {
        'form': form,
        'especialidades': especialidades,
        'condiciones_tratables': condiciones_tratables,
        'medicamentos': Medicamento.objects.all()
    })

@tipo_usuario_requerido(['admin'])
def eliminar_tratamiento(request, id):
    tratamiento = get_object_or_404(Tratamiento, id=id)
    if request.method == 'POST':
        tratamiento.delete()
        return redirect('lista_tratamientos')
    return render(request, 'confirmar_eliminar.html', {
        'objeto': tratamiento,
        'tipo': 'tratamiento'
    })

def determinar_especialidad(condiciones):
    # Mapeo expandido de condiciones a especialidades
    especialidades = {
        'diabetes': 'Endocrinología',
        'hipertension': 'Cardiología',
        'asma': 'Neumología',
        'artritis': 'Reumatología',
        'migraña': 'Neurología',
        'epilepsia': 'Neurología',
        'depresion': 'Psiquiatría',
        'ansiedad': 'Psiquiatría',
        'gastritis': 'Gastroenterología',
        'ulcera': 'Gastroenterología',
        'dermatitis': 'Dermatología',
        'psoriasis': 'Dermatología'
    }
    
    for condicion in condiciones:
        for keyword, especialidad in especialidades.items():
            if keyword in condicion.lower():
                return especialidad
    
    return 'Medicina General'  # Especialidad por defecto si no hay coincidencias

def encontrar_tratamiento_compatible(paciente):
    condiciones_paciente = [c.strip().lower() for c in paciente.condiciones_medicas.split(',')]
    
    # Buscar tratamientos que coincidan con las condiciones y edad del paciente
    tratamientos = Tratamiento.objects.all()
    
    for tratamiento in tratamientos:
        if (tratamiento.es_adecuado_para_edad(paciente.edad) and
            any(condicion in tratamiento.get_condiciones_list() for condicion in condiciones_paciente)):
            return tratamiento
    
    return None

def asignar_medicamentos(asignacion, paciente):
    if not asignacion.tratamiento:
        return
        
    alergias_paciente = [a.strip().lower() for a in paciente.alergias.split(',')]
    medicamentos_tratamiento = TratamientoMedicamento.objects.filter(
        tratamiento=asignacion.tratamiento
    ).select_related('medicamento')
    
    # Primero eliminamos cualquier asignación previa
    AsignacionTratamientoMedicamento.objects.filter(asignacion_tratamiento=asignacion).delete()
    
    for med_tratamiento in medicamentos_tratamiento:
        medicamento = med_tratamiento.medicamento
        es_alergico = any(alergia in medicamento.contraindicaciones.lower() for alergia in alergias_paciente)
        
        if es_alergico:
            # Buscar sustituto
            try:
                sustituto = MedicamentoSustituto.objects.get(medicamento_original=medicamento)
                AsignacionTratamientoMedicamento.objects.create(
                    asignacion_tratamiento=asignacion,
                    medicamento=sustituto.medicamento_sustituto,
                    es_sustituto=True,
                    medicamento_original=medicamento,
                    dosis=med_tratamiento.dosis,
                    frecuencia=med_tratamiento.frecuencia
                )
            except MedicamentoSustituto.DoesNotExist:
                continue
        else:
            AsignacionTratamientoMedicamento.objects.create(
                asignacion_tratamiento=asignacion,
                medicamento=medicamento,
                dosis=med_tratamiento.dosis,
                frecuencia=med_tratamiento.frecuencia
            )

def determinar_especialidad_y_tratamiento(paciente):
    # Convertir condiciones del paciente a lista y normalizar
    condiciones_paciente = [c.strip().lower() for c in paciente.condiciones_medicas.split(',')]
    
    # Buscar tratamientos que coincidan con las condiciones del paciente
    tratamientos_disponibles = Tratamiento.objects.all()
    
    for tratamiento in tratamientos_disponibles:
        # Normalizar condiciones tratadas
        condiciones_tratamiento = [c.strip().lower() for c in tratamiento.condiciones_tratadas.split(',')]
        
        # Verificar si hay coincidencia en condiciones y edad
        if (any(c in condiciones_tratamiento for c in condiciones_paciente) and
            paciente.edad >= tratamiento.edad_minima and
            paciente.edad <= tratamiento.edad_maxima):
            
            # Buscar doctor disponible para este tratamiento
            doctor = Doctor.objects.filter(
                especialidad=tratamiento.especialidad_requerida
            ).first()
            
            if doctor:
                return doctor, tratamiento
    
    # Si no se encuentra tratamiento específico, buscar doctor por especialidad
    especialidad = determinar_especialidad(condiciones_paciente)
    doctor = Doctor.objects.filter(especialidad=especialidad).first()
    
    return doctor, None

@login_required
@tipo_usuario_requerido(['paciente'])
def asignar_tratamiento_automatico(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Verificar si ya tiene un tratamiento activo
    if AsignacionTratamiento.objects.filter(
        paciente=paciente,
        estado__in=['pendiente', 'en_progreso']
    ).exists():
        messages.error(request, "Ya tienes un tratamiento activo.")
        return redirect('vista_paciente')
    
    doctor, tratamiento = determinar_especialidad_y_tratamiento(paciente)
    
    if not doctor:
        messages.error(request, "No hay doctores disponibles en el sistema.")
        return redirect('vista_paciente')
    
    # Crear la asignación
    asignacion = AsignacionTratamiento.objects.create(
        paciente=paciente,
        doctor=doctor,
        tratamiento=tratamiento,
        requiere_crear_tratamiento=(tratamiento is None),
        estado='pendiente'
    )
    
    if tratamiento:
        # Elegir estrategia de asignación
        if paciente.alergias:
            estrategia = AsignadorConSustitutos()
        else:
            estrategia = AsignadorOriginal()
        
        # Asignar medicamentos considerando alergias
        asignacion.asignar_medicamentos(estrategia)
        messages.success(request, f"Se te ha asignado el tratamiento '{tratamiento.nombre}' con el Dr. {doctor.usuario.get_full_name()}")
    else:
        messages.success(request, f"Se ha asignado tu caso al Dr. {doctor.usuario.get_full_name()}. El doctor creará un tratamiento personalizado para ti.")
    
    return redirect('vista_paciente')

@require_POST
@tipo_usuario_requerido(['doctor'])
def actualizar_estado_tratamiento(request, asignacion_id):
    try:
        # Verificar que el tratamiento pertenezca al doctor actual
        asignacion = AsignacionTratamiento.objects.get(
            id=asignacion_id, 
            doctor=request.user.doctor
        )
        
        data = json.loads(request.body)
        nuevo_estado = data.get('estado')
        
        if nuevo_estado in ['pendiente', 'en_progreso', 'completado']:
            asignacion.estado = nuevo_estado
            asignacion.save()
            
            return JsonResponse({
                'success': True,
                'mensaje': f'Estado actualizado a {nuevo_estado}'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Estado no válido'
            })
            
    except AsignacionTratamiento.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Tratamiento no encontrado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@tipo_usuario_requerido(['admin'])
def lista_medicamentos(request):
    medicamentos = Medicamento.objects.all()
    return render(request, 'medicamentos/lista_medicamentos.html', {'medicamentos': medicamentos})

@login_required
@tipo_usuario_requerido(['admin'])
def crear_medicamento(request):
    contraindicaciones_comunes = [
        'Penicilina', 'Sulfatos', 'Aspirina', 'Látex',
        'Polen', 'Ácaros', 'Mariscos', 'Nueces',
        'Huevo', 'Leche', 'Soya', 'Trigo',
        'Ibuprofeno', 'Paracetamol', 'Amoxicilina',
        'IECA', 'Embarazo', 'Insuficiencia cardíaca',
        'Glaucoma', 'Enfermedad hepática', 'Inmunosupresión',
        'Insuficiencia renal', 'Pancreatitis'
    ]

    if request.method == 'POST':
        form = MedicamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicamento creado exitosamente.', extra_tags='admin_medicamento')
            return redirect('lista_medicamentos')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = MedicamentoForm()

    return render(request, 'medicamentos/form_medicamento.html', {
        'form': form,
        'medicamento': None,
        'contraindicaciones_comunes': contraindicaciones_comunes
    })

@login_required
@tipo_usuario_requerido(['admin'])
def editar_medicamento(request, medicamento_id):
    medicamento = get_object_or_404(Medicamento, id=medicamento_id)
    contraindicaciones_comunes = [
        'Penicilina', 'Sulfatos', 'Aspirina', 'Látex',
        'Polen', 'Ácaros', 'Mariscos', 'Nueces',
        'Huevo', 'Leche', 'Soya', 'Trigo',
        'Ibuprofeno', 'Paracetamol', 'Amoxicilina',
        'IECA', 'Embarazo', 'Insuficiencia cardíaca',
        'Glaucoma', 'Enfermedad hepática', 'Inmunosupresión',
        'Insuficiencia renal', 'Pancreatitis'
    ]

    if request.method == 'POST':
        form = MedicamentoForm(request.POST, instance=medicamento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicamento actualizado exitosamente.')
            return redirect('lista_medicamentos')
    else:
        form = MedicamentoForm(instance=medicamento)

    return render(request, 'medicamentos/form_medicamento.html', {
        'form': form,
        'medicamento': medicamento,
        'contraindicaciones_comunes': contraindicaciones_comunes
    })

@login_required
@tipo_usuario_requerido(['admin'])
def eliminar_medicamento(request, id):
    medicamento = get_object_or_404(Medicamento, id=id)
    if request.method == 'POST':
        medicamento.delete()
        messages.success(request, 'Medicamento eliminado exitosamente.', extra_tags='admin_medicamento')
        return redirect('lista_medicamentos')
    return render(request, 'confirmar_eliminar.html', {'objeto': medicamento, 'tipo': 'medicamento'})

@tipo_usuario_requerido(['doctor'])
def crear_tratamiento_paciente(request, asignacion_id):
    asignacion = get_object_or_404(
        AsignacionTratamiento, 
        id=asignacion_id,
        doctor=request.user.doctor
    )
    
    condiciones_tratables = [
        'Hipertensión', 'Diabetes', 'Asma', 'Artritis',
        'Migraña', 'Epilepsia', 'Depresión', 'Ansiedad',
        'Gastritis', 'Úlcera', 'Dermatitis', 'Psoriasis',
        'Rinitis', 'Sinusitis', 'Bronquitis', 'Fibromialgia',
        'Obesidad', 'Osteoporosis', 'Arritmia', 'Colesterol alto'
    ]
    
    if request.method == 'POST':
        form = TratamientoForm(request.POST)
        if form.is_valid():
            tratamiento = form.save()
            
            # Procesar medicamentos seleccionados
            medicamentos_seleccionados = request.POST.getlist('medicamentos')
            for med_id in medicamentos_seleccionados:
                medicamento = Medicamento.objects.get(id=med_id)
                dosis = request.POST.get(f'dosis_{med_id}')
                frecuencia = request.POST.get(f'frecuencia_{med_id}')
                
                TratamientoMedicamento.objects.create(
                    tratamiento=tratamiento,
                    medicamento=medicamento,
                    dosis=dosis,
                    frecuencia=frecuencia
                )
            
            # Actualizar la asignación y asignar medicamentos
            asignacion.tratamiento = tratamiento
            asignacion.requiere_crear_tratamiento = False
            asignacion.save()
            
            print(f"Asignando medicamentos para paciente: {asignacion.paciente}")  # Debug
            print(f"Alergias del paciente: {asignacion.paciente.alergias}")  # Debug
            
            # Elegir estrategia de asignación
            if asignacion.paciente.alergias:
                estrategia = AsignadorConSustitutos()
            else:
                estrategia = AsignadorOriginal()
            
            asignacion.asignar_medicamentos(estrategia)
            
            # Verificar que se crearon las asignaciones
            medicamentos_asignados = asignacion.get_medicamentos()
            print(f"Medicamentos asignados: {list(medicamentos_asignados)}")  # Debug
            
            messages.success(request, 'Tratamiento creado exitosamente')
            return redirect('vista_doctor')
    else:
        initial_data = {
            'condiciones_tratadas': asignacion.paciente.condiciones_medicas
        }
        form = TratamientoForm(initial=initial_data)
    return render(request, 'tratamientos/crear_tratamiento.html', {
        'form': form,
        'medicamentos': Medicamento.objects.all(),
        'paciente': asignacion.paciente,
        'asignacion': asignacion,
        'condiciones_tratables': condiciones_tratables 
    })

@require_POST
@tipo_usuario_requerido(['doctor'])
def actualizar_estado_cita(request, cita_id):
    try:
        cita = Cita.objects.get(id=cita_id, doctor=request.user.doctor)
        data = json.loads(request.body)
        nuevo_estado = data.get('estado')
        
        if nuevo_estado in ['pendiente', 'confirmada', 'completada', 'cancelada']:
            cita.estado = nuevo_estado
            cita.save()
            
            return JsonResponse({
                'success': True,
                'mensaje': f'Estado de la cita actualizado a {nuevo_estado}'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Estado no válido'
            })
            
    except Cita.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Cita no encontrada'
        })

@login_required
@tipo_usuario_requerido(['paciente'])
def programar_cita(request, doctor_id):
    try:
        doctor = get_object_or_404(Doctor, id=doctor_id)
        paciente = request.user.paciente

        # Verificar si existe una asignación de tratamiento válida
        asignacion = AsignacionTratamiento.objects.filter(
            doctor=doctor,
            paciente=paciente,
            estado__in=['pendiente', 'en_progreso']
        ).first()

        if not asignacion:
            messages.error(request, "No tienes un tratamiento activo con este doctor.")
            return redirect('vista_paciente')

        if request.method == 'POST':
            # Crear una instancia de Cita primero
            cita = Cita(
                doctor=doctor,
                paciente=paciente,
                estado='pendiente'
            )
            
            # Usar el formulario para validar y llenar los campos restantes
            form = CitaForm(request.POST, instance=cita)
            
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, "Cita programada exitosamente.")
                    return redirect('vista_paciente')
                except ValidationError as e:
                    for error in e.messages:
                        messages.error(request, error)
                except Exception as e:
                    messages.error(request, f"Error al guardar la cita: {str(e)}")
            else:
                for field in form:
                    for error in field.errors:
                        messages.error(request, f"Error en {field.label}: {error}")
        else:
            form = CitaForm()

        doctor_info = f"Dr. {doctor.usuario.get_full_name()} ({doctor.especialidad})"
        return render(request, 'citas/programar_cita.html', {
            'form': form,
            'doctor': doctor,
            'doctor_info': doctor_info
        })
        
    except Exception as e:
        messages.error(request, f"Error inesperado: {str(e)}")
        return redirect('vista_paciente')

@login_required
@tipo_usuario_requerido(['admin'])
def editar_tratamiento(request, id):
    tratamiento = get_object_or_404(Tratamiento, id=id)
    medicamentos_asociados = {
        tm.medicamento.id: {
            'dosis': tm.dosis if tm.dosis != 'None' else '',
            'frecuencia': tm.frecuencia if tm.frecuencia != 'None' else '',
            'seleccionado': True
        }
        for tm in tratamiento.tratamientomedicamento_set.all()
    }
    
    # Listas predefinidas
    especialidades = [
        'Medicina General',
        'Cardiología',
        'Neurología',
        'Pediatría',
        'Ginecología',
        'Dermatología',
        'Oftalmología',
        'Otorrinolaringología',
        'Psiquiatría',
        'Endocrinología',
        'Gastroenterología',
        'Neumología',
        'Reumatología',
        'Urología',
        'Traumatología',
        'Oncología'
    ]
    
    condiciones_tratables = [
        'Hipertensión', 'Diabetes', 'Asma', 'Artritis',
        'Migraña', 'Epilepsia', 'Depresión', 'Ansiedad',
        'Gastritis', 'Úlcera', 'Dermatitis', 'Psoriasis',
        'Rinitis', 'Sinusitis', 'Bronquitis', 'Fibromialgia',
        'Obesidad', 'Osteoporosis', 'Arritmia', 'Colesterol alto'
    ]

    if request.method == 'POST':
        form = TratamientoForm(request.POST, instance=tratamiento)
        if form.is_valid():
            tratamiento = form.save()
            
            # Solo eliminamos las relaciones si se enviaron medicamentos
            if 'medicamentos' in request.POST:
                # Guardamos los medicamentos existentes antes de eliminarlos
                medicamentos_previos = {
                    tm.medicamento.id: {
                        'dosis': tm.dosis,
                        'frecuencia': tm.frecuencia
                    }
                    for tm in tratamiento.tratamientomedicamento_set.all()
                }
                
                TratamientoMedicamento.objects.filter(tratamiento=tratamiento).delete()
                
                medicamentos_seleccionados = request.POST.getlist('medicamentos')
                for med_id in medicamentos_seleccionados:
                    try:
                        medicamento = Medicamento.objects.get(id=med_id)
                        med_id = str(med_id)  # Convertir a string para comparar con POST
                        
                        # Obtener dosis y frecuencia del POST o usar valores previos
                        dosis = request.POST.get(f'dosis_{med_id}', '').strip()
                        frecuencia = request.POST.get(f'frecuencia_{med_id}', '').strip()
                        
                        # Si no hay nuevos valores, usar los valores previos
                        if not dosis and int(med_id) in medicamentos_previos:
                            dosis = medicamentos_previos[int(med_id)]['dosis']
                        if not frecuencia and int(med_id) in medicamentos_previos:
                            frecuencia = medicamentos_previos[int(med_id)]['frecuencia']
                        
                        # Asegurarse de que no se guarden valores None
                        dosis = '' if dosis in ['None', None] else dosis
                        frecuencia = '' if frecuencia in ['None', None] else frecuencia
                        
                        # Crear el TratamientoMedicamento
                        TratamientoMedicamento.objects.create(
                            tratamiento=tratamiento,
                            medicamento=medicamento,
                            dosis=dosis or '',  # Si es None o vacío, guardar string vacío
                            frecuencia=frecuencia or ''  # Si es None o vacío, guardar string vacío
                        )
                    except Exception as e:
                        messages.error(request, f'Error al guardar medicamento: {str(e)}')
                        return redirect('editar_tratamiento', id=id)
            
            messages.success(request, 'Tratamiento actualizado exitosamente.', extra_tags='admin_medicamento')
            return redirect('lista_tratamientos')
    else:
        form = TratamientoForm(instance=tratamiento)
    
    return render(request, 'tratamientos/form_tratamiento.html', {
        'form': form,
        'tratamiento': tratamiento,
        'medicamentos': Medicamento.objects.all(),
        'medicamentos_asociados': medicamentos_asociados,
        'especialidades': especialidades,
        'condiciones_tratables': condiciones_tratables
    })

@tipo_usuario_requerido(['admin'])
def asignar_tratamiento(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Verificar si el paciente ya tiene un tratamiento activo
    tratamiento_activo = AsignacionTratamiento.objects.filter(
        paciente=paciente,
        estado__in=['pendiente', 'en_progreso']
    ).exists()
    
    if tratamiento_activo:
        messages.error(request, 'No puedes solicitar un nuevo tratamiento mientras tengas uno activo.')
        return redirect('vista_paciente')
    
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        tratamiento_id = request.POST.get('tratamiento')
        
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            tratamiento = Tratamiento.objects.get(id=tratamiento_id)
            
            # Crear la asignación
            asignacion = AsignacionTratamiento.objects.create(
                paciente=paciente,
                doctor=doctor,
                tratamiento=tratamiento
            )
            
            # Elegir estrategia de asignación
            if paciente.alergias:
                estrategia = AsignadorConSustitutos()
            else:
                estrategia = AsignadorOriginal()
            
            # Asignar medicamentos considerando alergias
            asignacion.asignar_medicamentos(estrategia)
            
            messages.success(request, 'Tratamiento asignado exitosamente')
            return redirect('vista_admin')
            
        except Exception as e:
            messages.error(request, f'Error al asignar tratamiento: {str(e)}')
            return redirect('asignar_tratamiento', paciente_id=paciente_id)