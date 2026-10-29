from django.core.exceptions import ValidationError
from biblioteca.models import Socio, Reserva

class EliminarSocioService:

    @classmethod
    def ejecutar(cls, id_socio):
        """Elimina un socio si no posee libros pendientes de devolución."""
        socio = Socio.objects.filter(id=id_socio).first()
        if not socio:
            raise ValidationError("No existe ningún socio con el ID ingresado.")

        if cls.tiene_reservas_activas(socio):
            raise ValidationError(f"No se puede eliminar a {socio.nombre_completo} porque posee reservas activas o retiradas.")

        nombre_socio = socio.nombre_completo
        socio.delete()
        return nombre_socio

    @staticmethod
    def tiene_reservas_activas(socio):
        """Comprueba si el socio tiene reservas activas o retiradas."""
        return Reserva.objects.filter(socio=socio, estado__in=['ACTIVO', 'RETIRADO']).exists()