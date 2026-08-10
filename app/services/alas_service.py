import requests


ESTADO_MAP = {
    "Generada Cliente": "GUIA_GENERADA",
    "Recibido en bodega": "RECIBIDO_TRANSPORTADORA",
    "Viajando a destino": "EN_TRANSITO",
    "En ruta a destinatario": "EN_REPARTO",
    "Entregado": "ENTREGADO",
    "Dirección errada/incompleta": "NOVEDAD_DIRECCION",
    "Reprogramado": "REPROGRAMADO",
}


def crear_guia_alas(entrega, api_url, api_key):
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    payload = {
        "pedido": str(entrega.id_pedido),
        "destinatario": entrega.destinatario or "",
        "direccion": entrega.direccion or "",
        "ciudad": entrega.ciudad or "",
        "municipio": entrega.municipio or "",
        "telefono": entrega.telefono or "",
        "contenido": entrega.producto or "",
        "cantidad": entrega.cantidad or 1,
    }
    response = requests.post(f"{api_url}/guias", json=payload, headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json()
    guia = data.get("guia") or data.get("numero_guia", "")
    if guia:
        entrega.guia_alas = guia
        entrega.estado_entrega = "GUIA_GENERADA"
        from app.extensions import db
        db.session.commit()
    return data


def consultar_estado_guia(guia, api_url, api_key):
    headers = {"Authorization": "Bearer " + api_key}
    response = requests.get(f"{api_url}/guias/{guia}/estado", headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json()
    estado_alas = data.get("estado", "")
    estado_interno = ESTADO_MAP.get(estado_alas, estado_alas)
    return {"estado_alas": estado_alas, "estado_interno": estado_interno, "data": data}
