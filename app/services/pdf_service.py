import os
import re
from datetime import datetime
from flask import current_app
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from app.models import Remision
from app.extensions import db


def _sanitize_filename(name):
    name = str(name).upper()
    name = re.sub(r"[^A-Z0-9_\-]", "_", name)
    name = re.sub(r"_+", "_", name)
    return name.strip("_")


def _get_remision_folder(pedido, cliente_nombre):
    base = current_app.config["REMISIONES_FOLDER"]
    now = datetime.now()
    year = str(now.year)
    mes_num = now.strftime("%m")
    mes_nombre = now.strftime("%B").upper()
    mes_folder = f"{mes_num}_{mes_nombre}"
    cliente_folder = _sanitize_filename(cliente_nombre or "GENERAL")
    pedido_folder = f"PEDIDO_{pedido.numero_pedido}"
    folder = os.path.join(base, year, mes_folder, cliente_folder, pedido_folder)
    os.makedirs(folder, exist_ok=True)
    return folder


def _unique_filename(folder, base_name):
    filepath = os.path.join(folder, base_name)
    if not os.path.exists(filepath):
        return base_name, filepath
    stem, ext = os.path.splitext(base_name)
    version = 2
    while True:
        new_name = f"{stem}_V{version}{ext}"
        new_path = os.path.join(folder, new_name)
        if not os.path.exists(new_path):
            return new_name, new_path
        version += 1


def _build_filename(pedido, entrega, despacho, tipo):
    num = pedido.numero_pedido
    fecha = datetime.now().strftime("%Y%m%d")
    cliente = _sanitize_filename(pedido.cliente.nombre if pedido.cliente else "CLIENTE")

    if tipo == "NORMAL":
        return f"REM_{num}_{fecha}_{cliente}.pdf"
    elif tipo in ("BENEFICIARIO",) and entrega:
        idx = entrega.id_entrega
        dest = _sanitize_filename(entrega.destinatario or "DESTINATARIO")
        return f"REM_{num}_{str(idx).zfill(3)}_{dest}.pdf"
    elif tipo == "UN_SOLO_PUNTO":
        return f"REM_{num}_{cliente}_UN_SOLO_PUNTO.pdf"
    elif tipo == "RECOGIDA":
        return f"ACTA_RECOGIDA_{num}_{cliente}.pdf"
    elif tipo == "PARCIAL" and despacho:
        return f"REM_{num}_{despacho.numero_despacho}_PARCIAL.pdf"
    elif tipo == "FINAL" and despacho:
        return f"REM_{num}_{despacho.numero_despacho}_FINAL.pdf"
    else:
        return f"REM_{num}_{fecha}.pdf"


def _next_numero_remision(pedido_num):
    last = Remision.query.filter(
        Remision.numero_remision.like(f"REM-{pedido_num}-%")
    ).order_by(Remision.id_remision.desc()).first()
    if last:
        try:
            seq = int(last.numero_remision.split("-")[-1]) + 1
        except Exception:
            seq = 1
    else:
        seq = 1
    return f"REM-{pedido_num}-{str(seq).zfill(4)}"


def generar_remision_pdf(pedido, entrega=None, despacho=None, tipo="NORMAL"):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=styles["Title"], fontSize=16, spaceAfter=6, alignment=TA_CENTER)
    header_style = ParagraphStyle("header", parent=styles["Normal"], fontSize=10, textColor=colors.white, alignment=TA_CENTER)
    normal_style = styles["Normal"]
    bold_style = ParagraphStyle("bold", parent=styles["Normal"], fontName="Helvetica-Bold")
    small_style = ParagraphStyle("small", parent=styles["Normal"], fontSize=8)

    cliente_nombre = pedido.cliente.nombre if pedido.cliente else "N/A"
    folder = _get_remision_folder(pedido, cliente_nombre)
    base_filename = _build_filename(pedido, entrega, despacho, tipo)
    nombre_archivo, filepath = _unique_filename(folder, base_filename)

    numero_remision = _next_numero_remision(pedido.numero_pedido)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    elements = []

    # Header
    elements.append(Paragraph("TGC LOGÍSTICA", title_style))
    elements.append(Paragraph(f"REMISIÓN N° {numero_remision}", ParagraphStyle("remnum", parent=styles["Heading2"], alignment=TA_CENTER)))
    elements.append(Paragraph(f"Tipo: {tipo}", ParagraphStyle("tipo", parent=styles["Normal"], alignment=TA_CENTER, fontSize=10, textColor=colors.grey)))
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1F4E79")))
    elements.append(Spacer(1, 0.3 * cm))

    # Info table
    fecha_gen = datetime.now().strftime("%d/%m/%Y %H:%M")
    pedido_info = [
        ["N° Pedido:", pedido.numero_pedido, "Fecha Remisión:", fecha_gen],
        ["Cliente:", cliente_nombre, "Tipo Operación:", pedido.tipo_operacion],
        ["Producto:", pedido.producto_principal or "", "Cantidad Total:", str(pedido.cantidad_total)],
    ]

    if entrega:
        pedido_info += [
            ["Destinatario:", entrega.destinatario or "", "Empresa:", entrega.empresa or ""],
            ["Dirección:", entrega.direccion or "", "Ciudad:", entrega.ciudad or ""],
            ["Municipio:", entrega.municipio or "", "Teléfono:", entrega.telefono or ""],
            ["Fecha Entrega:", str(entrega.fecha_entrega or ""), "Transportadora:", entrega.transportadora or ""],
            ["Guía/Tracking:", entrega.guia_alas or entrega.tracking_pibox or "", "Estado:", entrega.estado_entrega or ""],
        ]
    elif despacho:
        entrega_list = [de.entrega for de in despacho.despacho_entregas if de.entrega]
        pedido_info += [
            ["N° Despacho:", despacho.numero_despacho, "Tipo Despacho:", despacho.tipo_despacho or ""],
            ["Fecha Despacho:", str(despacho.fecha_despacho or ""), "Transportadora:", despacho.transportadora or ""],
            ["Cant. Despachada:", str(despacho.cantidad_despachada), "Cant. Pendiente:", str(pedido.cantidad_total - sum(d.cantidad_despachada or 0 for d in pedido.despachos))],
        ]
        if entrega_list:
            pedido_info.append(["Entregas incluidas:", str(len(entrega_list)), "", ""])

    table = Table(pedido_info, colWidths=[4 * cm, 7.5 * cm, 4 * cm, 7.5 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F0FE")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#E8F0FE")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.5 * cm))

    if despacho and despacho.despacho_entregas:
        elements.append(Paragraph("DETALLE DE ENTREGAS", bold_style))
        elements.append(Spacer(1, 0.2 * cm))
        det_headers = ["#", "Destinatario", "Dirección", "Ciudad", "Teléfono", "Cantidad"]
        det_data = [det_headers]
        for i, de in enumerate(despacho.despacho_entregas, 1):
            e = de.entrega
            if e:
                det_data.append([
                    str(i), e.destinatario or "", e.direccion or "",
                    e.ciudad or "", e.telefono or "", str(de.cantidad_despachada)
                ])
        det_table = Table(det_data, colWidths=[1 * cm, 5 * cm, 6 * cm, 3 * cm, 3.5 * cm, 2.5 * cm])
        det_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 3),
        ]))
        elements.append(det_table)
        elements.append(Spacer(1, 0.5 * cm))

    # Parcial info
    if tipo in ("PARCIAL", "FINAL") and despacho:
        cant_total = pedido.cantidad_total
        cant_remitida = despacho.cantidad_despachada
        cant_pendiente = cant_total - sum(d.cantidad_despachada or 0 for d in pedido.despachos if d.id_despacho != despacho.id_despacho)
        parcial_data = [
            ["Cantidad Total Pedido", "Cantidad Remitida", "Cantidad Pendiente"],
            [str(cant_total), str(cant_remitida), str(max(0, cant_pendiente - cant_remitida))],
        ]
        parcial_table = Table(parcial_data, colWidths=[6 * cm, 6 * cm, 6 * cm])
        parcial_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E75B6")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 1, colors.white),
            ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#DEEBF7")),
        ]))
        elements.append(parcial_table)
        elements.append(Spacer(1, 0.5 * cm))

    # Observations
    obs = entrega.observacion if entrega else (despacho.observacion if despacho else pedido.observacion)
    if obs:
        elements.append(Paragraph(f"<b>Observaciones:</b> {obs}", normal_style))
        elements.append(Spacer(1, 0.3 * cm))

    # Signature
    elements.append(Spacer(1, 1 * cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    firma_data = [
        ["ENTREGADO POR", "RECIBIDO POR"],
        ["\n\n\n_________________________", "\n\n\n_________________________"],
        ["Firma / Nombre", "Firma / Nombre / Documento"],
    ]
    firma_table = Table(firma_data, colWidths=[9 * cm, 9 * cm])
    firma_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(firma_table)

    doc.build(elements)

    remision = Remision(
        id_pedido=pedido.id_pedido,
        id_entrega=entrega.id_entrega if entrega else None,
        id_despacho=despacho.id_despacho if despacho else None,
        numero_remision=numero_remision,
        tipo_remision=tipo,
        ruta_pdf=filepath,
        nombre_archivo=nombre_archivo,
        usuario_genero="usuario",
    )
    return remision
