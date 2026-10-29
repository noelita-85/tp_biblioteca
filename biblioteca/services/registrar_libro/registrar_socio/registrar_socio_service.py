from django.core.exceptions import ValidationError
from biblioteca.models import Socio

class RegistrarSocioService:

    @classmethod
    def ejecutar(cls, nombre, apellido, dni):
        """Punto de entrada principal para registrar un nuevo socio."""
        dni_limpio = str(dni).strip()

        if not cls.es_dni_valido(dni_limpio):
            raise ValidationError("El DNI debe tener entre 7 y 8 dígitos numéricos.")

        if cls.existe_dni(dni_limpio):
            raise ValidationError(f"Ya existe un socio registrado con el DNI {dni_limpio}.")

        socio = Socio.objects.create(
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            dni=dni_limpio
        )
        return socio

    @staticmethod
    def es_dni_valido(dni):
        """Valida que el formato del DNI sea numérico y de longitud correcta."""
        return dni.isdigit() and 7 <= len(dni) <= 8

    @staticmethod
    def existe_dni(dni):
        """Verifica si el DNI ya está registrado en la base de datos."""
        return Socio.objects.filter(dni=dni).exists()