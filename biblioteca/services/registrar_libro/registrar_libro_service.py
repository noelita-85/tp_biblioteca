from django.core.exceptions import ValidationError
from biblioteca.models import Libro


class RegistrarLibroService:

    @classmethod
    def ejecutar(cls, titulo, autor, isbn, cantidad_total=1, anio_publicacion=2024):
        """Registra un nuevo libro en el sistema."""
        if not titulo or not autor or not isbn:
            raise ValidationError("Título, autor e ISBN son obligatorios.")

        isbn_limpio = isbn.replace("-", "").strip()
        if not cls.es_isbn_valido(isbn_limpio):
            raise ValidationError("El ISBN debe contener 10 o 13 dígitos numéricos.")

        if cls.existe_isbn(isbn_limpio):
            raise ValidationError(f"Ya existe un libro registrado con el ISBN {isbn_limpio}.")

        cantidad_disponible = cantidad_total

        libro = Libro.objects.create(
            titulo=titulo.strip(),
            autor=autor.strip(),
            isbn=isbn_limpio,
            anio_publicacion=anio_publicacion,
            cantidad_total=cantidad_total,
            cantidad_disponible=cantidad_disponible
        )
        return libro

    @staticmethod
    def es_isbn_valido(isbn):
        return isbn.isdigit() and len(isbn) in (10, 13)

    @staticmethod
    def existe_isbn(isbn):
        return Libro.objects.filter(isbn=isbn).exists()