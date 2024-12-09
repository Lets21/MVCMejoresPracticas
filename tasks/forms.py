from django.forms import ModelForm
from .models import (
    Task, 
    Tratamiento, 
    Medicamento, 
    TratamientoMedicamento,
    Cita,
    TipoUsuario
)
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from datetime import datetime, time
from django.core.exceptions import ValidationError

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'important']

class PacienteRegistroForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Nombre')
    last_name = forms.CharField(max_length=30, required=True, help_text='Apellido')
    edad = forms.IntegerField(required=True)
    condiciones_medicas = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True
    )
    alergias = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2']

class DoctorRegistroForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Nombre')
    last_name = forms.CharField(max_length=30, required=True, help_text='Apellido')
    especialidad = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2', 'especialidad']

class MedicamentoTratamientoForm(forms.Form):
    medicamento = forms.ModelChoiceField(
        queryset=Medicamento.objects.all(),
        widget=forms.HiddenInput()
    )
    dosis = forms.CharField(max_length=100)
    frecuencia = forms.CharField(max_length=100)

class TratamientoForm(forms.ModelForm):
    # Listas predefinidas
    ESPECIALIDADES = [
        ('Medicina General', 'Medicina General'),
        ('Cardiología', 'Cardiología'),
        ('Neurología', 'Neurología'),
        ('Pediatría', 'Pediatría'),
        ('Ginecología', 'Ginecología'),
        ('Dermatología', 'Dermatología'),
        ('Oftalmología', 'Oftalmología'),
        ('Otorrinolaringología', 'Otorrinolaringología'),
        ('Psiquiatría', 'Psiquiatría'),
        ('Endocrinología', 'Endocrinología'),
        ('Gastroenterología', 'Gastroenterología'),
        ('Neumología', 'Neumología'),
        ('Reumatología', 'Reumatología'),
        ('Urología', 'Urología'),
        ('Traumatología', 'Traumatología'),
        ('Oncología', 'Oncología')
    ]

    especialidad_requerida = forms.ChoiceField(
        choices=ESPECIALIDADES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Tratamiento
        fields = [
            'nombre', 
            'descripcion', 
            'duracion', 
            'costo', 
            'especialidad_requerida',
            'condiciones_tratadas',
            'edad_minima',
            'edad_maxima'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'condiciones_tratadas': forms.Textarea(attrs={'rows': 2}),
        }

class MedicamentoForm(forms.ModelForm):
    # Componentes principales comunes
    COMPONENTES_PRINCIPALES = [
        ('Enalapril maleato', 'Enalapril maleato'),
        ('Losartán potásico', 'Losartán potásico'),
        ('Amlodipino besilato', 'Amlodipino besilato'),
        ('Salbutamol sulfato', 'Salbutamol sulfato'),
        ('Bromuro de ipratropio', 'Bromuro de ipratropio'),
        ('Montelukast sódico', 'Montelukast sódico'),
        ('Betametasona dipropionato', 'Betametasona dipropionato'),
        ('Tacrolimus monohidrato', 'Tacrolimus monohidrato'),
        ('Metformina clorhidrato', 'Metformina clorhidrato'),
        ('Sitagliptina fosfato', 'Sitagliptina fosfato')
    ]

    componente_principal = forms.ChoiceField(
        choices=COMPONENTES_PRINCIPALES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    contraindicaciones = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )

    class Meta:
        model = Medicamento
        fields = ['nombre', 'descripcion', 'componente_principal', 'contraindicaciones']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['fecha', 'hora', 'motivo']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'hora': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describa el motivo de su cita'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')

        if fecha and hora:
            # Verificar que sea día laborable
            if fecha.weekday() >= 5:
                raise forms.ValidationError('Las citas solo se pueden programar de lunes a viernes.')

            # Verificar horario laboral
            if not (time(8, 0) <= hora <= time(18, 0)):
                raise forms.ValidationError('Las citas solo pueden programarse entre 8:00 AM y 6:00 PM.')

        return cleaned_data

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class TipoUsuarioForm(forms.ModelForm):
    class Meta:
        model = TipoUsuario
        fields = ['tipo']
        widgets = {
            'tipo': forms.Select(choices=[
                ('admin', 'Administrador'),
                ('doctor', 'Doctor'),
                ('paciente', 'Paciente')
            ], attrs={'class': 'form-control'})
        }