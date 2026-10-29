
from biblioteca.models import Reserva


class ObtenerReservaTotalService:

    @classmethod
    def ejecutar(cls, estado=None):
        """Obtiene el listado completo de reservas, opcionalmente filtradas por estado."""
        queryset = Reserva.objects.select_related('libro', 'socio').all()

        if estado and cls.es_estado_valido(estado):
            queryset = queryset.filter(estado=estado.upper().strip())

        return queryset

    @staticmethod
    def es_estado_valido(estado):
        """Valida si el estado enviado está dentro de los permitidos."""
        estados_validos = ['PENDIENTE', 'RETIRADA', 'CANCELADA', 'FINALIZADA', 'ACTIVO', 'RETIRADO', 'DEVUELTO']
        return str(estado).upper().strip() in estados_validos    