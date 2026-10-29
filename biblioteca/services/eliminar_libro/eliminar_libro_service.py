from django.core.exceptions import ValidationError
from biblioteca.models import Libro, Reserva

class EliminarLibroService:

    @classmethod
    def ejecutar(cls, id_libro):
        """Elimina un libro de la base de datos si no tiene reservas pendientes."""
        libro = Libro.objects.filter(id=id_libro).first()
        if not libro:
            raise ValidationError("No existe ningún libro con el ID ingresado.")

        if cls.tiene_reservas_activas(libro):
            raise ValidationError(f"No se puede eliminar '{libro.titulo}' porque tiene reservas activas o prestadas.")

        titulo_eliminado = libro.titulo
        libro.delete()
        return titulo_eliminado

    @staticmethod
    def tiene_reservas_activas(libro):
        """Comprueba si el libro está asociado a reservas activas o retiradas."""
        return Reserva.objects.filter(libro=libro, estado__in=['ACTIVO', 'RETIRADO']).exists()