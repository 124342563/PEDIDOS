import requests


def crear_servicio_pibox(entrega, api_key):
    url = "https://api.pibox.app/v1/services"
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    payload = {
        "recipient_name": entrega.destinatario or "",
        "recipient_phone": entrega.telefono or "",
        "address": entrega.direccion or "",
        "city": entrega.ciudad or "",
        "notes": entrega.observacion or "",
    }
    response = requests.post(url, json=payload, headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json()
    tracking = data.get("tracking_id") or data.get("id", "")
    if tracking:
        entrega.tracking_pibox = tracking
        from app.extensions import db
        db.session.commit()
    return {"tracking": tracking, "data": data}
