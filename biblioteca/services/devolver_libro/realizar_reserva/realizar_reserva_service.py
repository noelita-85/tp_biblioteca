from django.core.exceptions import ValidationError
from biblioteca.models import Libro, Socio, Reserva

class RealizarReservaService:

    @classmethod
    def ejecutar(cls, id_socio, id_libro):
        """Crea una reserva de un libro para un socio determinado."""
        socio = Socio.objects.filter(id=id_socio).first()
        if not socio:
            raise ValidationError("No existe un socio registrado con ese ID.")

        libro = Libro.objects.filter(id=id_libro).first()
        if not libro:
            raise ValidationError("No existe un libro registrado con ese ID.")

        if not cls.hay_stock_disponible(libro):
            raise ValidationError(f"El libro '{libro.titulo}' no tiene ejemplares disponibles.")

        reserva = Reserva.objects.create(
            socio=socio,
            libro=libro,
            estado='ACTIVO'
        )
        return reserva

    @staticmethod
    def hay_stock_disponible(libro):
        """Valida que el libro tenga al menos 1 ejemplar disponible."""
        return libro.cantidad_total > 0