import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app


def enviar_correo(destinatario, asunto, mensaje, adjunto_path=None):
    host = current_app.config.get("SMTP_HOST")
    port = current_app.config.get("SMTP_PORT", 587)
    user = current_app.config.get("SMTP_USER")
    password = current_app.config.get("SMTP_PASSWORD")
    mail_from = current_app.config.get("MAIL_FROM") or user

    if not host or not user or not password:
        current_app.logger.warning("SMTP no configurado. Correo no enviado.")
        return False

    msg = MIMEMultipart()
    msg["From"] = mail_from
    msg["To"] = destinatario
    msg["Subject"] = asunto
    msg.attach(MIMEText(mensaje, "html"))

    if adjunto_path:
        import os
        from email.mime.base import MIMEBase
        from email import encoders
        if os.path.exists(adjunto_path):
            with open(adjunto_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(adjunto_path)}")
            msg.attach(part)

    try:
        with smtplib.SMTP(host, port) as server:
            server.ehlo()
            server.starttls()
            server.login(user, password)
            server.sendmail(mail_from, destinatario, msg.as_string())
        return True
    except Exception as e:
        current_app.logger.error(f"Error enviando correo: {e}")
        return False


def correo_pedido_creado(pedido):
    cliente = pedido.cliente
    correo_dest = cliente.correo if cliente else None
    if not correo_dest:
        return False
    asunto = f"Pedido {pedido.numero_pedido} recibido - {cliente.nombre}"
    mensaje = f"""
    <p>Estimado(a) {cliente.contacto_principal or cliente.nombre},</p>
    <p>Su pedido <strong>{pedido.numero_pedido}</strong> ha sido recibido y registrado correctamente.</p>
    <table border="1" cellpadding="5" style="border-collapse:collapse;">
        <tr><td><b>Cliente</b></td><td>{cliente.nombre}</td></tr>
        <tr><td><b>Pedido</b></td><td>{pedido.numero_pedido}</td></tr>
        <tr><td><b>Producto</b></td><td>{pedido.producto_principal or ''}</td></tr>
        <tr><td><b>Cantidad</b></td><td>{pedido.cantidad_total}</td></tr>
        <tr><td><b>Fecha programada</b></td><td>{pedido.fecha_entrega_general or ''}</td></tr>
        <tr><td><b>Estado</b></td><td>{pedido.estado_despacho}</td></tr>
    </table>
    <p>Quedo atento.</p>
    """
    return enviar_correo(correo_dest, asunto, mensaje)


def correo_entrega_realizada(entrega):
    pedido = entrega.pedido
    cliente = pedido.cliente if pedido else None
    correo_dest = cliente.correo if cliente else None
    if not correo_dest:
        return False
    asunto = f"Pedido {pedido.numero_pedido} entregado - {cliente.nombre}"
    mensaje = f"""
    <p>Cordial saludo,</p>
    <p>Se informa que la entrega fue realizada correctamente.</p>
    <table border="1" cellpadding="5" style="border-collapse:collapse;">
        <tr><td><b>Cliente</b></td><td>{cliente.nombre}</td></tr>
        <tr><td><b>Pedido</b></td><td>{pedido.numero_pedido}</td></tr>
        <tr><td><b>Destinatario</b></td><td>{entrega.destinatario or ''}</td></tr>
        <tr><td><b>Producto</b></td><td>{entrega.producto or ''}</td></tr>
        <tr><td><b>Fecha entrega</b></td><td>{entrega.fecha_entrega or ''}</td></tr>
        <tr><td><b>Estado</b></td><td>{entrega.estado_entrega}</td></tr>
    </table>
    <p>Quedo atento.</p>
    """
    return enviar_correo(correo_dest, asunto, mensaje)
