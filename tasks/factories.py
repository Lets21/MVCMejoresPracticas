class MedicamentoFactory:
    @staticmethod
    def crear_medicamento(nombre, descripcion, componente_principal, contraindicaciones):
        return Medicamento.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            componente_principal=componente_principal,
            contraindicaciones=contraindicaciones
        )