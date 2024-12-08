from django.core.management.base import BaseCommand
from tasks.fixtures.initial_data import crear_datos_iniciales
from tasks.models import Medicamento, MedicamentoSustituto, Tratamiento, TratamientoMedicamento

class Command(BaseCommand):
    help = 'Crea datos iniciales para el sistema médico'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creando datos iniciales...')
        
        # Limpiar datos existentes
        Medicamento.objects.all().delete()
        MedicamentoSustituto.objects.all().delete()
        Tratamiento.objects.all().delete()
        TratamientoMedicamento.objects.all().delete()
        
        # Crear todos los datos iniciales (incluyendo medicamentos)
        crear_datos_iniciales()
        
        self.stdout.write(self.style.SUCCESS('Datos creados exitosamente'))