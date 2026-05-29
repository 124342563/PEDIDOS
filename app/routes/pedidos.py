import uuid
from datetime import datetime, date
from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, jsonify, current_app
)
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import Pedido, PedidoItem, Cliente, Entrega, TrackingEvento
from app.services.excel_service import cargar_entregas_desde_base
from app.utils.status_mapper import calcular_estado_despacho

bp = Blueprint("pedidos", __name__)

TIPOS_OPERACION = ["NORMAL", "CONVENIO_CUMPLEAÑOS", "MASIVO_1_A_1", "UN_SOLO_PUNTO", "RECOGE_EN_BODEGA"]
ESTADOS_PRODUCCION = ["PENDIENTE", "EN PRODUCCIÓN", "PRODUCIDO", "LISTO PARA DESPACHO"]
ESTADOS_DESPACHO = ["PENDIENTE", "PROGRAMADO", "EN RUTA", "PARCIAL", "ENTREGADO", "NO ENTREGADO", "NOVEDAD", "COMPLETO"]


@bp.route("/")
def index():
    estado_prod = request.args.get("estado_produccion")
    estado_desp = request.args.get("estado_despacho")
    tipo_op = request.args.get("tipo_operacion")
    id_cliente = request.args.get("id_cliente", type=int)

    query = Pedido.query
    if estado_prod:
        query = query.filter_by(estado_produccion=estado_prod)
    if estado_desp:
        query = query.filter_by(estado_despacho=estado_desp)
    if tipo_op:
        query = query.filter_by(tipo_operacion=tipo_op)
    if id_cliente:
        query = query.filter_by(id_cliente=id_cliente)

    pedidos = query.order_by(Pedido.created_at.desc()).all()
    clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
    return render_template(
        "pedidos/index.html",
        pedidos=pedidos,
        clientes=clientes,
        tipos_operacion=TIPOS_OPERACION,
        estados_produccion=ESTADOS_PRODUCCION,
        estados_despacho=ESTADOS_DESPACHO,
        filtros=request.args,
    )


@bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
    if request.method == "POST":
        fecha_entrega = None
        if request.form.get("fecha_entrega_general"):
            try:
                fecha_entrega = datetime.strptime(request.form["fecha_entrega_general"], "%Y-%m-%d").date()
            except ValueError:
                pass

        pedido = Pedido(
            numero_pedido=request.form["numero_pedido"],
            id_cliente=request.form["id_cliente"],
            tipo_operacion=request.form["tipo_operacion"],
            producto_principal=request.form.get("producto_principal"),
            cantidad_total=int(request.form.get("cantidad_total") or 0),
            fecha_entrega_general=fecha_entrega,
            vendedora=request.form.get("vendedora"),
            estado_produccion="PENDIENTE",
            estado_despacho="PENDIENTE",
            observacion=request.form.get("observacion"),
        )
        db.session.add(pedido)
        db.session.flush()

        # Add items
        productos = request.form.getlist("producto[]")
        cantidades = request.form.getlist("cantidad_item[]")
        for prod, cant in zip(productos, cantidades):
            if prod.strip():
                item = PedidoItem(
                    id_pedido=pedido.id_pedido,
                    producto=prod.strip(),
                    cantidad=int(cant) if cant else 1,
                )
                db.session.add(item)

        # Tracking
        evento = TrackingEvento(
            id_pedido=pedido.id_pedido,
            estado_anterior=None,
            estado_nuevo="PENDIENTE",
            descripcion="Pedido creado",
            usuario="sistema",
            origen="SISTEMA",
        )
        db.session.add(evento)
        db.session.commit()
        flash("Pedido creado exitosamente.", "success")
        return redirect(url_for("pedidos.detalle", id_pedido=pedido.id_pedido))
    return render_template("pedidos/form.html", pedido=None, clientes=clientes, tipos_operacion=TIPOS_OPERACION, action="Nuevo")


@bp.route("/<int:id_pedido>")
def detalle(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    entregas = Entrega.query.filter_by(id_pedido=id_pedido).all()
    eventos = TrackingEvento.query.filter_by(id_pedido=id_pedido).order_by(TrackingEvento.fecha_evento.desc()).all()
    return render_template(
        "pedidos/detalle.html",
        pedido=pedido,
        entregas=entregas,
        eventos=eventos,
        estados_produccion=ESTADOS_PRODUCCION,
        estados_despacho=ESTADOS_DESPACHO,
    )


@bp.route("/<int:id_pedido>/editar", methods=["GET", "POST"])
def editar(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
    if request.method == "POST":
        fecha_entrega = None
        if request.form.get("fecha_entrega_general"):
            try:
                fecha_entrega = datetime.strptime(request.form["fecha_entrega_general"], "%Y-%m-%d").date()
            except ValueError:
                pass
        pedido.numero_pedido = request.form["numero_pedido"]
        pedido.id_cliente = request.form["id_cliente"]
        pedido.tipo_operacion = request.form["tipo_operacion"]
        pedido.producto_principal = request.form.get("producto_principal")
        pedido.cantidad_total = int(request.form.get("cantidad_total") or 0)
        pedido.fecha_entrega_general = fecha_entrega
        pedido.vendedora = request.form.get("vendedora")
        pedido.observacion = request.form.get("observacion")
        pedido.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Pedido actualizado.", "success")
        return redirect(url_for("pedidos.detalle", id_pedido=id_pedido))
    return render_template("pedidos/form.html", pedido=pedido, clientes=clientes, tipos_operacion=TIPOS_OPERACION, action="Editar")


@bp.route("/<int:id_pedido>/cambiar-estado-produccion", methods=["POST"])
def cambiar_estado_produccion(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    nuevo_estado = request.form.get("estado_produccion")
    if nuevo_estado in ESTADOS_PRODUCCION:
        estado_anterior = pedido.estado_produccion
        pedido.estado_produccion = nuevo_estado
        pedido.updated_at = datetime.utcnow()
        evento = TrackingEvento(
            id_pedido=id_pedido,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            descripcion=f"Estado de producción cambiado a {nuevo_estado}",
            usuario="usuario",
            origen="MANUAL",
        )
        db.session.add(evento)
        db.session.commit()
        flash(f"Estado de producción actualizado a {nuevo_estado}.", "success")
    return redirect(url_for("pedidos.detalle", id_pedido=id_pedido))


@bp.route("/<int:id_pedido>/preparar-despacho", methods=["GET", "POST"])
def preparar_despacho(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    entregas_existentes = Entrega.query.filter_by(id_pedido=id_pedido).all()

    resultado = {
        "accion": None,
        "mensaje": None,
        "entregas_existentes": len(entregas_existentes),
    }

    tipo = pedido.tipo_operacion

    if entregas_existentes:
        resultado["accion"] = "ENTREGA_CREADA"
        resultado["mensaje"] = f"Ya existen {len(entregas_existentes)} entrega(s) para este pedido."
    elif tipo == "RECOGE_EN_BODEGA":
        resultado["accion"] = "RECOGIDA_PROGRAMADA"
        resultado["mensaje"] = "Este pedido es de recogida en bodega. Registre los datos de recogida."
    elif tipo == "UN_SOLO_PUNTO":
        resultado["accion"] = "CREAR_UN_SOLO_PUNTO"
        resultado["mensaje"] = "Cree la entrega de un solo punto para este pedido."
    elif tipo in ("MASIVO_1_A_1", "CONVENIO_CUMPLEAÑOS"):
        resultado["accion"] = "REQUIERE_BASE"
        resultado["mensaje"] = "Este tipo de operación requiere cargar una base de datos."
    elif tipo == "NORMAL":
        # Check if base data available
        if pedido.cliente and pedido.cliente.direccion_principal:
            resultado["accion"] = "CREAR_AUTOMATICO"
            resultado["mensaje"] = "Se puede crear la entrega automáticamente desde los datos del cliente."
        else:
            resultado["accion"] = "REQUIERE_DATOS"
            resultado["mensaje"] = "Complete los datos de entrega para crear la entrega."
    else:
        resultado["accion"] = "REQUIERE_DATOS"
        resultado["mensaje"] = "Complete los datos de entrega."

    return render_template("pedidos/preparar_despacho.html", pedido=pedido, resultado=resultado)


@bp.route("/<int:id_pedido>/crear-entrega-automatica", methods=["POST"])
def crear_entrega_automatica(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    existente = Entrega.query.filter_by(id_pedido=id_pedido).first()
    if existente:
        flash("Ya existen entregas para este pedido.", "warning")
        return redirect(url_for("pedidos.detalle", id_pedido=id_pedido))

    cliente = pedido.cliente
    fecha = pedido.fecha_entrega_general

    entrega = Entrega(
        id_pedido=id_pedido,
        id_cliente=pedido.id_cliente,
        destinatario=cliente.contacto_principal or cliente.nombre,
        empresa=cliente.nombre,
        direccion=cliente.direccion_principal,
        ciudad=cliente.ciudad,
        telefono=cliente.telefono,
        producto=pedido.producto_principal,
        cantidad=pedido.cantidad_total,
        fecha_entrega=fecha,
        estado_entrega="PENDIENTE",
        token_tracking=str(uuid.uuid4()),
    )
    db.session.add(entrega)

    estado_ant = pedido.estado_produccion
    pedido.estado_produccion = "LISTO PARA DESPACHO"
    pedido.updated_at = datetime.utcnow()

    evento = TrackingEvento(
        id_pedido=id_pedido,
        estado_anterior=estado_ant,
        estado_nuevo="LISTO PARA DESPACHO",
        descripcion="Entrega creada automáticamente",
        usuario="sistema",
        origen="SISTEMA",
    )
    db.session.add(evento)
    db.session.commit()
    flash("Entrega creada automáticamente.", "success")
    return redirect(url_for("pedidos.detalle", id_pedido=id_pedido))


@bp.route("/<int:id_pedido>/cargar-base", methods=["GET", "POST"])
def cargar_base(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    if request.method == "POST":
        archivo = request.files.get("archivo")
        if not archivo:
            flash("Debe seleccionar un archivo.", "danger")
            return redirect(request.url)
        filename = secure_filename(archivo.filename)
        if not filename.endswith((".xlsx", ".xls")):
            flash("Solo se permiten archivos Excel (.xlsx, .xls).", "danger")
            return redirect(request.url)
        try:
            resultado = cargar_entregas_desde_base(archivo.stream, pedido)
            flash(f"Base cargada: {resultado['creadas']} entregas creadas, {resultado['errores']} errores.", "success")
        except Exception as e:
            flash(f"Error al cargar base: {str(e)}", "danger")
        return redirect(url_for("pedidos.detalle", id_pedido=id_pedido))
    return render_template("pedidos/cargar_base.html", pedido=pedido)
