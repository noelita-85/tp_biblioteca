from django.test import TestCase
from django.core.exceptions import ValidationError
from biblioteca.models import Libro, Socio, Reserva, ReservaEstado
from biblioteca.services import (
    RegistrarLibroService,
    RegistrarSocioService,
    RealizarReservaService,
    RetirarLibroService,
    DevolverLibroService,
)


class ModelosPropertyTestCase(TestCase):

    def test_socio_nombre_completo_property(self):
        """Verifica que la @property 'nombre_completo' concatene adecuadamente."""
        socio = Socio.objects.create(nombre="Juan", apellido="Pérez", dni="12345678")
        self.assertEqual(socio.nombre_completo, "Juan Pérez")

    def test_libro_esta_disponible_property(self):
        """Verifica la @property 'esta_disponible' en el modelo Libro."""
        libro = Libro.objects.create(
            titulo="El Aleph",
            autor="Jorge Luis Borges",
            isbn="9789500428669",
            anio_publicacion=1949,
            cantidad_total=1,
            cantidad_disponible=1
        )
        self.assertTrue(libro.esta_disponible)
        libro.cantidad_disponible = 0
        self.assertFalse(libro.esta_disponible)


class ServiciosTestCase(TestCase):

    def setUp(self):
        self.socio = RegistrarSocioService.ejecutar(
            nombre="Ana",
            apellido="García",
            dni="87654321"
        )
        self.libro = RegistrarLibroService.ejecutar(
            titulo="Ficciones",
            autor="Jorge Luis Borges",
            isbn="9789500428676",
            cantidad_total=1
        )

    def test_registrar_socio_dni_duplicado(self):
        """Valida que el servicio impida registrar dos socios con el mismo DNI."""
        with self.assertRaises(ValidationError):
            RegistrarSocioService.ejecutar(nombre="Carlos", apellido="Gómez", dni="87654321")

    def test_flujo_reserva_y_devolucion(self):
        """Prueba la integración completa de reserva, retiro y devolución."""
        # 1. Crear reserva (estado inicial: PENDIENTE)
        reserva = RealizarReservaService.ejecutar(self.socio.id, self.libro.id)
        self.assertEqual(reserva.estado, ReservaEstado.PENDIENTE)

        # 2. Retirar libro (estado pasa a: RETIRADA)
        reserva_retirada = RetirarLibroService.ejecutar(reserva.id)
        self.assertEqual(reserva_retirada.estado, ReservaEstado.RETIRADA)

        # 3. Devolver libro (estado pasa a: FINALIZADA)
        reserva_devuelta = DevolverLibroService.ejecutar(reserva.id)
        self.assertEqual(reserva_devuelta.estado, ReservaEstado.FINALIZADA)


class RealizarReservaTestCase(TestCase):

    def setUp(self):
        self.socio = RegistrarSocioService.ejecutar(
            nombre="Laura",
            apellido="Mendoza",
            dni="11223344"
        )
        self.libro_con_stock = RegistrarLibroService.ejecutar(
            titulo="Cien años de soledad",
            autor="Gabriel García Márquez",
            isbn="9780307474728",
            cantidad_total=1
        )
        self.libro_sin_stock = RegistrarLibroService.ejecutar(
            titulo="Rayuela",
            autor="Julio Cortázar",
            isbn="9788437604572",
            cantidad_total=0
        )

    def test_realizar_reserva_exitosa(self):
        """Verifica que se cree la reserva correctamente en estado PENDIENTE."""
        reserva = RealizarReservaService.ejecutar(self.socio.id, self.libro_con_stock.id)
        self.assertEqual(reserva.estado, ReservaEstado.PENDIENTE)
        self.assertEqual(reserva.socio, self.socio)
        self.assertEqual(reserva.libro, self.libro_con_stock)

    def test_error_reserva_socio_inexistente(self):
        """Lanza ValidationError si el ID de socio no existe."""
        with self.assertRaises(ValidationError):
            RealizarReservaService.ejecutar(id_socio=9999, id_libro=self.libro_con_stock.id)

    def test_error_reserva_libro_inexistente(self):
        """Lanza ValidationError si el ID de libro no existe."""
        with self.assertRaises(ValidationError):
            RealizarReservaService.ejecutar(id_socio=self.socio.id, id_libro=9999)

    def test_error_reserva_sin_stock(self):
        """Lanza ValidationError si el libro no tiene ejemplares disponibles."""
        with self.assertRaises(ValidationError):
            RealizarReservaService.ejecutar(self.socio.id, self.libro_sin_stock.id)   