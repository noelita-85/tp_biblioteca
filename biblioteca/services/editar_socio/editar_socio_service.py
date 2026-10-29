from django.core.exceptions import ValidationError
from biblioteca.models import Socio

class EditarSocioService:

    @classmethod
    def ejecutar(cls, id_socio, nombre=None, apellido=None, dni=None):
        """Actualiza los datos personales de un socio."""
        socio = Socio.objects.filter(id=id_socio).first()
        if not socio:
            raise ValidationError("No existe ningún socio con el ID ingresado.")

        if dni and dni != socio.dni:
            dni_limpio = str(dni).strip()
            if not cls.es_dni_valido(dni_limpio):
                raise ValidationError("El DNI debe tener entre 7 y 8 dígitos numéricos.")
            if cls.existe_dni_en_otro_socio(dni_limpio, id_socio):
                raise ValidationError(f"El DNI {dni_limpio} ya está registrado para otro socio.")
            socio.dni = dni_limpio

        if nombre is not None and nombre.strip():
            socio.nombre = nombre.strip()

        if apellido is not None and apellido.strip():
            socio.apellido = apellido.strip()

        socio.save()
        return socio

    @staticmethod
    def es_dni_valido(dni):
        """Valida formato básico del DNI."""
        return dni.isdigit() and 7 <= len(dni) <= 8

    @staticmethod
    def existe_dni_en_otro_socio(dni, id_socio):
        """Evita duplicados de DNI al actualizar."""
        return Socio.objects.filter(dni=dni).exclude(id=id_socio).exists()