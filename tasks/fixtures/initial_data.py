from django.contrib.auth.models import User
from tasks.models import Doctor, Paciente, TipoUsuario, Tratamiento, Medicamento, TratamientoMedicamento, MedicamentoSustituto

admin_data = {
    "username": "admin",
    "first_name": "Administrador",
    "last_name": "Sistema",
    "password": "admin123"
}

# Crear Doctores
doctores_data = [
    {
        "username": "dr.garcia",
        "first_name": "Carlos",
        "last_name": "García",
        "especialidad": "Cardiología"
    },
    {
        "username": "dra.rodriguez",
        "first_name": "Ana",
        "last_name": "Rodríguez",
        "especialidad": "Endocrinología"
    },
    {
        "username": "dr.martinez",
        "first_name": "Juan",
        "last_name": "Martínez",
        "especialidad": "Reumatología"
    },
    {
        "username": "dra.lopez",
        "first_name": "María",
        "last_name": "López",
        "especialidad": "Neumología"
    },
    {
        "username": "dr.fernandez",
        "first_name": "Ricardo",
        "last_name": "Fernndez",
        "especialidad": "Neurología"
    }
]

# Crear Pacientes con alergias específicas
pacientes_data = [
    {
        "username": "juan.perez",
        "first_name": "Juan",
        "last_name": "Pérez",
        "edad": 45,
        "condiciones_medicas": "hipertensión, diabetes tipo 2",
        "alergias": "IECA, penicilina"  # Alérgico a Enalapril (IECA)
    },
    {
        "username": "pedro.gomez",
        "first_name": "Pedro",
        "last_name": "Gómez",
        "edad": 45,
        "condiciones_medicas": "migraña, epilepsia",  # Condiciones neurológicas
        "alergias": "ninguna"
    },
    {
        "username": "maria.sanchez",
        "first_name": "María",
        "last_name": "Sánchez",
        "edad": 35,
        "condiciones_medicas": "asma, rinitis",
        "alergias": "sulfatos"  # Alérgica a Salbutamol (sulfatos)
    }
]

# Crear Tratamientos
tratamientos_data = [
    {
        "nombre": "Control Cardiológico Integral",
        "descripcion": "Seguimiento completo de pacientes con hipertensión y condiciones cardíacas",
        "duracion": "6 meses",
        "costo": 1500.00,
        "especialidad_requerida": "Cardiología",
        "condiciones_tratadas": "hipertensión, cardiopatía, arritmia",
        "edad_minima": 40,
        "edad_maxima": 85
    },
    {
        "nombre": "Tratamiento para Asma Pediátrico",
        "descripcion": "Control y seguimiento de asma bronquial para niños",
        "duracion": "4 meses",
        "costo": 700.00,
        "especialidad_requerida": "Neumología",
        "condiciones_tratadas": "asma, bronquitis, asma bronquial",
        "edad_minima": 5,
        "edad_maxima": 18
    },
    {
        "nombre": "Tratamiento para Asma Adultos",
        "descripcion": "Control y seguimiento de asma bronquial para adultos",
        "duracion": "6 meses",
        "costo": 900.00,
        "especialidad_requerida": "Neumología",
        "condiciones_tratadas": "asma, bronquitis, asma bronquial",
        "edad_minima": 19,
        "edad_maxima": 80
    }
]

# Medicamentos con contraindicaciones específicas
medicamentos_data = [
    # Grupo Antihipertensivos
    {
        "nombre": "Enalapril",
        "descripcion": "IECA para hipertensión",
        "contraindicaciones": "IECA, penicilina",
        "componente_principal": "Enalapril maleato"
    },
    {
        "nombre": "Losartán",
        "descripcion": "ARA-II para hipertensión",
        "contraindicaciones": "embarazo",
        "componente_principal": "Losartán potásico"
    },
    {
        "nombre": "Amlodipino",
        "descripcion": "Bloqueador de calcio para hipertensión",
        "contraindicaciones": "insuficiencia cardíaca",
        "componente_principal": "Amlodipino besilato"
    },
    # Grupo Antiasmáticos
    {
        "nombre": "Salbutamol",
        "descripcion": "Broncodilatador para asma",
        "contraindicaciones": "sulfatos",
        "componente_principal": "Salbutamol sulfato"
    },
    {
        "nombre": "Ipratropio",
        "descripcion": "Broncodilatador alternativo",
        "contraindicaciones": "glaucoma",
        "componente_principal": "Bromuro de ipratropio"
    },
    {
        "nombre": "Montelukast",
        "descripcion": "Antileucotrieno para asma",
        "contraindicaciones": "enfermedad hepática",
        "componente_principal": "Montelukast sódico"
    },
    # Grupo Dermatológico
    {
        "nombre": "Betametasona",
        "descripcion": "Corticoide para condiciones dermatológicas",
        "contraindicaciones": "látex",
        "componente_principal": "Betametasona dipropionato"
    },
    {
        "nombre": "Tacrolimus",
        "descripcion": "Inmunosupresor tópico",
        "contraindicaciones": "inmunosupresión",
        "componente_principal": "Tacrolimus monohidrato"
    },
    # Grupo Antidiabéticos
    {
        "nombre": "Metformina",
        "descripcion": "Antidiabético oral",
        "contraindicaciones": "insuficiencia renal",
        "componente_principal": "Metformina clorhidrato"
    },
    {
        "nombre": "Sitagliptina",
        "descripcion": "Inhibidor DPP-4 para diabetes",
        "contraindicaciones": "pancreatitis",
        "componente_principal": "Sitagliptina fosfato"
    }
]

# Relaciones entre medicamentos y sus sustitutos
medicamentos_sustitutos_data = [
    # Grupo Antihipertensivos
    {
        "medicamento_original": "Enalapril",
        "medicamento_sustituto": "Losartán",
        "motivo_sustitucion": "Alternativa para pacientes alérgicos a IECA"
    },
    {
        "medicamento_original": "Losartán",
        "medicamento_sustituto": "Amlodipino",
        "motivo_sustitucion": "Alternativa para embarazadas"
    },
    {
        "medicamento_original": "Amlodipino",
        "medicamento_sustituto": "Enalapril",
        "motivo_sustitucion": "Alternativa para insuficiencia cardíaca"
    },
    # Grupo Antiasmáticos
    {
        "medicamento_original": "Salbutamol",
        "medicamento_sustituto": "Ipratropio",
        "motivo_sustitucion": "Alternativa para pacientes alérgicos a sulfatos"
    },
    {
        "medicamento_original": "Ipratropio",
        "medicamento_sustituto": "Montelukast",
        "motivo_sustitucion": "Alternativa para pacientes con glaucoma"
    },
    {
        "medicamento_original": "Montelukast",
        "medicamento_sustituto": "Salbutamol",
        "motivo_sustitucion": "Alternativa para pacientes con enfermedad hepática"
    },
    # Grupo Dermatológico
    {
        "medicamento_original": "Betametasona",
        "medicamento_sustituto": "Tacrolimus",
        "motivo_sustitucion": "Alternativa para pacientes alérgicos al látex"
    },
    {
        "medicamento_original": "Tacrolimus",
        "medicamento_sustituto": "Betametasona",
        "motivo_sustitucion": "Alternativa para pacientes inmunocomprometidos"
    },
    # Grupo Antidiabéticos
    {
        "medicamento_original": "Metformina",
        "medicamento_sustituto": "Sitagliptina",
        "motivo_sustitucion": "Alternativa para pacientes con insuficiencia renal"
    },
    {
        "medicamento_original": "Sitagliptina",
        "medicamento_sustituto": "Metformina",
        "motivo_sustitucion": "Alternativa para pacientes con pancreatitis"
    }
]

# Relacionar medicamentos con tratamientos
tratamientos_medicamentos_data = [
    {
        "tratamiento": "Control Cardiológico Integral",
        "medicamentos": [
            {
                "medicamento": "Enalapril",
                "dosis": "10mg",
                "frecuencia": "1 vez al día"
            }
        ]
    },
    {
        "tratamiento": "Tratamiento para Asma Pediátrico",
        "medicamentos": [
            {
                "medicamento": "Salbutamol",
                "dosis": "100mcg",
                "frecuencia": "2 inhalaciones cada 8 horas"
            }
        ]
    },
    {
        "tratamiento": "Tratamiento para Asma Adultos",
        "medicamentos": [
            {
                "medicamento": "Salbutamol",
                "dosis": "200mcg",
                "frecuencia": "2 inhalaciones cada 6 horas"
            }
        ]
    }
]

def crear_datos_iniciales():
    # Crear Administrador
    try:
        admin_user = User.objects.create_superuser(
            username=admin_data["username"],
            password=admin_data["password"],
            first_name=admin_data["first_name"],
            last_name=admin_data["last_name"]
        )
        TipoUsuario.objects.create(usuario=admin_user, tipo='admin')
    except Exception as e:
        print(f"Error al crear administrador: {e}")

    # Crear Doctores
    for doctor_data in doctores_data:
        user = User.objects.create_user(
            username=doctor_data["username"],
            password="contraseña123",
            first_name=doctor_data["first_name"],
            last_name=doctor_data["last_name"]
        )
        doctor = Doctor.objects.create(
            usuario=user,
            especialidad=doctor_data["especialidad"]
        )
        TipoUsuario.objects.create(usuario=user, tipo='doctor')

    # Crear Pacientes
    for paciente_data in pacientes_data:
        user = User.objects.create_user(
            username=paciente_data["username"],
            password="contraseña123",
            first_name=paciente_data["first_name"],
            last_name=paciente_data["last_name"]
        )
        paciente = Paciente.objects.create(
            usuario=user,
            edad=paciente_data["edad"],
            condiciones_medicas=paciente_data["condiciones_medicas"],
            alergias=paciente_data["alergias"]
        )
        TipoUsuario.objects.create(usuario=user, tipo='paciente')

    # Crear Tratamientos
    for tratamiento_data in tratamientos_data:
        Tratamiento.objects.create(**tratamiento_data)

    # Crear Medicamentos y guardar referencias
    medicamentos_dict = {}
    for medicamento_data in medicamentos_data:
        medicamento = Medicamento.objects.create(**medicamento_data)
        medicamentos_dict[medicamento_data['nombre']] = medicamento

    # Crear Relaciones entre medicamentos y sus sustitutos
    for sustituto_data in medicamentos_sustitutos_data:
        MedicamentoSustituto.objects.create(
            medicamento_original=medicamentos_dict[sustituto_data['medicamento_original']],
            medicamento_sustituto=medicamentos_dict[sustituto_data['medicamento_sustituto']],
            motivo_sustitucion=sustituto_data['motivo_sustitucion']
        )

    # Relacionar medicamentos con tratamientos
    for trat_med_data in tratamientos_medicamentos_data:
        tratamiento = Tratamiento.objects.get(nombre=trat_med_data['tratamiento'])
        for med_data in trat_med_data['medicamentos']:
            TratamientoMedicamento.objects.create(
                tratamiento=tratamiento,
                medicamento=medicamentos_dict[med_data['medicamento']],
                dosis=med_data['dosis'],
                frecuencia=med_data['frecuencia']
            )
        