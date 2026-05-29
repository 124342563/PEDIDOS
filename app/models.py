from datetime import datetime
from app.extensions import db


class Cliente(db.Model):
    __tablename__ = "clientes"

    id_cliente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.Text, nullable=False)
    nit = db.Column(db.Text)
    contacto_principal = db.Column(db.Text)
    correo = db.Column(db.Text)
    telefono = db.Column(db.Text)
    direccion_principal = db.Column(db.Text)
    ciudad = db.Column(db.Text)
    es_convenio = db.Column(db.Boolean, default=False)
    activo = db.Column(db.Boolean, default=True)
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pedidos = db.relationship("Pedido", backref="cliente", lazy=True)
    colaboradores = db.relationship("Colaborador", backref="cliente", lazy=True)

    def to_dict(self):
        return {
            "id_cliente": self.id_cliente,
            "nombre": self.nombre,
            "nit": self.nit,
            "contacto_principal": self.contacto_principal,
            "correo": self.correo,
            "telefono": self.telefono,
            "direccion_principal": self.direccion_principal,
            "ciudad": self.ciudad,
            "es_convenio": self.es_convenio,
            "activo": self.activo,
            "observaciones": self.observaciones,
        }


class Colaborador(db.Model):
    __tablename__ = "colaboradores"

    id_colaborador = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("clientes.id_cliente"), nullable=False)
    nombre = db.Column(db.Text, nullable=False)
    documento = db.Column(db.Text)
    telefono = db.Column(db.Text)
    correo = db.Column(db.Text)
    direccion = db.Column(db.Text)
    ciudad = db.Column(db.Text)
    municipio = db.Column(db.Text)
    fecha_nacimiento = db.Column(db.Date)
    activo = db.Column(db.Boolean, default=True)
    observacion = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id_colaborador": self.id_colaborador,
            "id_cliente": self.id_cliente,
            "nombre": self.nombre,
            "documento": self.documento,
            "telefono": self.telefono,
            "correo": self.correo,
            "direccion": self.direccion,
            "ciudad": self.ciudad,
            "municipio": self.municipio,
            "fecha_nacimiento": self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            "activo": self.activo,
            "observacion": self.observacion,
        }


class Pedido(db.Model):
    __tablename__ = "pedidos"

    id_pedido = db.Column(db.Integer, primary_key=True)
    numero_pedido = db.Column(db.Text, nullable=False, unique=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("clientes.id_cliente"), nullable=False)
    tipo_operacion = db.Column(db.Text, nullable=False)
    producto_principal = db.Column(db.Text)
    cantidad_total = db.Column(db.Integer, default=0)
    fecha_entrega_general = db.Column(db.Date)
    vendedora = db.Column(db.Text)
    estado_produccion = db.Column(db.Text, default="PENDIENTE")
    estado_despacho = db.Column(db.Text, default="PENDIENTE")
    observacion = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship("PedidoItem", backref="pedido", lazy=True, cascade="all, delete-orphan")
    entregas = db.relationship("Entrega", backref="pedido", lazy=True, cascade="all, delete-orphan")
    despachos = db.relationship("Despacho", backref="pedido", lazy=True, cascade="all, delete-orphan")
    tracking_eventos = db.relationship("TrackingEvento", backref="pedido", lazy=True)
    remisiones = db.relationship("Remision", backref="pedido", lazy=True)

    def to_dict(self):
        return {
            "id_pedido": self.id_pedido,
            "numero_pedido": self.numero_pedido,
            "id_cliente": self.id_cliente,
            "cliente_nombre": self.cliente.nombre if self.cliente else None,
            "tipo_operacion": self.tipo_operacion,
            "producto_principal": self.producto_principal,
            "cantidad_total": self.cantidad_total,
            "fecha_entrega_general": self.fecha_entrega_general.isoformat() if self.fecha_entrega_general else None,
            "vendedora": self.vendedora,
            "estado_produccion": self.estado_produccion,
            "estado_despacho": self.estado_despacho,
            "observacion": self.observacion,
        }


class PedidoItem(db.Model):
    __tablename__ = "pedido_items"

    id_item = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedidos.id_pedido"), nullable=False)
    producto = db.Column(db.Text, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    observacion = db.Column(db.Text)

    def to_dict(self):
        return {
            "id_item": self.id_item,
            "id_pedido": self.id_pedido,
            "producto": self.producto,
            "cantidad": self.cantidad,
            "observacion": self.observacion,
        }


class Entrega(db.Model):
    __tablename__ = "entregas"

    id_entrega = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedidos.id_pedido"), nullable=False)
    id_cliente = db.Column(db.Integer, db.ForeignKey("clientes.id_cliente"))
    id_colaborador = db.Column(db.Integer, db.ForeignKey("colaboradores.id_colaborador"))
    destinatario = db.Column(db.Text)
    empresa = db.Column(db.Text)
    direccion = db.Column(db.Text)
    ciudad = db.Column(db.Text)
    municipio = db.Column(db.Text)
    telefono = db.Column(db.Text)
    producto = db.Column(db.Text)
    cantidad = db.Column(db.Integer, default=1)
    fecha_entrega = db.Column(db.Date)
    estado_entrega = db.Column(db.Text, default="PENDIENTE")
    transportadora = db.Column(db.Text)
    guia_alas = db.Column(db.Text)
    link_simpliroute = db.Column(db.Text)
    tracking_pibox = db.Column(db.Text)
    token_tracking = db.Column(db.Text)
    observacion = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tracking_eventos = db.relationship("TrackingEvento", backref="entrega", lazy=True)
    remisiones = db.relationship("Remision", backref="entrega", lazy=True)

    def to_dict(self):
        return {
            "id_entrega": self.id_entrega,
            "id_pedido": self.id_pedido,
            "id_cliente": self.id_cliente,
            "id_colaborador": self.id_colaborador,
            "destinatario": self.destinatario,
            "empresa": self.empresa,
            "direccion": self.direccion,
            "ciudad": self.ciudad,
            "municipio": self.municipio,
            "telefono": self.telefono,
            "producto": self.producto,
            "cantidad": self.cantidad,
            "fecha_entrega": self.fecha_entrega.isoformat() if self.fecha_entrega else None,
            "estado_entrega": self.estado_entrega,
            "transportadora": self.transportadora,
            "guia_alas": self.guia_alas,
            "link_simpliroute": self.link_simpliroute,
            "tracking_pibox": self.tracking_pibox,
            "token_tracking": self.token_tracking,
            "observacion": self.observacion,
        }


class Despacho(db.Model):
    __tablename__ = "despachos"

    id_despacho = db.Column(db.Integer, primary_key=True)
    numero_despacho = db.Column(db.Text, nullable=False, unique=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedidos.id_pedido"), nullable=False)
    tipo_despacho = db.Column(db.Text)
    fecha_despacho = db.Column(db.Date)
    transportadora = db.Column(db.Text)
    estado_despacho = db.Column(db.Text, default="PENDIENTE")
    cantidad_despachada = db.Column(db.Integer, default=0)
    observacion = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    despacho_entregas = db.relationship("DespachoEntrega", backref="despacho", lazy=True, cascade="all, delete-orphan")
    remisiones = db.relationship("Remision", backref="despacho", lazy=True)

    def to_dict(self):
        return {
            "id_despacho": self.id_despacho,
            "numero_despacho": self.numero_despacho,
            "id_pedido": self.id_pedido,
            "tipo_despacho": self.tipo_despacho,
            "fecha_despacho": self.fecha_despacho.isoformat() if self.fecha_despacho else None,
            "transportadora": self.transportadora,
            "estado_despacho": self.estado_despacho,
            "cantidad_despachada": self.cantidad_despachada,
            "observacion": self.observacion,
        }


class DespachoEntrega(db.Model):
    __tablename__ = "despacho_entregas"

    id = db.Column(db.Integer, primary_key=True)
    id_despacho = db.Column(db.Integer, db.ForeignKey("despachos.id_despacho"), nullable=False)
    id_entrega = db.Column(db.Integer, db.ForeignKey("entregas.id_entrega"), nullable=False)
    cantidad_despachada = db.Column(db.Integer, default=1)

    entrega = db.relationship("Entrega")


class Remision(db.Model):
    __tablename__ = "remisiones"

    id_remision = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedidos.id_pedido"))
    id_entrega = db.Column(db.Integer, db.ForeignKey("entregas.id_entrega"))
    id_despacho = db.Column(db.Integer, db.ForeignKey("despachos.id_despacho"))
    numero_remision = db.Column(db.Text, nullable=False, unique=True)
    tipo_remision = db.Column(db.Text)
    ruta_pdf = db.Column(db.Text)
    nombre_archivo = db.Column(db.Text)
    fecha_generacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_genero = db.Column(db.Text)

    def to_dict(self):
        return {
            "id_remision": self.id_remision,
            "id_pedido": self.id_pedido,
            "id_entrega": self.id_entrega,
            "id_despacho": self.id_despacho,
            "numero_remision": self.numero_remision,
            "tipo_remision": self.tipo_remision,
            "ruta_pdf": self.ruta_pdf,
            "nombre_archivo": self.nombre_archivo,
            "fecha_generacion": self.fecha_generacion.isoformat() if self.fecha_generacion else None,
            "usuario_genero": self.usuario_genero,
        }


class TrackingEvento(db.Model):
    __tablename__ = "tracking_eventos"

    id_evento = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedidos.id_pedido"))
    id_entrega = db.Column(db.Integer, db.ForeignKey("entregas.id_entrega"))
    id_despacho = db.Column(db.Integer, db.ForeignKey("despachos.id_despacho"))
    estado_anterior = db.Column(db.Text)
    estado_nuevo = db.Column(db.Text)
    descripcion = db.Column(db.Text)
    usuario = db.Column(db.Text)
    origen = db.Column(db.Text, default="MANUAL")
    fecha_evento = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id_evento": self.id_evento,
            "id_pedido": self.id_pedido,
            "id_entrega": self.id_entrega,
            "id_despacho": self.id_despacho,
            "estado_anterior": self.estado_anterior,
            "estado_nuevo": self.estado_nuevo,
            "descripcion": self.descripcion,
            "usuario": self.usuario,
            "origen": self.origen,
            "fecha_evento": self.fecha_evento.isoformat() if self.fecha_evento else None,
        }


class Notificacion(db.Model):
    __tablename__ = "notificaciones"

    id_notificacion = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedidos.id_pedido"))
    id_entrega = db.Column(db.Integer, db.ForeignKey("entregas.id_entrega"))
    canal = db.Column(db.Text)
    destinatario = db.Column(db.Text)
    asunto = db.Column(db.Text)
    mensaje = db.Column(db.Text)
    estado_envio = db.Column(db.Text, default="PENDIENTE")
    error = db.Column(db.Text)
    fecha_envio = db.Column(db.DateTime)


class Transportadora(db.Model):
    __tablename__ = "transportadoras"

    id_transportadora = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.Text, nullable=False)
    tipo_integracion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    observacion = db.Column(db.Text)

    def to_dict(self):
        return {
            "id_transportadora": self.id_transportadora,
            "nombre": self.nombre,
            "tipo_integracion": self.tipo_integracion,
            "activo": self.activo,
            "observacion": self.observacion,
        }
