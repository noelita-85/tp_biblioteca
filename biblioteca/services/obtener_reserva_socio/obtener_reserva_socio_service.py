from django.core.exceptions import ValidationError
from biblioteca.models import Reserva, Socio

class ObtenerReservaSocioService:

    @classmethod
    def ejecutar(cls, id_socio):
        """Obtiene el historial de reservas de un socio específico."""
        if not cls.es_id_valido(id_socio):
            raise ValidationError("El ID de socio debe ser un entero positivo.")

        socio = Socio.objects.filter(id=id_socio).first()
        if not socio:
            raise ValidationError("No existe ningún socio registrado con ese ID.")

        return Reserva.objects.filter(socio=socio).select_related('libro', 'socio')

    @staticmethod
    def es_id_valido(id_socio):
        """Valida que el identificador ingresado sea numérico."""
        return str(id_socio).isdigit()