from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.extensions import db
from app.models import Cliente

bp = Blueprint("clientes", __name__)


@bp.route("/")
def index():
    clientes = Cliente.query.order_by(Cliente.nombre).all()
    return render_template("clientes/index.html", clientes=clientes)


@bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "POST":
        cliente = Cliente(
            nombre=request.form["nombre"],
            nit=request.form.get("nit"),
            contacto_principal=request.form.get("contacto_principal"),
            correo=request.form.get("correo"),
            telefono=request.form.get("telefono"),
            direccion_principal=request.form.get("direccion_principal"),
            ciudad=request.form.get("ciudad"),
            es_convenio=bool(request.form.get("es_convenio")),
            activo=True,
            observaciones=request.form.get("observaciones"),
        )
        db.session.add(cliente)
        db.session.commit()
        flash("Cliente creado exitosamente.", "success")
        return redirect(url_for("clientes.index"))
    return render_template("clientes/form.html", cliente=None, action="Nuevo")


@bp.route("/<int:id_cliente>")
def detalle(id_cliente):
    cliente = Cliente.query.get_or_404(id_cliente)
    return render_template("clientes/detalle.html", cliente=cliente)


@bp.route("/<int:id_cliente>/editar", methods=["GET", "POST"])
def editar(id_cliente):
    cliente = Cliente.query.get_or_404(id_cliente)
    if request.method == "POST":
        cliente.nombre = request.form["nombre"]
        cliente.nit = request.form.get("nit")
        cliente.contacto_principal = request.form.get("contacto_principal")
        cliente.correo = request.form.get("correo")
        cliente.telefono = request.form.get("telefono")
        cliente.direccion_principal = request.form.get("direccion_principal")
        cliente.ciudad = request.form.get("ciudad")
        cliente.es_convenio = bool(request.form.get("es_convenio"))
        cliente.activo = bool(request.form.get("activo"))
        cliente.observaciones = request.form.get("observaciones")
        cliente.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Cliente actualizado exitosamente.", "success")
        return redirect(url_for("clientes.detalle", id_cliente=id_cliente))
    return render_template("clientes/form.html", cliente=cliente, action="Editar")


@bp.route("/<int:id_cliente>/eliminar", methods=["POST"])
def eliminar(id_cliente):
    cliente = Cliente.query.get_or_404(id_cliente)
    cliente.activo = False
    cliente.updated_at = datetime.utcnow()
    db.session.commit()
    flash("Cliente desactivado exitosamente.", "success")
    return redirect(url_for("clientes.index"))


@bp.route("/api/lista")
def api_lista():
    clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
    return jsonify([{"id": c.id_cliente, "nombre": c.nombre} for c in clientes])
