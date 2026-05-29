from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from app.models import Pedido, Entrega, Despacho
from app.services.excel_service import (
    exportar_plano_simpliroute,
    exportar_plano_alas,
    exportar_plano_pibox,
    exportar_reporte_entregas,
    generar_plantilla_cargue,
)

bp = Blueprint("exportaciones", __name__)


@bp.route("/")
def index():
    return render_template("exportaciones/index.html")


@bp.route("/simpliroute/<int:id_pedido>")
def simpliroute(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    try:
        ruta = exportar_plano_simpliroute(pedido)
        return send_file(ruta, as_attachment=True)
    except Exception as e:
        flash(f"Error al exportar: {str(e)}", "danger")
        return redirect(url_for("pedidos.detalle", id_pedido=id_pedido))


@bp.route("/alas/<int:id_pedido>")
def alas(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    try:
        ruta = exportar_plano_alas(pedido)
        return send_file(ruta, as_attachment=True)
    except Exception as e:
        flash(f"Error al exportar: {str(e)}", "danger")
        return redirect(url_for("pedidos.detalle", id_pedido=id_pedido))


@bp.route("/pibox/<int:id_pedido>")
def pibox(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    try:
        ruta = exportar_plano_pibox(pedido)
        return send_file(ruta, as_attachment=True)
    except Exception as e:
        flash(f"Error al exportar: {str(e)}", "danger")
        return redirect(url_for("pedidos.detalle", id_pedido=id_pedido))


@bp.route("/reporte-entregas/<int:id_pedido>")
def reporte_entregas(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    try:
        ruta = exportar_reporte_entregas(pedido)
        return send_file(ruta, as_attachment=True)
    except Exception as e:
        flash(f"Error al exportar: {str(e)}", "danger")
        return redirect(url_for("pedidos.detalle", id_pedido=id_pedido))


@bp.route("/plantilla-cargue")
def plantilla_cargue():
    try:
        ruta = generar_plantilla_cargue()
        return send_file(ruta, as_attachment=True)
    except Exception as e:
        flash(f"Error al generar plantilla: {str(e)}", "danger")
        return redirect(url_for("exportaciones.index"))
