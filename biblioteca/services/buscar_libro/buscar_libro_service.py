from django.db.models import Q
from biblioteca.models import Libro

class BuscarLibroService:

    @classmethod
    def ejecutar(cls, criterio=""):
        """Busca libros coincidiendo por título, autor o ISBN. Si no hay criterio, devuelve todos."""
        texto = cls.limpiar_texto(criterio)
        if not texto:
            return Libro.objects.all()

        return Libro.objects.filter(
            Q(titulo__icontains=texto) |
            Q(autor__icontains=texto) |
            Q(isbn__icontains=texto)
        )

    @staticmethod
    def limpiar_texto(texto):
        """Remueve espacios innecesarios del criterio de búsqueda."""
        return str(texto).strip() if texto else ""