from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from biblioteca.models import Libro, Socio, Reserva
from biblioteca.services import (
    realizar_reserva,
    retirar_libro,
    devolver_libro,
)

class EvaluacionProfesorTestCase(TestCase):

    def setUp(self):
        """Configuración de datos base para las pruebas."""
        self.libro = Libro.objects.create(
            titulo="Rayuela",
            autor="Julio Cortázar",
            isbn="9789505113569",
            anio_publicacion=1963,
            editorial="Sudamericana",
            cantidad_total=2,
            cantidad_disponible=2,
        )
        
        self.socio = Socio.objects.create(
            nombre="María",
            apellido="Gómez",
            dni="40123456",
            id_socio=2001,
            activo=True,
        )

    # 1. Libro inexistente
    def test_libro_inexistente(self):
        with self.assertRaises(ValidationError):
            realizar_reserva(self.socio.id_socio, "0000000000000")

    # 2. Socio inexistente
    def test_socio_inexistente(self):
        with self.assertRaises(ValidationError):
            realizar_reserva(9999, self.libro.isbn)

    # 3. ISBN duplicado
    def test_isbn_duplicado(self):
        with self.assertRaises(IntegrityError):
            Libro.objects.create(
                titulo="Otro Libro",
                autor="Otro Autor",
                isbn="9789505113569",  # Mismo ISBN que el de setUp
                anio_publicacion=2020,
                editorial="Planeta",
                cantidad_total=1,
                cantidad_disponible=1,
            )

    # 4. DNI duplicado
    def test_dni_duplicado(self):
        with self.assertRaises(IntegrityError):
            Socio.objects.create(
                nombre="Lucas",
                apellido="Pérez",
                dni="40123456",  # Mismo DNI que el de setUp
                id_socio=2002,
                activo=True,
            )

    # 5. Intentar reservar un libro sin disponibilidad
    def test_reservar_libro_sin_disponibilidad(self):
        self.libro.cantidad_disponible = 0
        self.libro.save()

        with self.assertRaises(ValidationError):
            realizar_reserva(self.socio.id_socio, self.libro.isbn)

    # 6. Intentar reservar siendo un socio inactivo
    def test_reservar_socio_inactivo(self):
        self.socio.activo = False
        self.socio.save()

        with self.assertRaises(ValidationError):
            realizar_reserva(self.socio.id_socio, self.libro.isbn)
            

    # 7. Cancelar/Devolver una reserva ya retirada (Tratar de operar un estado no válido)
    def test_cancelar_reserva_ya_retirada(self):
        reserva = realizar_reserva(self.socio.id_socio, self.libro.isbn)
        retirar_libro(reserva.id)  # Estado pasa a RETIRADA

        # Un segundo intento de retiro o cancelación inválida debe fallar
        with self.assertRaises(ValidationError):
            retirar_libro(reserva.id)

    # 8. Devolver una reserva que no fue retirada
    def test_devolver_reserva_no_retirada(self):
        reserva = realizar_reserva(self.socio.id_socio, self.libro.isbn)  # Estado PENDIENTE

        # Intentar devolver directamente sin haber retirado antes
        with self.assertRaises(ValidationError):
            devolver_libro(reserva.id)

    # 9. Ingresar opciones incorrectas en el menú
    def test_opciones_incorrectas_menu(self):
        # Valida que ante un ID de reserva inválido o inexistente el servicio devuelva ValidationError
        with self.assertRaises(ValidationError):
            devolver_libro(99999)
            
def test_obtener_reservas_por_socio(self):
        realizar_reserva(self.socio.id_socio, self.libro.isbn)
        reservas = obtener_reservas_por_socio(self.socio.id_socio)
        self.assertEqual(reservas.count(), 1)

def test_obtener_todas_las_reservas(self):
        realizar_reserva(self.socio.id_socio, self.libro.isbn)
        reservas = obtener_todas_las_reservas()
        self.assertEqual(reservas.count(), 1)            