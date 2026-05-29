import urllib.parse


def generar_link_whatsapp(numero, mensaje):
    numero_limpio = "".join(filter(str.isdigit, str(numero or "")))
    if not numero_limpio.startswith("57"):
        numero_limpio = "57" + numero_limpio
    mensaje_codificado = urllib.parse.quote(mensaje)
    return f"https://wa.me/{numero_limpio}?text={mensaje_codificado}"


def mensaje_pedido_en_ruta(pedido, entrega):
    return (
        f"Estimado(a) {entrega.destinatario or 'cliente'}, "
        f"su pedido {pedido.numero_pedido} de {entrega.producto or 'producto'} "
        f"está en camino. "
        f"Fecha programada: {entrega.fecha_entrega or 'por definir'}. "
        f"Transportadora: {entrega.transportadora or 'por definir'}. "
        f"Gracias por su preferencia."
    )


def mensaje_cumpleanos(pedido, entrega):
    return (
        f"Feliz cumpleaños {entrega.destinatario or 'colaborador'}! "
        f"Su detalle especial de {pedido.cliente.nombre if pedido.cliente else ''} "
        f"({entrega.producto or ''}) está en camino. "
        f"Esperamos que disfrute su día."
    )
