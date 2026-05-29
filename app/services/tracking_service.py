from app.models import TrackingEvento
from app.extensions import db
from datetime import datetime


def registrar_evento(id_pedido=None, id_entrega=None, id_despacho=None,
                     estado_anterior=None, estado_nuevo=None,
                     descripcion=None, usuario="sistema", origen="SISTEMA"):
    evento = TrackingEvento(
        id_pedido=id_pedido,
        id_entrega=id_entrega,
        id_despacho=id_despacho,
        estado_anterior=estado_anterior,
        estado_nuevo=estado_nuevo,
        descripcion=descripcion,
        usuario=usuario,
        origen=origen,
        fecha_evento=datetime.utcnow(),
    )
    db.session.add(evento)
    return evento


ESTADOS_ECOMMERCE = [
    "PEDIDO_RECIBIDO",
    "EN_PRODUCCION",
    "LISTO_PARA_DESPACHO",
    "PROGRAMADO",
    "GUIA_GENERADA",
    "EN_RUTA",
    "EN_REPARTO",
    "ENTREGADO",
    "NOVEDAD",
    "REPROGRAMADO",
    "COMPLETO",
]
