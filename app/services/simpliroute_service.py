import requests
from datetime import datetime


def crear_visita_simpliroute(entrega, token):
    url = "https://api.simpliroute.com/v1/visits/"
    headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
    payload = {
        "title": entrega.destinatario or "",
        "address": entrega.direccion or "",
        "city": entrega.ciudad or "",
        "contact_name": entrega.destinatario or "",
        "contact_phone": entrega.telefono or "",
        "reference": str(entrega.id_pedido),
        "notes": entrega.observacion or "",
        "planned_date": entrega.fecha_entrega.strftime("%Y-%m-%d") if entrega.fecha_entrega else datetime.now().strftime("%Y-%m-%d"),
    }
    response = requests.post(url, json=payload, headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json()
    entrega.link_simpliroute = data.get("tracking_url") or data.get("url", "")
    from app.extensions import db
    db.session.commit()
    return data
