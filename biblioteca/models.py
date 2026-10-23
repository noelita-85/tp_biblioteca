#capa de dominio:Define la estructura de las entidades y encapsula el comportamiento propio de cada objeto
from django .db import models
from django.core.exceptions import ValidationError
from django.db import models
from django.db import transaction
from datetime import timedelta
from django.utils import timezone
DIAS_INACTIVIDAD_SOCIO = 45

class SocioEstado(models.TextChoices):
    ACTIVO = 'ACT', 'Activo'
    INACTIVO = 'INA', 'Inactivo'
    
class ReservaEstado(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    RETIRADA = 'RETIRADA', 'Retirada'
    CANCELADA = 'CANCELADA', 'Cancelada'
    FINALIZADA = 'FINALIZADA', 'Finalizada' 
        
# Enumerador
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

class Libro(models.Model):
    isbn = models.CharField(max_length=13, unique=True)
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=150)
    editorial = models.CharField(max_length=100, blank=True)
    anio_publicacion = models.IntegerField(null=False)
    cantidad_total = models.PositiveIntegerField(default=1)
    cantidad_disponible = models.PositiveIntegerField(default=1)
    categoria = models.CharField(max_length=10,
        choices=CategoriaLibro.choices,
        default=CategoriaLibro.OTRO  # Le damos un valor por defecto para los libros que ya creaste
    )

    def __str__(self):
        return f"{self.titulo} - {self.autor} ({self.get_categoria_display()} - {self.editorial})"

    # ... (deja los métodos esta_disponible, reservar_ejemplar y liberar_ejemplar igual que antes)

    def esta_disponible(self):
        return self.cantidad_disponible > 0

    def reservar_ejemplar(self):
        if not self.esta_disponible():
            raise ValidationError("No hay ejemplares disponibles.")
        
        self.cantidad_disponible -= 1
        self.save(update_fields=["cantidad_disponible"])
       

    def liberar_ejemplar(self):
        if self.cantidad_disponible >= self.cantidad_total:
            raise ValidationError(
                "La cantidad disponible ya alcanzó la cantidad total."
            )

        self.cantidad_disponible += 1
        self.save(update_fields=["cantidad_disponible"])
        
class Persona(models.Model):
    
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=8, unique=True)
    email = models.EmailField(blank=True, null=True)
            
    class Meta:
        abstract = True  # Indica a Django que no cree una tabla 'Persona' en la BD

    def __str__(self):
        return f"{self.nombre} {self.apellido} (DNI: {self.id_socio})"    
    
class Socio(Persona):
    id_socio = models.IntegerField(unique=True)
    activo = models.BooleanField(default=True)
    ultima_actividad = models.DateTimeField(default=timezone.now)

    def actualizar_estado_actividad(self):
        fecha_limite = timezone.now() - timedelta(
        days=DIAS_INACTIVIDAD_SOCIO
    )

        if self.activo and self.ultima_actividad <= fecha_limite:
            self.activo = False
        self.save(update_fields=["activo"])

        return self.activo

    def actualizar_estado_actividad(self):
        return self.activo
    def __str__(self):
        return f"{self.nombre} {self.apellido} (Socio #{self.id_socio})"
   
    def registrar_actividad(self):
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
            f"por {self.socio.nombre} {self.socio.apellido} "
            f"| Estado: {self.get_estado_display()} | Fecha: {fecha_str}"
        )
       