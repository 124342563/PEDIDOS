from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models import Notificacion, Pedido, Entrega
from app.services.email_service import enviar_correo
from app.services.whatsapp_service import generar_link_whatsapp
from app.extensions import db

bp = Blueprint("notificaciones", __name__)


@bp.route("/")
def index():
    notificaciones = Notificacion.query.order_by(Notificacion.fecha_envio.desc()).limit(100).all()
    return render_template("notificaciones/index.html", notificaciones=notificaciones)


@bp.route("/enviar-correo/<int:id_pedido>", methods=["GET", "POST"])
def enviar_correo_pedido(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    if request.method == "POST":
        destinatario = request.form.get("destinatario")
        asunto = request.form.get("asunto")
        mensaje = request.form.get("mensaje")
        try:
            resultado = enviar_correo(destinatario, asunto, mensaje)
            notif = Notificacion(
                id_pedido=id_pedido,
                canal="CORREO",
                destinatario=destinatario,
                asunto=asunto,
                mensaje=mensaje,
                estado_envio="ENVIADO" if resultado else "ERROR",
            )
            db.session.add(notif)
            db.session.commit()
            flash("Correo enviado exitosamente." if resultado else "Error al enviar correo.", "success" if resultado else "danger")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
        return redirect(url_for("pedidos.detalle", id_pedido=id_pedido))
    return render_template("notificaciones/correo.html", pedido=pedido)


@bp.route("/whatsapp/<int:id_entrega>")
def whatsapp_entrega(id_entrega):
    entrega = Entrega.query.get_or_404(id_entrega)
    pedido = entrega.pedido
    mensaje = (
        f"Estimado(a) {entrega.destinatario}, su pedido {pedido.numero_pedido} "
        f"de {entrega.producto} está en camino. "
        f"Fecha de entrega programada: {entrega.fecha_entrega}. "
        f"Transportadora: {entrega.transportadora or 'Por definir'}."
    )
    link = generar_link_whatsapp(entrega.telefono, mensaje)
    return redirect(link)
