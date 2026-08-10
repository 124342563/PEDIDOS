import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.extensions import db
from app.models import Entrega, Pedido, TrackingEvento
from app.utils.status_mapper import calcular_estado_despacho

bp = Blueprint("entregas", __name__)

ESTADOS_ENTREGA = [
    "PENDIENTE", "PROGRAMADO", "EN RUTA", "ENTREGADO",
    "NO ENTREGADO", "NOVEDAD", "REPROGRAMADO", "REQUIERE ACTUALIZAR TRANSPORTADORA"
]
TRANSPORTADORAS = ["SIMPLIROUTE", "ALAS", "PIBOX", "UBER", "MENSAJEROS URBANOS", "INTERNO", "RECOGE EN BODEGA"]


@bp.route("/")
def index():
    id_pedido = request.args.get("id_pedido", type=int)
    estado = request.args.get("estado")
    query = Entrega.query
    if id_pedido:
        query = query.filter_by(id_pedido=id_pedido)
    if estado:
        query = query.filter_by(estado_entrega=estado)
    entregas = query.order_by(Entrega.created_at.desc()).all()
    return render_template("entregas/index.html", entregas=entregas, estados=ESTADOS_ENTREGA)


@bp.route("/nueva", methods=["GET", "POST"])
def nueva():
    id_pedido = request.args.get("id_pedido", type=int)
    pedidos = Pedido.query.order_by(Pedido.numero_pedido).all()
    if request.method == "POST":
        fecha_entrega = None
        if request.form.get("fecha_entrega"):
            try:
                fecha_entrega = datetime.strptime(request.form["fecha_entrega"], "%Y-%m-%d").date()
            except ValueError:
                pass
        entrega = Entrega(
            id_pedido=request.form["id_pedido"],
            id_cliente=request.form.get("id_cliente") or None,
            destinatario=request.form.get("destinatario"),
            empresa=request.form.get("empresa"),
            direccion=request.form.get("direccion"),
            ciudad=request.form.get("ciudad"),
            municipio=request.form.get("municipio"),
            telefono=request.form.get("telefono"),
            producto=request.form.get("producto"),
            cantidad=int(request.form.get("cantidad") or 1),
            fecha_entrega=fecha_entrega,
            estado_entrega="PENDIENTE",
            transportadora=request.form.get("transportadora"),
            observacion=request.form.get("observacion"),
            token_tracking=str(uuid.uuid4()),
        )
        db.session.add(entrega)
        db.session.flush()
        evento = TrackingEvento(
            id_pedido=entrega.id_pedido,
            id_entrega=entrega.id_entrega,
            estado_anterior=None,
            estado_nuevo="PENDIENTE",
            descripcion="Entrega creada manualmente",
            usuario="usuario",
            origen="MANUAL",
        )
        db.session.add(evento)
        pedido = Pedido.query.get(entrega.id_pedido)
        if pedido:
            pedido.estado_despacho = calcular_estado_despacho(pedido)
            pedido.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Entrega creada exitosamente.", "success")
        return redirect(url_for("pedidos.detalle", id_pedido=entrega.id_pedido))
    return render_template("entregas/form.html", entrega=None, pedidos=pedidos, transportadoras=TRANSPORTADORAS, id_pedido=id_pedido, action="Nueva")


@bp.route("/<int:id_entrega>")
def detalle(id_entrega):
    entrega = Entrega.query.get_or_404(id_entrega)
    eventos = TrackingEvento.query.filter_by(id_entrega=id_entrega).order_by(TrackingEvento.fecha_evento.desc()).all()
    return render_template("entregas/detalle.html", entrega=entrega, eventos=eventos, estados=ESTADOS_ENTREGA)


@bp.route("/<int:id_entrega>/editar", methods=["GET", "POST"])
def editar(id_entrega):
    entrega = Entrega.query.get_or_404(id_entrega)
    pedidos = Pedido.query.order_by(Pedido.numero_pedido).all()
    tiene_guia = bool(entrega.guia_alas or entrega.link_simpliroute or entrega.tracking_pibox)
    if request.method == "POST":
        fecha_entrega = None
        if request.form.get("fecha_entrega"):
            try:
                fecha_entrega = datetime.strptime(request.form["fecha_entrega"], "%Y-%m-%d").date()
            except ValueError:
                pass
        entrega.destinatario = request.form.get("destinatario")
        entrega.empresa = request.form.get("empresa")
        entrega.direccion = request.form.get("direccion")
        entrega.ciudad = request.form.get("ciudad")
        entrega.municipio = request.form.get("municipio")
        entrega.telefono = request.form.get("telefono")
        entrega.producto = request.form.get("producto")
        entrega.cantidad = int(request.form.get("cantidad") or 1)
        entrega.fecha_entrega = fecha_entrega
        entrega.transportadora = request.form.get("transportadora")
        entrega.observacion = request.form.get("observacion")
        if tiene_guia:
            entrega.estado_entrega = "REQUIERE ACTUALIZAR TRANSPORTADORA"
        entrega.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Entrega actualizada.", "success")
        return redirect(url_for("entregas.detalle", id_entrega=id_entrega))
    return render_template("entregas/form.html", entrega=entrega, pedidos=pedidos, transportadoras=TRANSPORTADORAS, action="Editar")


@bp.route("/<int:id_entrega>/cambiar-estado", methods=["POST"])
def cambiar_estado(id_entrega):
    entrega = Entrega.query.get_or_404(id_entrega)
    nuevo_estado = request.form.get("estado_entrega")
    if nuevo_estado in ESTADOS_ENTREGA:
        estado_anterior = entrega.estado_entrega
        entrega.estado_entrega = nuevo_estado
        entrega.updated_at = datetime.utcnow()
        evento = TrackingEvento(
            id_pedido=entrega.id_pedido,
            id_entrega=id_entrega,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            descripcion=f"Estado cambiado a {nuevo_estado}",
            usuario="usuario",
            origen="MANUAL",
        )
        db.session.add(evento)
        pedido = Pedido.query.get(entrega.id_pedido)
        if pedido:
            pedido.estado_despacho = calcular_estado_despacho(pedido)
            pedido.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f"Estado actualizado a {nuevo_estado}.", "success")
    return redirect(url_for("entregas.detalle", id_entrega=id_entrega))
