from app.models import Pedido, Entrega
from app.extensions import db


def generar_reporte_pedido(pedido):
    entregas = Entrega.query.filter_by(id_pedido=pedido.id_pedido).all()
    entregadas = sum(1 for e in entregas if e.estado_entrega == "ENTREGADO")
    novedades = sum(1 for e in entregas if e.estado_entrega == "NOVEDAD")
    return {
        "pedido": pedido.numero_pedido,
        "cliente": pedido.cliente.nombre if pedido.cliente else "",
        "producto": pedido.producto_principal,
        "cantidad_total": pedido.cantidad_total,
        "total_entregas": len(entregas),
        "entregadas": entregadas,
        "novedades": novedades,
        "pendientes": len(entregas) - entregadas - novedades,
    }
