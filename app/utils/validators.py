def validar_entrega(entrega):
    errores = []
    if not entrega.get("destinatario"):
        errores.append("El nombre del destinatario es obligatorio.")
    if not entrega.get("direccion"):
        errores.append("La dirección de entrega es obligatoria.")
    if not entrega.get("ciudad"):
        errores.append("La ciudad es obligatoria.")
    if not entrega.get("telefono"):
        errores.append("El teléfono es obligatorio.")
    return errores


def validar_pedido(pedido):
    errores = []
    if not pedido.get("numero_pedido"):
        errores.append("El número de pedido es obligatorio.")
    if not pedido.get("id_cliente"):
        errores.append("El cliente es obligatorio.")
    if not pedido.get("tipo_operacion"):
        errores.append("El tipo de operación es obligatorio.")
    return errores


def validar_telefono(telefono):
    if not telefono:
        return False
    digits = "".join(filter(str.isdigit, str(telefono)))
    return len(digits) >= 7
