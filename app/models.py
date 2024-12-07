from . import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_chasis = db.Column(db.String(100), nullable=True)
    marca_id = db.Column(db.Integer, db.ForeignKey('marca.id'), nullable=False)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelo.id'), nullable=False)
    año_fabricacion = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(50), nullable=False)
    gastos = db.relationship('Gasto', backref='producto', lazy=True)
    precio_venta = db.Column(db.Float, nullable=False) 
    marca = db.relationship('Marca', backref='productos', lazy=True)
    modelo = db.relationship('Modelo', backref='productos', lazy=True)
    ubicacion = db.Column(db.String(100), nullable=True)

    def calcular_costo(self):
        #return sum(gasto.monto * (1 if gasto.moneda == 'PYG' else gasto.tasa_cambio or 1) for gasto in self.gastos)
        total_gastos = sum(gasto.monto for gasto in self.gastos)
        return total_gastos
    @property
    def descripcion(self):
        return f"{self.marca.nombre} {self.modelo.nombre} {self.año_fabricacion} {self.color} {self.numero_chasis}"
    def __repr__(self):
        return f'<Producto {self.nombre}>'
    @property
    def marca_nombre(self):
        return self.marca.nombre if self.marca else "No disponible"

    @property
    def modelo_nombre(self):
        return self.modelo.nombre if self.modelo else "No disponible"

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    numero_documento = db.Column(db.String(50), nullable=False, unique=True)
    telefono = db.Column(db.String(20), nullable=True)  # Nuevo campo agregado

class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    producto = db.relationship('Producto', backref='ventas', lazy=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    cliente = db.relationship('Cliente', backref='ventas', lazy=True)
    tipo_pago = db.Column(db.String(20), nullable=False)  # 'contado' o 'credito'
    codigo_interno = db.Column(db.String(10), nullable=True)  
    entrega_inicial = db.Column(db.Float, nullable=True)
    total = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    cuotas = db.relationship('Cuota', backref='venta', cascade='all, delete-orphan', passive_deletes=True)
    @property
    def saldo(self):
        if self.tipo_pago == 'contado':
            return 0
        try:
            print(f'calculando cuotas pagadas venta {self.id}')
            total_cuotas_pagadas = sum(cuota.importe for cuota in self.cuotas if cuota.pagado)
            total_cuotas = sum(cuota.importe for cuota in self.cuotas)
            return (total_cuotas + (self.entrega_inicial or 0)) - total_cuotas_pagadas - (self.entrega_inicial or 0)
        except Exception as e:
            print(f"Error al calcular saldo de la venta {self.id}, asignando 0. Detalles: {e}")
            return 0

class Cuota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id', ondelete='CASCADE'), nullable=False)
    #venta = db.relationship('Venta', backref=db.backref('cuotas', lazy=True))
    importe = db.Column(db.Float, nullable=False)
    fecha_vencimiento = db.Column(db.DateTime, nullable=False)
    fecha_pago = db.Column(db.DateTime, nullable=True)
    pagado = db.Column(db.Boolean, default=False)
    tipo_pago = db.Column(db.String(50), nullable=True)  # Nuevo campo agregado
    @property
    def numero_pagare(self):
        """Devuelve el número de pagaré en formato X/Y."""
        # Obtener todas las cuotas de la venta ordenadas por fecha de vencimiento
        cuotas = sorted(self.venta.cuotas, key=lambda c: c.fecha_vencimiento)
        
        # Encontrar la posición actual
        posicion = cuotas.index(self) + 1  # +1 para que el índice empiece en 1
        total = len(cuotas)
        
        return f"{posicion}/{total}"
# Modelo para Marca
class Marca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    modelos = db.relationship('Modelo', backref='marca', lazy=True)

    def __repr__(self):
        return f'<Marca {self.nombre}>'

# Modelo para Modelo
class Modelo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    marca_id = db.Column(db.Integer, db.ForeignKey('marca.id'), nullable=False)

    def __repr__(self):
        return f'<Modelo {self.nombre}>'

# Modelo para Detalle de Gasto
class Gasto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(200), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    moneda = db.Column(db.String(10), nullable=False)  # 'USD' o 'PYG'
    tasa_cambio = db.Column(db.Float, nullable=True)  # Solo para 'USD'
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)

    def __repr__(self):
        return f'<Gasto {self.descripcion} - {self.monto} {self.moneda}>'
class PagoCuota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cuota_id = db.Column(db.Integer, db.ForeignKey('cuota.id'), nullable=False)
    monto_pago = db.Column(db.Float, nullable=False)
    fecha_pago = db.Column(db.Date, nullable=False)
    cuota = db.relationship('Cuota', backref='pagos')

    def __repr__(self):
        return f'<PagoCuota {self.id}>'

class SeguimientoVenta(db.Model):
    __tablename__ = 'seguimiento_venta'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_proximo_contacto = db.Column(db.Date, nullable=True)  # Asegúrate de que este campo existe
    detalle = db.Column(db.String(255), nullable=False)
    
    cliente = db.relationship('Cliente', backref=db.backref('seguimientos_venta', lazy=True))

    def __init__(self, cliente_id, detalle, fecha=None, fecha_proximo_contacto=None):
        self.cliente_id = cliente_id
        self.detalle = detalle
        if fecha is not None:
            self.fecha = fecha
        if fecha_proximo_contacto is not None:
            self.fecha_proximo_contacto = fecha_proximo_contacto

class SeguimientoCobranza(db.Model):
    __tablename__ = 'seguimiento_cobranza'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    detalle = db.Column(db.String(255), nullable=False)

    cliente = db.relationship('Cliente', backref=db.backref('seguimientos_cobranza', lazy=True))

    def __init__(self, cliente_id, detalle, fecha):
        self.cliente_id = cliente_id
        self.detalle = detalle
        if fecha is not None:
            self.fecha = fecha
class Concepto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'ingreso' o 'egreso'

class Ingreso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    concepto_id = db.Column(db.Integer, db.ForeignKey('concepto.id'), nullable=False)
    concepto = db.relationship('Concepto', backref=db.backref('ingresos', lazy=True))
    descripcion = db.Column(db.String(255), nullable=False)  # 'PYG' o 'USD'
    fecha = db.Column(db.Date, nullable=False)
    importe = db.Column(db.Float, nullable=False)
    moneda = db.Column(db.String(10), nullable=False)  # 'PYG' o 'USD'
    tasa_cambio = db.Column(db.Float, default=1.0)
    
class Egreso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    concepto_id = db.Column(db.Integer, db.ForeignKey('concepto.id'), nullable=False)
    concepto = db.relationship('Concepto', backref=db.backref('egresos', lazy=True))
    descripcion = db.Column(db.String(255), nullable=False)  # 'PYG' o 'USD'
    fecha = db.Column(db.Date, nullable=False)
    importe = db.Column(db.Float, nullable=False)
    moneda = db.Column(db.String(10), nullable=False)  # 'PYG' o 'USD'
    tasa_cambio = db.Column(db.Float, default=1.0)