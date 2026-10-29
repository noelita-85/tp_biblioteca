from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from biblioteca.services import (
    RegistrarLibroService,
    RegistrarSocioService,
    BuscarLibroService,
    BuscarSocioService,
    RealizarReservaService,
    RetirarLibroService,
    DevolverLibroService,
    EditarLibroService,
    EditarSocioService,
    EliminarLibroService,
    EliminarSocioService,
    ObtenerReservaSocioService,
    ObtenerReservaTotalService,
)


class Command(BaseCommand):
    help = "Inicia el sistema interactivo de reserva de libros"

    def handle(self, *args, **options):
        while True:
            self.stdout.write("\n=== SISTEMA DE GESTIÓN DE BIBLIOTECA ===")
            self.stdout.write("1. Registrar Libro")
            self.stdout.write("2. Registrar Socio")
            self.stdout.write("3. Buscar Libro")
            self.stdout.write("4. Buscar Socio")
            self.stdout.write("5. Realizar Reserva")
            self.stdout.write("6. Retirar Libro Reservado")
            self.stdout.write("7. Devolver Libro")
            self.stdout.write("8. Editar Libro")
            self.stdout.write("9. Editar Socio")
            self.stdout.write("10. Eliminar Libro")
            self.stdout.write("11. Eliminar Socio")
            self.stdout.write("12. Listar reservas de un socio")
            self.stdout.write("13. Listar todas las reservas")
            self.stdout.write("0. Salir")

            opcion = input("Seleccione una opción: ").strip()

            if opcion == "0":
                self.stdout.write(self.style.SUCCESS("¡Hasta luego!"))
                break

            elif opcion == "1":
                self.stdout.write("\n--- REGISTRAR LIBRO ---")
                try:
                    titulo = input("Título: ").strip()
                    autor = input("Autor: ").strip()
                    isbn = input("ISBN: ").strip()
                    cant = input("Cantidad de ejemplares (por defecto 1): ").strip()
                    cantidad = int(cant) if cant.isdigit() else 1

                    libro = RegistrarLibroService.ejecutar(titulo, autor, isbn, cantidad)
                    self.stdout.write(self.style.SUCCESS(f"Libro '{libro.titulo}' registrado con éxito (ID #{libro.id})."))
                except ValidationError as e:
                    msg = e.message if hasattr(e, 'message') else str(e)
                    self.stdout.write(self.style.ERROR(f"Error: {msg}"))

            elif opcion == "2":
                self.stdout.write("\n--- REGISTRAR SOCIO ---")
                try:
                    nombre = input("Nombre: ").strip()
                    apellido = input("Apellido: ").strip()
                    dni = input("DNI: ").strip()

                    socio = RegistrarSocioService.ejecutar(nombre, apellido, dni)
                    self.stdout.write(self.style.SUCCESS(f"Socio '{socio.nombre_completo}' registrado con éxito (ID #{socio.id})."))
                except ValidationError as e:
                    msg = e.message if hasattr(e, 'message') else str(e)
                    self.stdout.write(self.style.ERROR(f"Error: {msg}"))

            elif opcion == "3":
                self.stdout.write("\n--- BUSCAR LIBROS ---")
                criterio = input("Ingrese título, autor o ISBN (deje vacío para listar todos): ").strip()
                libros = BuscarLibroService.ejecutar(criterio)

                if not libros.exists():
                    self.stdout.write(self.style.WARNING("No se encontraron libros."))
                else:
                    for l in libros:
                        self.stdout.write(f"- ID #{l.id} | '{l.titulo}' - {l.autor} | ISBN: {l.isbn} | Stock: {l.cantidad_total}")

            elif opcion == "4":
                self.stdout.write("\n--- BÚSQUEDA DE SOCIOS ---")
                busqueda = input("Ingrese nombre, apellido, DNI o ID de socio a buscar: ").strip()

                if not busqueda:
                    self.stdout.write(self.style.ERROR("El término de búsqueda no puede estar vacío."))
                    continue

                socios = BuscarSocioService.ejecutar(busqueda)

                if not socios.exists():
                    self.stdout.write(self.style.ERROR("No se encontraron socios que coincidan con la búsqueda."))
                else:
                    self.stdout.write(self.style.SUCCESS(f"\nSe encontraron {socios.count()} socio(s):"))
                    for socio in socios:
                        if hasattr(socio, 'get_estado_display'):
                            estado_texto = socio.get_estado_display()
                        elif hasattr(socio, 'activo'):
                            estado_texto = "Activo" if socio.activo else "Inactivo"
                        else:
                            estado_texto = getattr(socio, 'estado', 'N/A')

                        id_mostrar = getattr(socio, 'id_socio', socio.id)
                        email_mostrar = getattr(socio, 'email', None) or 'N/A'

                        self.stdout.write(
                            f"- Socio #{id_mostrar}: {socio.nombre_completo} | "
                            f"DNI: {socio.dni} | Email: {email_mostrar} | Estado: {estado_texto}"
                        )

            elif opcion == "5":
                self.stdout.write("\n--- REALIZAR RESERVA ---")
                try:
                    id_socio = input("ID de Socio: ").strip()
                    id_libro = input("ID de Libro: ").strip()

                    reserva = RealizarReservaService.ejecutar(id_socio, id_libro)
                    self.stdout.write(
                        self.style.SUCCESS(f"Reserva #{reserva.id} creada con éxito para {reserva.socio.nombre_completo}.")
                    )
                except ValidationError as e:
                    msg = e.message if hasattr(e, 'message') else str(e)
                    self.stdout.write(self.style.ERROR(f"Error: {msg}"))

            elif opcion == "6":
                self.stdout.write("\n--- RETIRAR LIBRO ---")
                try:
                    id_reserva = input("ID de Reserva a retirar: ").strip()

                    reserva = RetirarLibroService.ejecutar(id_reserva)
                    self.stdout.write(
                        self.style.SUCCESS(f"Libro '{reserva.libro.titulo}' marcado como RETIRADO por {reserva.socio.nombre_completo}.")
                    )
                except ValidationError as e:
                    msg = e.message if hasattr(e, 'message') else str(e)
                    self.stdout.write(self.style.ERROR(f"Error: {msg}"))

            elif opcion == "7":
                self.stdout.write("\n--- DEVOLVER LIBRO ---")
                try:
                    id_reserva = input("ID de Reserva a devolver: ").strip()

                    reserva = DevolverLibroService.ejecutar(id_reserva)
                    self.stdout.write(
                        self.style.SUCCESS(f"Libro '{reserva.libro.titulo}' devuelto por {reserva.socio.nombre_completo}.")
                    )
                except ValidationError as e:
                    msg = e.message if hasattr(e, 'message') else str(e)
                    self.stdout.write(self.style.ERROR(f"Error: {msg}"))

            elif opcion == "8":
                self.stdout.write("\n--- EDITAR LIBRO ---")
                try:
                    id_libro = input("ID del libro a editar: ").strip()
                    self.stdout.write("Ingrese los nuevos datos (presione ENTER para mantener el valor actual):")

                    titulo = input("Nuevo título: ").strip() or None
                    autor = input("Nuevo autor: ").strip() or None
                    isbn = input("Nuevo ISBN: ").strip() or None
                    cant_str = input("Nueva cantidad de ejemplares: ").strip()
                    cantidad = int(cant_str) if cant_str.isdigit() else None

                    libro = EditarLibroService.ejecutar(id_libro, titulo, autor, isbn, cantidad)
                    self.stdout.write(self.style.SUCCESS(f"Libro #{libro.id} actualizado con éxito."))
                except ValidationError as e:
                    msg = e.message if hasattr(e, 'message') else str(e)
                    self.stdout.write(self.style.ERROR(f"Error: {msg}"))

            elif opcion == "9":
                self.stdout.write("\n--- EDITAR SOCIO ---")
                try:
                    id_socio = input("ID del socio a editar: ").strip()
                    self.stdout.write("Ingrese los nuevos datos (presione ENTER para mantener el valor actual):")

                    nombre = input("Nuevo nombre: ").strip() or None
                    apellido = input("Nuevo apellido: ").strip() or None
                    dni = input("Nuevo DNI: ").strip() or None

                    socio = EditarSocioService.ejecutar(id_socio, nombre, apellido, dni)
                    self.stdout.write(self.style.SUCCESS(f"Socio '{socio.nombre_completo}' actualizado con éxito."))
                except ValidationError as e:
                    msg = e.message if hasattr(e, 'message') else str(e)
                    self.stdout.write(self.style.ERROR(f"Error: {msg}"))

            elif opcion == "10":
                self.stdout.write("\n--- ELIMINAR LIBRO ---")
                try:
                    id_libro = input("ID del libro a eliminar: ").strip()
                    confirmacion = input(f"¿Está seguro de eliminar el libro #{id_libro}? (s/n): ").strip().lower()

                    if confirmacion == 's':
                        titulo = EliminarLibroService.ejecutar(id_libro)
                        self.stdout.write(self.style.SUCCESS(f"Libro '{titulo}' eliminado correctamente."))
                    else:
                        self.stdout.write("Operación cancelada.")
                except ValidationError as e:
                    msg = e.message if hasattr(e, 'message') else str(e)
                    self.stdout.write(self.style.ERROR(f"Error: {msg}"))

            elif opcion == "11":
                self.stdout.write("\n--- ELIMINAR SOCIO ---")
                try:
                    id_socio = input("ID del socio a eliminar: ").strip()
                    confirmacion = input(f"¿Está seguro de eliminar al socio #{id_socio}? (s/n): ").strip().lower()

                    if confirmacion == 's':
                        nombre = EliminarSocioService.ejecutar(id_socio)
                        self.stdout.write(self.style.SUCCESS(f"Socio '{nombre}' eliminado correctamente."))
                    else:
                        self.stdout.write("Operación cancelada.")
                except ValidationError as e:
                    msg = e.message if hasattr(e, 'message') else str(e)
                    self.stdout.write(self.style.ERROR(f"Error: {msg}"))

            elif opcion == "12":
                self.stdout.write("\n--- RESERVAS POR SOCIO ---")
                try:
                    id_socio = input("ID del socio: ").strip()
                    reservas = ObtenerReservaSocioService.ejecutar(id_socio)

                    if not reservas.exists():
                        self.stdout.write(self.style.WARNING("El socio no tiene reservas registradas."))
                    else:
                        for r in reservas:
                            self.stdout.write(
                                f"- Reserva #{r.id} | Libro: '{r.libro.titulo}' | Estado: {r.estado}"
                            )
                except ValidationError as e:
                    msg = e.message if hasattr(e, 'message') else str(e)
                    self.stdout.write(self.style.ERROR(f"Error: {msg}"))

            elif opcion == "13":
                self.stdout.write("\n--- TODAS LAS RESERVAS ---")
                estado = input("Filtrar por estado (ACTIVO, RETIRADO, DEVUELTO) o presione ENTER para ver todas: ").strip()
                reservas = ObtenerReservaTotalService.ejecutar(estado or None)

                if not reservas.exists():
                    self.stdout.write(self.style.WARNING("No se encontraron reservas."))
                else:
                    for r in reservas:
                        self.stdout.write(
                            f"- Reserva #{r.id} | Socio: {r.socio.nombre_completo} | Libro: '{r.libro.titulo}' | Estado: {r.estado}"
                        )

            else:
                self.stdout.write(self.style.ERROR("Opción no válida. Por favor, intente nuevamente."))
                