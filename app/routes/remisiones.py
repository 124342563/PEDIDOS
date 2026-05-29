import os
from flask import Blueprint, render_template, redirect, url_for, flash, send_file, current_app
from app.extensions import db
from app.models import Remision, Pedido, Entrega, Despacho
from app.services.pdf_service import generar_remision_pdf

bp = Blueprint("remisiones", __name__)


@bp.route("/")
def index():
    remisiones = Remision.query.order_by(Remision.fecha_generacion.desc()).all()
    return render_template("remisiones/index.html", remisiones=remisiones)


@bp.route("/generar/pedido/<int:id_pedido>")
def generar_pedido(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    try:
        remision = generar_remision_pdf(pedido=pedido, tipo="NORMAL")
        db.session.add(remision)
        db.session.commit()
        flash(f"Remisión {remision.numero_remision} generada exitosamente.", "success")
    except Exception as e:
        flash(f"Error al generar remisión: {str(e)}", "danger")
    return redirect(url_for("pedidos.detalle", id_pedido=id_pedido))


@bp.route("/generar/entrega/<int:id_entrega>")
def generar_entrega(id_entrega):
    entrega = Entrega.query.get_or_404(id_entrega)
    pedido = Pedido.query.get_or_404(entrega.id_pedido)
    try:
        remision = generar_remision_pdf(pedido=pedido, entrega=entrega, tipo="BENEFICIARIO")
        db.session.add(remision)
        db.session.commit()
        flash(f"Remisión {remision.numero_remision} generada exitosamente.", "success")
    except Exception as e:
        flash(f"Error al generar remisión: {str(e)}", "danger")
    return redirect(url_for("entregas.detalle", id_entrega=id_entrega))


@bp.route("/generar/despacho/<int:id_despacho>")
def generar_despacho(id_despacho):
    despacho = Despacho.query.get_or_404(id_despacho)
    pedido = Pedido.query.get_or_404(despacho.id_pedido)
    tipo = "PARCIAL" if despacho.tipo_despacho == "PARCIAL" else "FINAL" if despacho.tipo_despacho == "FINAL" else "NORMAL"
    try:
        remision = generar_remision_pdf(pedido=pedido, despacho=despacho, tipo=tipo)
        db.session.add(remision)
        db.session.commit()
        flash(f"Remisión {remision.numero_remision} generada exitosamente.", "success")
    except Exception as e:
        flash(f"Error al generar remisión: {str(e)}", "danger")
    return redirect(url_for("despachos.detalle", id_despacho=id_despacho))


@bp.route("/descargar/<int:id_remision>")
def descargar(id_remision):
    remision = Remision.query.get_or_404(id_remision)
    if not remision.ruta_pdf or not os.path.exists(remision.ruta_pdf):
        flash("El archivo PDF no está disponible.", "danger")
        return redirect(url_for("remisiones.index"))
    return send_file(remision.ruta_pdf, as_attachment=True, download_name=remision.nombre_archivo)
