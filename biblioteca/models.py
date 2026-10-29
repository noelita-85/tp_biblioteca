#capa de dominio:Define la estructura de las entidades y encapsula el comportamiento propio de cada objeto
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# Constantes del módulo
DIAS_INACTIVIDAD_SOCIO = 45


# --- ENUMERADORES / CHOICES ---

class SocioEstado(models.TextChoices):
    ACTIVO = 'ACT', 'Activo'
    INACTIVO = 'INA', 'Inactivo'


class ReservaEstado(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    RETIRADA = 'RETIRADA', 'Retirada'
    CANCELADA = 'CANCELADA', 'Cancelada'
    FINALIZADA = 'FINALIZADA', 'Finalizada'


class CategoriaLibro(models.TextChoices):
    INFANTIL = 'INF', 'Infantil'
    ACCION = 'ACC', 'Acción'
    DRAMA = 'DRA', 'Drama'
    NOVELA = 'NOV', 'Novela'
    CIENCIA_FICCION = 'CIFI', 'Ciencia Ficción'
    TERROR = 'TER', 'Terror'
    THRILLER = 'THR', 'Thriller'
    AVENTURA = 'AVE', 'Aventura'
    OTRO = 'OTR', 'Otro'


# --- MODELOS ---

class Libro(models.Model):
    isbn = models.CharField(max_length=13, unique=True)
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=150)
    editorial = models.CharField(max_length=100, blank=True)
    anio_publicacion = models.IntegerField(default = 2024)
    cantidad_total = models.PositiveIntegerField(default=1)
    cantidad_disponible = models.PositiveIntegerField(default=1)
    categoria = models.CharField(
        max_length=10,
        choices=CategoriaLibro.choices,
        default=CategoriaLibro.OTRO
    )

    def __str__(self):
        return f"{self.titulo} - {self.autor} ({self.get_categoria_display()})"

    @property
    def esta_disponible(self):
        """Propiedad calculada: devuelve True si hay al menos un ejemplar libre."""
        return self.cantidad_disponible > 0

    def reservar_ejemplar(self):
        """Descuenta un ejemplar del stock si está disponible."""
        if not self.esta_disponible:  # Se accede como propiedad, sin paréntesis
            raise ValidationError("No hay ejemplares disponibles.")

        self.cantidad_disponible -= 1
        self.save(update_fields=["cantidad_disponible"])

    def liberar_ejemplar(self):
        """Aumenta un ejemplar al stock disponible."""
        if self.cantidad_disponible >= self.cantidad_total:
            raise ValidationError("La cantidad disponible ya alcanzó la cantidad total.")

        self.cantidad_disponible += 1
        self.save(update_fields=["cantidad_disponible"])


class Persona(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)

    class Meta:
        abstract = True  # No genera tabla en la base de datos

    @property
    def nombre_completo(self):
        """Propiedad calculada disponible para Persona y todas sus subclases."""
        return f"{self.nombre} {self.apellido}"


class Socio(Persona):
    dni = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    es_activo = models.BooleanField(default=True)
    ultima_actividad = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.nombre_completo} (DNI: {self.dni})"

    @property
    def esta_inactivo(self):
        """Propiedad calculada: evalúa si superó el tiempo máximo de inactividad."""
        fecha_limite = timezone.now() - timedelta(days=DIAS_INACTIVIDAD_SOCIO)
        return self.ultima_actividad <= fecha_limite

    def actualizar_estado_actividad(self):
        """Actualiza el estado 'es_activo' en la BD si superó la inactividad permitida."""
        if self.es_activo and self.esta_inactivo:
            self.es_activo = False
            self.save(update_fields=["es_activo"])
        return self.es_activo

    def registrar_actividad(self):
        """Actualiza la fecha de última actividad al momento actual."""
        self.ultima_actividad = timezone.now()
        self.save(update_fields=["ultima_actividad"])


class Reserva(models.Model):
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    fecha_reserva = models.DateTimeField(default=timezone.now)
    estado = models.CharField(
        max_length=20,
        choices=ReservaEstado.choices,
        default=ReservaEstado.PENDIENTE
    )

    def __str__(self) -> str:
        fecha_str = self.fecha_reserva.strftime("%d/%m/%Y %H:%M") if self.fecha_reserva else "Sin fecha"
        cat = self.libro.get_categoria_display()
        return (
            f"Reserva #{self.id}: '{self.libro.titulo}' [{cat}] "
            f"por {self.socio.nombre_completo} "
            f"| Estado: {self.get_estado_display()} | Fecha: {fecha_str}"
        )