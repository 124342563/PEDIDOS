from app.models import Entrega


def calcular_estado_despacho(pedido):
    entregas = Entrega.query.filter_by(id_pedido=pedido.id_pedido).all()
    if not entregas:
        return "PENDIENTE"
    total = pedido.cantidad_total or len(entregas)
    despachadas = sum(
        e.cantidad for e in entregas
        if e.estado_entrega in ("ENTREGADO", "EN RUTA", "PROGRAMADO")
    )
    if despachadas == 0:
        return "PENDIENTE"
    if despachadas < total:
        return "PARCIAL"
    return "COMPLETO"


ESTADOS_PRODUCCION_MAP = {
    "PENDIENTE": "secondary",
    "EN PRODUCCIÓN": "warning",
    "PRODUCIDO": "info",
    "LISTO PARA DESPACHO": "success",
}

ESTADOS_DESPACHO_MAP = {
    "PENDIENTE": "secondary",
    "PROGRAMADO": "primary",
    "EN RUTA": "warning",
    "PARCIAL": "info",
    "ENTREGADO": "success",
    "NO ENTREGADO": "danger",
    "NOVEDAD": "danger",
    "COMPLETO": "success",
}

ESTADOS_ENTREGA_MAP = {
    "PENDIENTE": "secondary",
    "PROGRAMADO": "primary",
    "EN RUTA": "warning",
    "ENTREGADO": "success",
    "NO ENTREGADO": "danger",
    "NOVEDAD": "danger",
    "REPROGRAMADO": "info",
    "REQUIERE ACTUALIZAR TRANSPORTADORA": "warning",
}


def badge_produccion(estado):
    return ESTADOS_PRODUCCION_MAP.get(estado, "secondary")


def badge_despacho(estado):
    return ESTADOS_DESPACHO_MAP.get(estado, "secondary")


def badge_entrega(estado):
    return ESTADOS_ENTREGA_MAP.get(estado, "secondary")
