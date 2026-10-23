#logica de negocios
from django.core.exceptions import ValidationError
from django.db import transaction
from biblioteca.models import Libro, Socio, Reserva,CategoriaLibro



def registrar_libro(
    titulo: str, 
    autor: str, 
    isbn: str, 
    editorial: str, 
    cantidad_total: int, 
    categoria: str = CategoriaLibro.INFANTIL,
    anio_publicacion: int = None
):
    if not titulo or not autor or not isbn:
        raise ValidationError("El título, autor e ISBN son obligatorios.")

    if cantidad_total <= 0:
        raise ValidationError("La cantidad de ejemplares debe ser mayor a cero.")

    if Libro.objects.filter(isbn=isbn).exists():
        raise ValidationError(f"Ya existe un libro registrado con el ISBN '{isbn}'.")

    libro = Libro.objects.create(
        titulo=titulo,
        autor=autor,
        isbn=isbn,
        editorial=editorial,
        categoria=categoria,
        cantidad_total=cantidad_total,
        cantidad_disponible=cantidad_total,
        anio_publicacion=anio_publicacion
    )
    return libro
def realizar_reserva(id_socio, isbn):
    # 1. Buscar al socio.
    try:
        socio = Socio.objects.get(id_socio=id_socio)
    except Socio.DoesNotExist:
        raise ValidationError("Socio no encontrado.")

    # 2. Actualizar y comprobar el estado del socio.
    if not socio.actualizar_estado_actividad():
        raise ValidationError(
            "El socio está inactivo o lleva 45 días sin actividad."
        )

    # 3. Realizar la reserva dentro de una transacción.
    with transaction.atomic():
        try:
            libro = Libro.objects.select_for_update().get(isbn=isbn)
        except Libro.DoesNotExist:
            raise ValidationError("Libro no encontrado.")
        # select_for_update() bloquea la fila del libro para evitar condiciones de carrera, evita que 2 socios reserven el mismo libro
        # 4. Evitar reservas activas duplicadas.
        reserva_existente = Reserva.objects.filter(
            socio=socio,
            libro=libro,
            estado__in=["PENDIENTE", "RETIRADA"],
        ).exists()

        if reserva_existente:
            raise ValidationError(
                "El socio ya tiene una reserva activa de este libro."
            )

        # 5. Descontar un ejemplar disponible.
        libro.reservar_ejemplar()

        # 6. Crear la reserva.
        reserva = Reserva.objects.create(
            socio=socio,
            libro=libro,
            estado="PENDIENTE",
        )

        # 7. Registrar la actividad exitosa.
        socio.registrar_actividad()

        return reserva
       

def editar_libro(isbn, nuevo_titulo=None, nuevo_autor=None, nueva_cantidad_total=None, nueva_categoria=None):
    """
    Actualiza los datos de un libro existente.
    Si se modifica la cantidad total, recalcula proporcionalmente los ejemplares disponibles.
    """
    try:
        libro = Libro.objects.get(isbn=isbn)
    except Libro.DoesNotExist:
        raise ValidationError("No existe ningún libro registrado con ese ISBN.")

    if nuevo_titulo:
        libro.titulo = nuevo_titulo
    if nuevo_autor:
        libro.autor = nuevo_autor
    if nueva_categoria:
        libro.categoria = nueva_categoria

    if nueva_cantidad_total is not None:
        if nueva_cantidad_total < 0:
            raise ValidationError("La cantidad total no puede ser negativa.")
        
        diferencia = nueva_cantidad_total - libro.cantidad_total
        ejemplares_disponibles = libro.cantidad_disponible + diferencia
        
        if ejemplares_disponibles < 0:
            raise ValidationError("No hay suficientes ejemplares disponibles.")
        
        libro.cantidad_total = nueva_cantidad_total
        libro.cantidad_disponible = ejemplares_disponibles

    libro.save()
    return libro


def eliminar_libro(isbn):
    """
    Elimina un libro de la base de datos si no tiene reservas activas.
    """
    try:
        libro = Libro.objects.get(isbn=isbn)
    except Libro.DoesNotExist:
        raise ValidationError("No existe ningún libro registrado con ese ISBN.")

    # Regla de negocio: Verificar si existen reservas activas (PENDIENTE o RETIRADA)
    if Reserva.objects.filter(libro=libro, estado__in=["PENDIENTE", "RETIRADA"]).exists():
        raise ValidationError("No se puede eliminar el libro porque tiene reservas activas.")

    libro.delete()
    return True


def retirar_libro(id_reserva):
    with transaction.atomic():
        # 1. Buscar y bloquear la reserva.
        try:
            reserva = Reserva.objects.select_for_update().get(
                pk=id_reserva
            )
        except Reserva.DoesNotExist:
            raise ValidationError(
                "No se encontró ninguna reserva con ese ID."
            )

        # 2. Solo se pueden retirar reservas pendientes.
        if reserva.estado != "PENDIENTE":
            raise ValidationError(
                "Solo se pueden retirar reservas pendientes."
            )

        # 3. Cambiar el estado de la reserva.
        reserva.estado = "RETIRADA"
        reserva.save(update_fields=["estado"])
        
        reserva.socio.registrar_actividad()

        # 4. Devolver la reserva actualizada.
        return reserva


def devolver_libro(id_reserva):
    with transaction.atomic():
        # 1. Buscar y bloquear la reserva.
        try:
            reserva = Reserva.objects.select_for_update().get(
                pk=id_reserva
            )
        except Reserva.DoesNotExist:
            raise ValidationError(
                "No se encontró ninguna reserva con ese ID."
            )

        # 2. Verificar que el libro haya sido retirado.
        if reserva.estado != "RETIRADA":
            raise ValidationError(
                "Solo se pueden devolver reservas que estén retiradas."
            )

        # 3. Buscar y bloquear el libro relacionado.
        try:
            libro = Libro.objects.select_for_update().get(
                pk=reserva.libro_id
            )
        except Libro.DoesNotExist:
            raise ValidationError(
                "No se encontró el libro asociado a la reserva."
            )

        # 4. Liberar el ejemplar.
        libro.liberar_ejemplar()

        # 5. Marcar la reserva como finalizada.
        reserva.estado = "FINALIZADA"
        reserva.save(update_fields=["estado"])

        # 6. Devolver la reserva actualizada.
        return reserva
    
def editar_socio(id_socio, nuevo_nombre=None, nuevo_apellido=None, nuevo_dni=None, nuevo_email=None, activo=None):
    """
    Actualiza los datos personales o el estado de un socio.
    """
    try:
        socio = Socio.objects.get(id_socio=id_socio)
    except Socio.DoesNotExist:
        raise ValidationError("No existe ningún socio registrado con ese número.")

    if nuevo_nombre:
        socio.nombre = nuevo_nombre
    if nuevo_apellido:
        socio.apellido = nuevo_apellido
    if nuevo_dni:
        socio.dni = nuevo_dni
    if nuevo_email:
        socio.email = nuevo_email    
    if activo is not None:
        socio.activo = activo

    socio.save()
    return socio


def eliminar_socio(id_socio):
    """
    Elimina un socio si no tiene reservas activas (PENDIENTE o RETIRADA).
    """
    try:
        socio = Socio.objects.get(id_socio=id_socio)
    except Socio.DoesNotExist:
        raise ValidationError("No existe ningún socio registrado con ese número.")

    if Reserva.objects.filter(socio=socio, estado__in=["PENDIENTE", "RETIRADA"]).exists():
        raise ValidationError("No se puede eliminar el socio porque tiene reservas activas o préstamos pendientes.")

    socio.delete()
    return True
def obtener_reservas_por_socio(id_socio):
    """
    Retorna el listado de reservas asociadas a un socio específico.
    """
    try:
        socio = Socio.objects.get(id_socio=id_socio)
    except Socio.DoesNotExist:
        raise ValidationError("No existe ningún socio registrado con ese número.")

    return Reserva.objects.filter(socio=socio).order_by('-id')


def obtener_todas_las_reservas():
    return Reserva.objects.select_related('libro', 'socio').all().order_by('-id')   