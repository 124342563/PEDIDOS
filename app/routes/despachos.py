from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.extensions import db
from app.models import Despacho, DespachoEntrega, Entrega, Pedido, TrackingEvento
from app.utils.status_mapper import calcular_estado_despacho

bp = Blueprint("despachos", __name__)

TIPOS_DESPACHO = ["TOTAL", "PARCIAL", "FINAL"]
TRANSPORTADORAS = ["SIMPLIROUTE", "ALAS", "PIBOX", "UBER", "MENSAJEROS URBANOS", "INTERNO", "RECOGE EN BODEGA"]


@bp.route("/")
def index():
    despachos = Despacho.query.order_by(Despacho.created_at.desc()).all()
    return render_template("despachos/index.html", despachos=despachos)


@bp.route("/nuevo/<int:id_pedido>", methods=["GET", "POST"])
def nuevo(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    entregas_pendientes = Entrega.query.filter(
        Entrega.id_pedido == id_pedido,
        Entrega.estado_entrega.in_(["PENDIENTE", "PROGRAMADO"])
    ).all()

    if request.method == "POST":
        tipo = request.form.get("tipo_despacho")
        transportadora = request.form.get("transportadora")
        observacion = request.form.get("observacion")
        fecha_str = request.form.get("fecha_despacho")
        fecha_despacho = date.today()
        if fecha_str:
            try:
                fecha_despacho = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        entrega_ids = request.form.getlist("entregas[]")
        if not entrega_ids:
            flash("Debe seleccionar al menos una entrega.", "danger")
            return redirect(request.url)

        # Generate despacho number
        count = Despacho.query.filter_by(id_pedido=id_pedido).count()
        numero_despacho = f"{pedido.numero_pedido}-{str(count + 1).zfill(2)}"

        cantidad_total = 0
        despacho = Despacho(
            numero_despacho=numero_despacho,
            id_pedido=id_pedido,
            tipo_despacho=tipo,
            fecha_despacho=fecha_despacho,
            transportadora=transportadora,
            estado_despacho="PROGRAMADO",
            observacion=observacion,
        )
        db.session.add(despacho)
        db.session.flush()

        for eid in entrega_ids:
            entrega = Entrega.query.get(int(eid))
            if entrega:
                de = DespachoEntrega(
                    id_despacho=despacho.id_despacho,
                    id_entrega=entrega.id_entrega,
                    cantidad_despachada=entrega.cantidad,
                )
                db.session.add(de)
                cantidad_total += entrega.cantidad or 0
                entrega.estado_entrega = "PROGRAMADO"
                entrega.transportadora = transportadora
                entrega.updated_at = datetime.utcnow()
                evento_e = TrackingEvento(
                    id_pedido=id_pedido,
                    id_entrega=entrega.id_entrega,
                    id_despacho=despacho.id_despacho,
                    estado_anterior="PENDIENTE",
                    estado_nuevo="PROGRAMADO",
                    descripcion=f"Incluida en despacho {numero_despacho}",
                    usuario="usuario",
                    origen="MANUAL",
                )
                db.session.add(evento_e)

        despacho.cantidad_despachada = cantidad_total

        # Update pedido state
        nuevo_estado = calcular_estado_despacho(pedido)
        pedido.estado_despacho = nuevo_estado
        pedido.updated_at = datetime.utcnow()

        evento_p = TrackingEvento(
            id_pedido=id_pedido,
            id_despacho=despacho.id_despacho,
            estado_anterior=pedido.estado_despacho,
            estado_nuevo=nuevo_estado,
            descripcion=f"Despacho {tipo} creado: {numero_despacho}",
            usuario="usuario",
            origen="MANUAL",
        )
        db.session.add(evento_p)
        db.session.commit()
        flash(f"Despacho {numero_despacho} creado exitosamente.", "success")
        return redirect(url_for("pedidos.detalle", id_pedido=id_pedido))

    return render_template(
        "despachos/form.html",
        pedido=pedido,
        entregas=entregas_pendientes,
        tipos_despacho=TIPOS_DESPACHO,
        transportadoras=TRANSPORTADORAS,
    )


@bp.route("/<int:id_despacho>")
def detalle(id_despacho):
    despacho = Despacho.query.get_or_404(id_despacho)
    return render_template("despachos/detalle.html", despacho=despacho)
