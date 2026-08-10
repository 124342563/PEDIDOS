from app.models import Entrega


def calcular_estado_despacho(pedido):
    entregas = Entrega.query.filter_by(id_pedido=pedido.id_pedido).all()
    if not entregas:
        return "PENDIENTE"
    total = entregas
    estados = [e.estado_entrega for e in entregas]
    if all(e == "ENTREGADO" for e in estados):
        return "COMPLETO"
    if any(e in ("NO ENTREGADO", "NOVEDAD") for e in estados):
        if any(e == "ENTREGADO" for e in estados):
            return "PARCIAL"
        return "NOVEDAD"
    if any(e == "EN RUTA" for e in estados):
        return "EN RUTA"
    if any(e == "PROGRAMADO" for e in estados):
        return "PROGRAMADO"
    if any(e == "ENTREGADO" for e in estados):
        return "PARCIAL"
    return "PENDIENTE"


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
