from app import db
from datetime import datetime

class Empleado(db.Model):
    __tablename__ = 'empleados'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    cargo = db.Column(db.String(100), nullable=False)
    salario_hora = db.Column(db.Float, nullable=False)
    uid_biometrico = db.Column(db.Integer, unique=True)  # ID del lector ZKTeco
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    asistencias = db.relationship('Asistencia', backref='empleado', lazy=True)
    
    def __repr__(self):
        return f'<Empleado {self.nombre} {self.apellido}>'


class Asistencia(db.Model):
    __tablename__ = 'asistencias'
    
    id = db.Column(db.Integer, primary_key=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora_entrada = db.Column(db.Time, nullable=True)
    hora_salida = db.Column(db.Time, nullable=True)
    tipo_registro = db.Column(db.String(20), default='manual')  # 'manual' o 'biometrico'
    
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
    
    empleado = db.relationship('Empleado')
    
    def calcular_total(self):
        self.total_neto = self.salario_base + self.bonificaciones - self.deducciones
        return self.total_neto