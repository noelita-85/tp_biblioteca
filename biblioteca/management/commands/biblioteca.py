#"la interacción con el usuario:mostrar opciones,capturar entradas por teclado y formatear la salida""
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from biblioteca.models import Libro, Socio, Reserva, CategoriaLibro
from django.db.models import Q
from biblioteca.services import (
    registrar_libro,
    realizar_reserva,
    editar_libro,
    eliminar_libro,
    retirar_libro,
    devolver_libro,
    editar_socio,
    eliminar_socio,
    obtener_reservas_por_socio,
    obtener_todas_las_reservas,
)

class Command(BaseCommand):
    help = "Inicia el sistema interactivo de reserva de libros"

    def handle(self, *args, **options):
        while True:
            self.stdout.write("\n=== SISTEMA DE GESTIÓN DE BIBLIOTECA ===")
            self.stdout.write("1. Registrar Socio")
            self.stdout.write("2. Registrar Libro")
            self.stdout.write("3. Buscar Libro")   
            self.stdout.write("4. Buscar Socio")
            self.stdout.write("5. Realizar Reserva")
            self.stdout.write("6. Retirar Libro Reservado")
            self.stdout.write("7. Devolver Libro")
            self.stdout.write("8. Editar Libro")
            self.stdout.write("9. Eliminar Libro")
            self.stdout.write("10. Editar Socio")
            self.stdout.write("11. Eliminar Socio")
            self.stdout.write("12. Listar reservas de un socio")
            self.stdout.write("13. Listar todas las reservas")
            self.stdout.write("0. Salir")
            
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                # Agregar socio con confirmación repetida
                mientras_agrega = True
                while mientras_agrega:
                    try:
                        nombre = input("Nombre: ").strip()
                        apellido = input("Apellido: ").strip()
                        dni = input("DNI: ").strip()
                        email = input("Email: ").strip()
                        id_socio = int(input("Número de socio: "))

                        Socio.objects.create(
                            nombre=nombre,
                            apellido=apellido,
                            dni=dni,
                            email=email,
                            id_socio=id_socio
                        )
                        self.stdout.write(self.style.SUCCESS(f"Socio '{nombre} {apellido}' registrado con éxito."))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error al registrar socio: {e}"))

                    resp = input("\n¿Desea agregar otro socio? (s/n): ").strip().lower()
                    if resp != 's':
                        mientras_agrega = False
            elif opcion == "2":
                self.stdout.write("\n--- REGISTRAR LIBRO ---")
                titulo = input("Título: ").strip()
                autor = input("Autor: ").strip()
                isbn = input("ISBN: ").strip()
                editorial = input("Editorial: ").strip()
                anio_str = input("Año de publicación: ").strip()

                if not titulo or not autor or not isbn:
                    self.stdout.write(self.style.ERROR("Título, Autor e ISBN son campos obligatorios."))
                    continue

                self.stdout.write("\nCategorías disponibles:")
                self.stdout.write(" 1. Infantil\n 2. Acción\n 3. Drama\n 4. Novela\n 5. CI-FI\n 6. Terror\n 7. Thriller\n 8. Aventura\n 9. Otro")
                cat_opcion = input("Seleccione categoría (1-9) [1 por defecto]: ").strip()

                map_cat = {
                    "1": CategoriaLibro.INFANTIL,
                    "2": CategoriaLibro.ACCION,
                    "3": CategoriaLibro.DRAMA,
                    "4": CategoriaLibro.NOVELA,
                    "5": CategoriaLibro.CIENCIA_FICCION,
                    "6": CategoriaLibro.TERROR,
                    "7": CategoriaLibro.THRILLER,
                    "8": CategoriaLibro.AVENTURA,
                    "9": CategoriaLibro.OTRO,
                }
                categoria_sel = map_cat.get(cat_opcion, CategoriaLibro.INFANTIL)

                try:
                    cant_str = input("Cantidad de ejemplares: ").strip()
                    cant = int(cant_str) if cant_str else 1
                    anio_pub = int(anio_str) if anio_str else 2024
                    
                    
                    libro = registrar_libro(
                        titulo, 
                        autor, 
                        isbn, 
                        editorial, 
                        cant, 
                        categoria=categoria_sel, 
                        anio_publicacion=anio_pub
                    )
                    self.stdout.write(self.style.SUCCESS(f"Libro '{libro.titulo}' registrado con éxito en categoría [{libro.get_categoria_display()}]."))
                except ValidationError as e:
                    self.stdout.write(self.style.ERROR(f"Error de validación: {e.message if hasattr(e, 'message') else e}"))
                except ValueError:
                    self.stdout.write(self.style.ERROR("La cantidad y el año deben ser números enteros válidos."))
            elif opcion == "3":
                self.stdout.write("\n--- BÚSQUEDA DE LIBROS ---")
                busqueda = input("Ingrese título, autor o ISBN a buscar: ").strip()

                if not busqueda:
                    self.stdout.write(self.style.ERROR("El término de búsqueda no puede estar vacío."))
                    continue

                filtro = Q(titulo__icontains=busqueda) | Q(autor__icontains=busqueda) | Q(isbn__icontains=busqueda)
                libros = Libro.objects.filter(filtro)

                if not libros.exists():
                    self.stdout.write(self.style.ERROR("No se encontraron libros que coincidan con la búsqueda."))
                else:
                    self.stdout.write(self.style.SUCCESS(f"\nSe encontraron {libros.count()} libro(s):"))
                    for libro in libros:
                        disponibilidad = "Disponible" if libro.esta_disponible() else "Agotado"
                        self.stdout.write(
                            f"- '{libro.titulo}' por {libro.autor} | ISBN: {libro.isbn} | "
                            f"Editorial: {libro.editorial} | Disponibles: {libro.cantidad_disponible}/{libro.cantidad_total} ({disponibilidad})"
                        )

            elif opcion == "4":
                self.stdout.write("\n--- BÚSQUEDA DE SOCIOS ---")
                busqueda = input("Ingrese nombre, apellido, DNI o ID de socio a buscar: ").strip()

                if not busqueda:
                    self.stdout.write(self.style.ERROR("El término de búsqueda no puede estar vacío."))
                    continue

                filtro = Q(nombre__icontains=busqueda) | Q(apellido__icontains=busqueda) | Q(dni__icontains=busqueda)
                if busqueda.isdigit():
                    filtro |= Q(id_socio=int(busqueda))

                socios = Socio.objects.filter(filtro)

                if not socios.exists():
                    self.stdout.write(self.style.ERROR("No se encontraron socios que coincidan con la búsqueda."))
                else:
                    self.stdout.write(self.style.SUCCESS(f"\nSe encontraron {socios.count()} socio(s):"))
                    for socio in socios:
                        # Evaluamos el estado según la estructura de tu modelo Socio
                        if hasattr(socio, 'get_estado_display'):
                            estado_texto = socio.get_estado_display()
                        elif hasattr(socio, 'activo'):
                            estado_texto = "Activo" if socio.activo else "Inactivo"
                        else:
                            estado_texto = getattr(socio, 'estado', 'N/A')

                        self.stdout.write(
                            f"- Socio #{socio.id_socio}: {socio.nombre} {socio.apellido} | "
                            f"DNI: {socio.dni} | Email: {socio.email or 'N/A'} | Estado: {estado_texto}"
                        )
            elif opcion == "5":
                self.stdout.write("\n--- REALIZAR RESERVA ---")
                try:
                    id_socio_input = input("Número de Socio (ID): ").strip()
                    if not id_socio_input.isdigit():
                        self.stdout.write(self.style.ERROR("El ID de socio debe ser un número entero válido."))
                        continue

                    id_socio = int(id_socio_input)

                    busqueda = input("Ingrese el nombre del libro o autor a buscar: ").strip()
                    if not busqueda:
                        self.stdout.write(self.style.ERROR("El término de búsqueda no puede estar vacío."))
                        continue

                    # Búsqueda flexible por título o autor mediante Q objects
                    libros_encontrados = list(
                        Libro.objects.filter(
                            Q(titulo__icontains=busqueda) | Q(autor__icontains=busqueda)
                        )
                    )

                    if not libros_encontrados:
                        self.stdout.write(self.style.ERROR("No se encontraron libros con ese criterio."))
                        continue

                   
                    self.stdout.write("\nLibros encontrados:")
                    for idx, libro in enumerate(libros_encontrados, start=1):
                        disponible = "Disponible" if libro.esta_disponible() else "Agotado"
                        self.stdout.write(
                            f"Opción {idx} [ID #{libro.id}]: '{libro.titulo}' | Categoría: {libro.get_categoria_display()} | "
                            f"Año: {libro.anio_publicacion} | Editorial: {libro.editorial} | "
                            f"Estado: {disponible} (ISBN: {libro.isbn})"
                        )
                    opc_input = input("\nSeleccione el número de libro a reservar (0 para cancelar): ").strip()
                    if not opc_input.isdigit():
                        self.stdout.write(self.style.ERROR("Debe ingresar un número entero válido."))
                        continue

                    opc_libro = int(opc_input)

                    if opc_libro == 0:
                        self.stdout.write("Reserva cancelada.")
                    elif 1 <= opc_libro <= len(libros_encontrados):
                        libro_seleccionado = libros_encontrados[opc_libro - 1]

                        # Llamada a la capa de servicios con id_socio e ISBN
                        reserva = realizar_reserva(id_socio, libro_seleccionado.isbn)
                        self.stdout.write(
                            self.style.SUCCESS(f"¡Reserva realizada con éxito! Nro de Reserva: #{reserva.id}")
                        )
                    else:
                        self.stdout.write(self.style.ERROR("Opción fuera de rango. Intente nuevamente."))

                except ValidationError as e:
                    msg = e.message if hasattr(e, 'message') else str(e)
                    self.stdout.write(self.style.ERROR(f"Error de negocio: {msg}"))
                except ValueError:
                    self.stdout.write(self.style.ERROR("Error: Ingrese un valor numérico válido."))
            elif opcion == "6":
                try:
                    id_reserva = int(input("ID de Reserva a retirar: "))
                    reserva = retirar_libro(id_reserva)
                    self.stdout.write(self.style.SUCCESS(f"Reserva #{reserva.id} retirada con éxito."))
                except ValidationError as e:
                    self.stdout.write(self.style.ERROR(f"Error: {e.message}"))

            elif opcion == "7":
                try:
                    id_reserva = int(input("ID de Reserva a devolver: "))
                    reserva = devolver_libro(id_reserva)
                    self.stdout.write(self.style.SUCCESS(f"Reserva #{reserva.id} devuelta con éxito."))
                except ValidationError as e:
                    self.stdout.write(self.style.ERROR(f"Error: {e.message}"))

            elif opcion == "8":
                try:
                    isbn = input("ISBN del libro a editar: ")
                    titulo = input("Nuevo título (dejar en blanco para mantener): ").strip() or None
                    autor = input("Nuevo autor (dejar en blanco para mantener): ").strip() or None
                    cant_str = input("Nueva cantidad total (dejar en blanco para mantener): ").strip()
                    cantidad = int(cant_str) if cant_str else None

                    editar_libro(isbn, nuevo_titulo=titulo, nuevo_autor=autor, nueva_cantidad_total=cantidad)
                    self.stdout.write(self.style.SUCCESS("Libro actualizado con éxito."))
                except ValidationError as e:
                    self.stdout.write(self.style.ERROR(f"Error: {e.message}"))

            elif opcion == "9":
                try:
                    isbn = input("ISBN del libro a eliminar: ")
                    eliminar_libro(isbn)
                    self.stdout.write(self.style.SUCCESS("Libro eliminado con éxito."))
                except ValidationError as e:
                    self.stdout.write(self.style.ERROR(f"Error: {e.message}"))

            elif opcion == "10":
                try:
                    id_socio = int(input("Número de socio a editar: "))
                    nombre = input("Nuevo nombre (dejar en blanco para mantener): ").strip() or None
                    apellido = input("Nuevo apellido (dejar en blanco para mantener): ").strip() or None
                    dni = input("Nuevo DNI (dejar en blanco para mantener): ").strip() or None
                    email = input("Nuevo email (dejar en blanco para mantener): ").strip() or None
                    editar_socio(id_socio, nuevo_nombre=nombre, nuevo_apellido=apellido, nuevo_dni=dni, nuevo_email=email      )
                    self.stdout.write(self.style.SUCCESS("Socio actualizado con éxito."))
                except ValidationError as e:
                    self.stdout.write(self.style.ERROR(f"Error: {e.message}"))

            elif opcion == "11": 
                try:
                    id_socio = int(input("Número de socio a eliminar: "))
                    eliminar_socio(id_socio)
                    self.stdout.write(self.style.SUCCESS("Socio eliminado con éxito."))
                except ValidationError as e:
                    self.stdout.write(self.style.ERROR(f"Error: {e.message}"))
  
            elif opcion == "12":
                self.stdout.write("\n--- RESERVAS DE UN SOCIO ---")
                try:
                    id_socio = int(input("Ingrese el ID del socio: ").strip())
                    reservas = obtener_reservas_por_socio(id_socio)

                    if not reservas.exists():
                        self.stdout.write(self.style.WARNING("El socio no tiene reservas registradas."))
                    else:
                        self.stdout.write(self.style.SUCCESS(f"\nSe encontraron {reservas.count()} reserva(s):"))
                        for r in reservas:
                            cat_libro = r.libro.get_categoria_display()
                            self.stdout.write(
                                f"- Reserva #{r.id}: '{r.libro.titulo}' (Categoría: {cat_libro}) "
                                f"| Estado: {r.get_estado_display()}"
                            )
                except ValueError:
                    self.stdout.write(self.style.ERROR("El ID de socio debe ser un número entero."))
                except ValidationError as e:
                    self.stdout.write(self.style.ERROR(f"Error: {e.message if hasattr(e, 'message') else e}"))

            elif opcion == "13":
                self.stdout.write("\n--- TODAS LAS RESERVAS DEL SISTEMA ---")
                reservas = obtener_todas_las_reservas()

                if not reservas.exists():
                    self.stdout.write(self.style.WARNING("No hay reservas registradas en el sistema."))
                else:
                    self.stdout.write(self.style.SUCCESS(f"\nTotal de reservas: {reservas.count()}"))
                    for r in reservas:
                        cat_libro = r.libro.get_categoria_display()
                        self.stdout.write(
                            f"- Reserva #{r.id}: '{r.libro.titulo}' (Categoría: {cat_libro}) "
                            f"| Socio: {r.socio.nombre} {r.socio.apellido} (ID #{r.socio.id_socio}) "
                            f"| Estado: {r.get_estado_display()}"
                        )

            elif opcion == "0":
                self.stdout.write("Saliendo del sistema...")
                break
            else:
                self.stdout.write(self.style.ERROR("Opción no válida. Intente nuevamente."))
                
            