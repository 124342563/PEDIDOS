import io
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import Colaborador, Cliente
from app.services.excel_service import importar_colaboradores_excel

bp = Blueprint("colaboradores", __name__)


@bp.route("/")
def index():
    id_cliente = request.args.get("id_cliente", type=int)
    query = Colaborador.query
    if id_cliente:
        query = query.filter_by(id_cliente=id_cliente)
    colaboradores = query.order_by(Colaborador.nombre).all()
    clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
    return render_template("colaboradores/index.html", colaboradores=colaboradores, clientes=clientes, id_cliente_sel=id_cliente)


@bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
    if request.method == "POST":
        fecha_nac = None
        if request.form.get("fecha_nacimiento"):
            try:
                fecha_nac = datetime.strptime(request.form["fecha_nacimiento"], "%Y-%m-%d").date()
            except ValueError:
                pass
        colaborador = Colaborador(
            id_cliente=request.form["id_cliente"],
            nombre=request.form["nombre"],
            documento=request.form.get("documento"),
            telefono=request.form.get("telefono"),
            correo=request.form.get("correo"),
            direccion=request.form.get("direccion"),
            ciudad=request.form.get("ciudad"),
            municipio=request.form.get("municipio"),
            fecha_nacimiento=fecha_nac,
            activo=True,
            observacion=request.form.get("observacion"),
        )
        db.session.add(colaborador)
        db.session.commit()
        flash("Colaborador creado exitosamente.", "success")
        return redirect(url_for("colaboradores.index"))
    return render_template("colaboradores/form.html", colaborador=None, clientes=clientes, action="Nuevo")


@bp.route("/<int:id_colaborador>/editar", methods=["GET", "POST"])
def editar(id_colaborador):
    colaborador = Colaborador.query.get_or_404(id_colaborador)
    clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
    if request.method == "POST":
        fecha_nac = None
        if request.form.get("fecha_nacimiento"):
            try:
                fecha_nac = datetime.strptime(request.form["fecha_nacimiento"], "%Y-%m-%d").date()
            except ValueError:
                pass
        colaborador.id_cliente = request.form["id_cliente"]
        colaborador.nombre = request.form["nombre"]
        colaborador.documento = request.form.get("documento")
        colaborador.telefono = request.form.get("telefono")
        colaborador.correo = request.form.get("correo")
        colaborador.direccion = request.form.get("direccion")
        colaborador.ciudad = request.form.get("ciudad")
        colaborador.municipio = request.form.get("municipio")
        colaborador.fecha_nacimiento = fecha_nac
        colaborador.activo = bool(request.form.get("activo"))
        colaborador.observacion = request.form.get("observacion")
        colaborador.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Colaborador actualizado exitosamente.", "success")
        return redirect(url_for("colaboradores.index"))
    return render_template("colaboradores/form.html", colaborador=colaborador, clientes=clientes, action="Editar")


@bp.route("/<int:id_colaborador>/eliminar", methods=["POST"])
def eliminar(id_colaborador):
    colaborador = Colaborador.query.get_or_404(id_colaborador)
    colaborador.activo = False
    colaborador.updated_at = datetime.utcnow()
    db.session.commit()
    flash("Colaborador desactivado.", "success")
    return redirect(url_for("colaboradores.index"))


@bp.route("/importar", methods=["GET", "POST"])
def importar():
    clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
    if request.method == "POST":
        archivo = request.files.get("archivo")
        id_cliente = request.form.get("id_cliente")
        if not archivo or not id_cliente:
            flash("Debe seleccionar un archivo y un cliente.", "danger")
            return redirect(url_for("colaboradores.importar"))
        filename = secure_filename(archivo.filename)
        if not filename.endswith((".xlsx", ".xls")):
            flash("Solo se permiten archivos Excel (.xlsx, .xls).", "danger")
            return redirect(url_for("colaboradores.importar"))
        try:
            resultado = importar_colaboradores_excel(archivo.stream, int(id_cliente))
            flash(f"Importación completada: {resultado['creados']} creados, {resultado['errores']} errores.", "success")
        except Exception as e:
            flash(f"Error al importar: {str(e)}", "danger")
        return redirect(url_for("colaboradores.index"))
    return render_template("colaboradores/importar.html", clientes=clientes)
