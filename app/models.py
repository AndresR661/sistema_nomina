from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Empleado(db.Model):
    __tablename__ = 'empleados'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    cargo = db.Column(db.String(100), nullable=False)
    salario_hora = db.Column(db.Float, nullable=False)
    uid_biometrico = db.Column(db.Integer, unique=True, nullable=True)
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    asistencias = db.relationship('Asistencia', backref='empleado', lazy=True)
    nominas = db.relationship('Nomina', backref='empleado', lazy=True)
    usuario = db.relationship('Usuario', backref='empleado', uselist=False)
    
    def __repr__(self):
        return f'<Empleado {self.nombre} {self.apellido}>'


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), default='empleado')  # 'admin' o 'empleado'
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados.id'), nullable=True)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def es_admin(self):
        return self.rol == 'admin'
    
    def __repr__(self):
        return f'<Usuario {self.username} - {self.rol}>'


class Asistencia(db.Model):
    __tablename__ = 'asistencias'
    
    id = db.Column(db.Integer, primary_key=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora_entrada = db.Column(db.Time, nullable=True)
    hora_salida = db.Column(db.Time, nullable=True)
    tipo_registro = db.Column(db.String(20), default='manual')
    
    def __repr__(self):
        return f'<Asistencia {self.empleado_id} - {self.fecha}>'


class Nomina(db.Model):
    __tablename__ = 'nominas'
    
    id = db.Column(db.Integer, primary_key=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados.id'), nullable=False)
    periodo_inicio = db.Column(db.Date, nullable=False)
    periodo_fin = db.Column(db.Date, nullable=False)
    horas_trabajadas = db.Column(db.Float, default=0)
    salario_base = db.Column(db.Float, default=0)
    bonificaciones = db.Column(db.Float, default=0)
    deducciones = db.Column(db.Float, default=0)
    total_neto = db.Column(db.Float, default=0)
    fecha_calculo = db.Column(db.DateTime, default=datetime.utcnow)
    
    def calcular_total(self):
        self.total_neto = self.salario_base + self.bonificaciones - self.deducciones
        return self.total_neto


class Configuracion(db.Model):
    __tablename__ = 'configuracion'
    
    id = db.Column(db.Integer, primary_key=True)
    smmlv = db.Column(db.Float, default=1750905)  # 2026
    auxilio_transporte = db.Column(db.Float, default=249095)  # 2026
    uvt = db.Column(db.Float, default=42412)  # 2026
    porcentaje_salud_empleado = db.Column(db.Float, default=4.0)
    porcentaje_pension_empleado = db.Column(db.Float, default=4.0)
    porcentaje_salud_empleador = db.Column(db.Float, default=8.5)
    porcentaje_pension_empleador = db.Column(db.Float, default=12.0)
    porcentaje_cesantias = db.Column(db.Float, default=8.33)
    porcentaje_prima = db.Column(db.Float, default=8.33)
    porcentaje_vacaciones = db.Column(db.Float, default=4.17)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)


class Novedad(db.Model):
    __tablename__ = 'novedades'
    
    id = db.Column(db.Integer, primary_key=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # 'vacacion', 'incapacidad', 'licencia', 'permiso'
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    dias = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    estado = db.Column(db.String(20), default='pendiente')  # 'pendiente', 'aprobada', 'rechazada'
    archivo_soporte = db.Column(db.String(255), nullable=True)
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_respuesta = db.Column(db.DateTime, nullable=True)
    respuesta_admin = db.Column(db.Text, nullable=True)
    
    empleado = db.relationship('Empleado', backref='novedades')
    
    def calcular_dias(self):
        """Calcula los días entre fecha_inicio y fecha_fin"""
        from datetime import timedelta
        return (self.fecha_fin - self.fecha_inicio).days + 1