from django.db.models import Q
from biblioteca.models import Socio

class BuscarSocioService:

    @classmethod
    def ejecutar(cls, criterio=""):
        """Busca socios por nombre, apellido o DNI. Si no hay criterio, devuelve todos."""
        texto = cls.limpiar_texto(criterio)
        if not texto:
            return Socio.objects.all()

        return Socio.objects.filter(
            Q(nombre__icontains=texto) |
            Q(apellido__icontains=texto) |
            Q(dni__icontains=texto)
        )

    @staticmethod
    def limpiar_texto(texto):
        """Remueve espacios innecesarios del criterio de búsqueda."""
        return str(texto).strip() if texto else ""