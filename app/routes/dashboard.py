from datetime import date
from flask import Blueprint, render_template
from app.extensions import db
from app.models import Pedido, Entrega, Despacho

bp = Blueprint("dashboard", __name__)


@bp.route("/")
def index():
    today = date.today()

    pedidos_hoy = Pedido.query.filter(Pedido.fecha_entrega_general == today).count()
    entregas_hoy = Entrega.query.filter(Entrega.fecha_entrega == today).count()
    en_produccion = Pedido.query.filter(Pedido.estado_produccion == "EN PRODUCCIÓN").count()
    listos_despacho = Pedido.query.filter(Pedido.estado_produccion == "LISTO PARA DESPACHO").count()
    en_ruta = Entrega.query.filter(Entrega.estado_entrega == "EN RUTA").count()
    entregados = Entrega.query.filter(Entrega.estado_entrega == "ENTREGADO").count()
    novedades = Entrega.query.filter(Entrega.estado_entrega == "NOVEDAD").count()
    despachos_parciales = Despacho.query.filter(Despacho.tipo_despacho == "PARCIAL").count()
    recogidas_pendientes = Pedido.query.filter(
        Pedido.tipo_operacion == "RECOGE_EN_BODEGA",
        Pedido.estado_despacho == "PENDIENTE"
    ).count()

    pedidos_recientes = (
        Pedido.query
        .order_by(Pedido.created_at.desc())
        .limit(20)
        .all()
    )

    stats = {
        "pedidos_hoy": pedidos_hoy,
        "entregas_hoy": entregas_hoy,
        "en_produccion": en_produccion,
        "listos_despacho": listos_despacho,
        "en_ruta": en_ruta,
        "entregados": entregados,
        "novedades": novedades,
        "despachos_parciales": despachos_parciales,
        "recogidas_pendientes": recogidas_pendientes,
    }

    return render_template("dashboard.html", stats=stats, pedidos=pedidos_recientes)
