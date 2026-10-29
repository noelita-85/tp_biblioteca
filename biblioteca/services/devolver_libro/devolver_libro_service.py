from django.core.exceptions import ValidationError
from biblioteca.models import Reserva, ReservaEstado


class DevolverLibroService:

    @classmethod
    def ejecutar(cls, id_reserva):
        reserva = Reserva.objects.select_related('libro', 'socio').filter(id=id_reserva).first()
        if not reserva:
            raise ValidationError("No existe ninguna reserva con el ID ingresado.")

        if reserva.estado != ReservaEstado.RETIRADA:
            raise ValidationError("Solo se pueden devolver libros de reservas en estado RETIRADA.")

        reserva.estado = ReservaEstado.FINALIZADA
        reserva.save(update_fields=['estado'])

        reserva.libro.liberar_ejemplar()
        return reserva