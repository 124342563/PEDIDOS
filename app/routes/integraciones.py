from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from app.models import Pedido, Entrega, Despacho
from app.services.simpliroute_service import crear_visita_simpliroute
from app.services.alas_service import crear_guia_alas, consultar_estado_guia
from app.services.pibox_service import crear_servicio_pibox

bp = Blueprint("integraciones", __name__)


@bp.route("/")
def index():
    return render_template("integraciones/index.html")


@bp.route("/simpliroute/crear/<int:id_entrega>", methods=["POST"])
def simpliroute_crear(id_entrega):
    entrega = Entrega.query.get_or_404(id_entrega)
    token = current_app.config.get("SIMPLIROUTE_TOKEN")
    if not token:
        flash("Token de SimpliRoute no configurado. Use exportación por archivo plano.", "warning")
        return redirect(url_for("exportaciones.simpliroute", id_pedido=entrega.id_pedido))
    try:
        resultado = crear_visita_simpliroute(entrega, token)
        flash(f"Visita creada en SimpliRoute: {resultado.get('id')}", "success")
    except Exception as e:
        flash(f"Error con SimpliRoute: {str(e)}", "danger")
    return redirect(url_for("entregas.detalle", id_entrega=id_entrega))


@bp.route("/alas/crear-guia/<int:id_entrega>", methods=["POST"])
def alas_crear_guia(id_entrega):
    entrega = Entrega.query.get_or_404(id_entrega)
    api_url = current_app.config.get("ALAS_API_URL")
    api_key = current_app.config.get("ALAS_API_KEY")
    if not api_url or not api_key:
        flash("API de Alas no configurada. Use exportación por archivo plano.", "warning")
        return redirect(url_for("exportaciones.alas", id_pedido=entrega.id_pedido))
    try:
        resultado = crear_guia_alas(entrega, api_url, api_key)
        flash(f"Guía Alas creada: {resultado.get('guia')}", "success")
    except Exception as e:
        flash(f"Error con Alas: {str(e)}", "danger")
    return redirect(url_for("entregas.detalle", id_entrega=id_entrega))


@bp.route("/pibox/crear/<int:id_entrega>", methods=["POST"])
def pibox_crear(id_entrega):
    entrega = Entrega.query.get_or_404(id_entrega)
    api_key = current_app.config.get("PIBOX_API_KEY")
    if not api_key:
        flash("API de Pibox no configurada. Registre el tracking manualmente.", "warning")
        return redirect(url_for("entregas.detalle", id_entrega=id_entrega))
    try:
        resultado = crear_servicio_pibox(entrega, api_key)
        flash(f"Servicio Pibox creado: {resultado.get('tracking')}", "success")
    except Exception as e:
        flash(f"Error con Pibox: {str(e)}", "danger")
    return redirect(url_for("entregas.detalle", id_entrega=id_entrega))
