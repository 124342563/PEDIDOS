from flask import Blueprint, render_template, abort
from app.models import Entrega, TrackingEvento, Pedido

bp = Blueprint("tracking", __name__)


@bp.route("/<token>")
def publico(token):
    entrega = Entrega.query.filter_by(token_tracking=token).first_or_404()
    pedido = Pedido.query.get(entrega.id_pedido)
    eventos = (
        TrackingEvento.query
        .filter_by(id_entrega=entrega.id_entrega)
        .order_by(TrackingEvento.fecha_evento.asc())
        .all()
    )
    return render_template("tracking/publico.html", entrega=entrega, pedido=pedido, eventos=eventos)


@bp.route("/pedido/<int:id_pedido>")
def pedido(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    eventos = (
        TrackingEvento.query
        .filter_by(id_pedido=id_pedido)
        .order_by(TrackingEvento.fecha_evento.asc())
        .all()
    )
    return render_template("tracking/pedido.html", pedido=pedido, eventos=eventos)
