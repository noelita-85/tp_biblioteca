from django.core.exceptions import ValidationError
from biblioteca.models import Libro

class EditarLibroService:

    @classmethod
    def ejecutar(cls, id_libro, titulo=None, autor=None, isbn=None, cantidad_total=None):
        """Actualiza la información de un libro existente."""
        libro = Libro.objects.filter(id=id_libro).first()
        if not libro:
            raise ValidationError("No existe ningún libro con el ID ingresado.")

        if isbn and isbn != libro.isbn:
            isbn_limpio = isbn.replace("-", "").strip()
            if not cls.es_isbn_valido(isbn_limpio):
                raise ValidationError("El ISBN debe contener 10 o 13 dígitos numéricos.")
            if cls.existe_isbn_en_otro_libro(isbn_limpio, id_libro):
                raise ValidationError(f"El ISBN {isbn_limpio} ya pertenece a otro libro.")
            libro.isbn = isbn_limpio

        if titulo is not None and titulo.strip():
            libro.titulo = titulo.strip()

        if autor is not None and autor.strip():
            libro.autor = autor.strip()

        if cantidad_total is not None:
            if not cls.es_cantidad_valida(cantidad_total):
                raise ValidationError("La cantidad de ejemplares no puede ser negativa.")
            libro.cantidad_total = cantidad_total

        libro.save()
        return libro

    @staticmethod
    def es_isbn_valido(isbn):
        """Valida longitud y formato del ISBN."""
        return isbn.isdigit() and len(isbn) in (10, 13)

    @staticmethod
    def existe_isbn_en_otro_libro(isbn, id_libro):
        """Evita duplicados de ISBN al actualizar."""
        return Libro.objects.filter(isbn=isbn).exclude(id=id_libro).exists()

    @staticmethod
    def es_cantidad_valida(cantidad):
        """Valida que la cantidad no sea negativa."""
        return isinstance(cantidad, int) and cantidad >= 0