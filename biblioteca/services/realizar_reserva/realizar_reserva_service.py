from django.core.exceptions import ValidationError
from biblioteca.models import Libro, Socio, Reserva, ReservaEstado


class RealizarReservaService:

    @classmethod
    def ejecutar(cls, id_socio, id_libro):
        """Crea una reserva de un libro para un socio determinado."""
        socio = Socio.objects.filter(id=id_socio).first()
        if not socio:
            raise ValidationError("No existe ningún socio registrado con el ID ingresado.")

        libro = Libro.objects.filter(id=id_libro).first()
        if not libro:
            raise ValidationError("No existe ningún libro registrado con el ID ingresado.")

        if not cls.socio_esta_habilitado(socio):
            raise ValidationError(f"El socio {socio.nombre_completo} está inactivo y no puede reservar.")

        if not cls.hay_stock_disponible(libro):
            raise ValidationError(f"El libro '{libro.titulo}' no tiene ejemplares disponibles.")

        # Descuenta un ejemplar del stock y actualiza la actividad del socio
        libro.reservar_ejemplar()
        socio.registrar_actividad()

        reserva = Reserva.objects.create(
            socio=socio,
            libro=libro,
            estado=ReservaEstado.PENDIENTE
        )
        return reserva

    @staticmethod
    def hay_stock_disponible(libro):
        """Usa la @property esta_disponible del modelo Libro."""
        return libro.esta_disponible

    @staticmethod
    def socio_esta_habilitado(socio):
        """Verifica si el socio se encuentra en estado activo."""
        return socio.es_activo