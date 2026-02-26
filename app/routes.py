from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models import Empleado, Asistencia, Nomina
from datetime import datetime, date, time
from zk import ZK

main = Blueprint('main', __name__)

# ==================== RUTAS PRINCIPALES ====================

@main.route('/')
def index():
    total_empleados = Empleado.query.filter_by(activo=True).count()
    hoy = date.today()
    asistencias_hoy = Asistencia.query.filter_by(fecha=hoy).count()
    return render_template('index.html', 
                         total_empleados=total_empleados,
                         asistencias_hoy=asistencias_hoy)

# ==================== EMPLEADOS ====================

@main.route('/empleados')
def empleados():
    empleados = Empleado.query.filter_by(activo=True).all()
    # Convertir a diccionarios para JSON
    empleados_json = [{
        'id': e.id,
        'nombre': e.nombre,
        'apellido': e.apellido,
        'cedula': e.cedula,
        'cargo': e.cargo,
        'salario_hora': e.salario_hora,
        'uid_biometrico': e.uid_biometrico,
        'fecha_registro': e.fecha_registro.isoformat() if e.fecha_registro else None
    } for e in empleados]
    return render_template('empleados.html', empleados=empleados, empleados_json=empleados_json)

@main.route('/empleados/nuevo', methods=['POST'])
def nuevo_empleado():
    try:
        empleado = Empleado(
            nombre=request.form['nombre'],
            apellido=request.form['apellido'],
            cedula=request.form['cedula'],
            cargo=request.form['cargo'],
            salario_hora=float(request.form['salario_hora']),
            uid_biometrico=int(request.form['uid_biometrico']) if request.form['uid_biometrico'] else None
        )
        db.session.add(empleado)
        db.session.commit()
        flash('Empleado registrado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar empleado: {str(e)}', 'danger')
    return redirect(url_for('main.empleados'))

@main.route('/empleados/editar/<int:id>', methods=['POST'])
def editar_empleado(id):
    empleado = Empleado.query.get_or_404(id)
    try:
        empleado.nombre = request.form['nombre']
        empleado.apellido = request.form['apellido']
        empleado.cedula = request.form['cedula']
        empleado.cargo = request.form['cargo']
        empleado.salario_hora = float(request.form['salario_hora'])
        empleado.uid_biometrico = int(request.form['uid_biometrico']) if request.form['uid_biometrico'] else None
        db.session.commit()
        flash('Empleado actualizado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar empleado: {str(e)}', 'danger')
    return redirect(url_for('main.empleados'))

@main.route('/empleados/eliminar/<int:id>')
def eliminar_empleado(id):
    empleado = Empleado.query.get_or_404(id)
    try:
        empleado.activo = False
        db.session.commit()
        flash('Empleado desactivado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al desactivar empleado: {str(e)}', 'danger')
    return redirect(url_for('main.empleados'))

# ==================== ASISTENCIA ====================

@main.route('/asistencia')
def asistencia():
    hoy = date.today()
    registros = Asistencia.query.filter_by(fecha=hoy).order_by(Asistencia.hora_entrada.desc()).all()
    empleados = Empleado.query.filter_by(activo=True).all()
    return render_template('asistencia.html', registros=registros, empleados=empleados, hoy=hoy)

@main.route('/asistencia/registrar', methods=['POST'])
def registrar_asistencia():
    try:
        empleado_id = request.form['empleado_id']
        tipo = request.form['tipo']  # 'entrada' o 'salida'
        
        hoy = date.today()
        ahora = datetime.now().time()
        
        # Buscar registro de hoy
        registro = Asistencia.query.filter_by(
            empleado_id=empleado_id,
            fecha=hoy
        ).first()
        
        if tipo == 'entrada':
            if registro and registro.hora_entrada:
                flash('El empleado ya registró entrada hoy', 'warning')
            else:
                if not registro:
                    registro = Asistencia(
                        empleado_id=empleado_id,
                        fecha=hoy,
                        hora_entrada=ahora,
                        tipo_registro='manual'
                    )
                    db.session.add(registro)
                else:
                    registro.hora_entrada = ahora
                db.session.commit()
                flash('Entrada registrada exitosamente', 'success')
                
        elif tipo == 'salida':
            if not registro or not registro.hora_entrada:
                flash('El empleado no tiene entrada registrada hoy', 'warning')
            elif registro.hora_salida:
                flash('El empleado ya registró salida hoy', 'warning')
            else:
                registro.hora_salida = ahora
                db.session.commit()
                flash('Salida registrada exitosamente', 'success')
                
    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar asistencia: {str(e)}', 'danger')
    
    return redirect(url_for('main.asistencia'))

# ==================== BIOMÉTRICO ====================

@main.route('/biometrico/conectar', methods=['POST'])
def conectar_biometrico():
    try:
        ip = request.json.get('ip', '192.168.1.201')
        puerto = request.json.get('puerto', 4370)
        
        zk = ZK(ip, port=puerto, timeout=5)
        conn = zk.connect()
        
        if conn:
            conn.disconnect()
            return jsonify({'success': True, 'message': 'Conexión exitosa con el lector biométrico'})
        else:
            return jsonify({'success': False, 'message': 'No se pudo conectar al lector'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@main.route('/biometrico/sincronizar', methods=['POST'])
def sincronizar_biometrico():
    try:
        ip = request.json.get('ip', '192.168.1.201')
        puerto = request.json.get('puerto', 4370)
        
        zk = ZK(ip, port=puerto, timeout=5)
        conn = zk.connect()
        
        if not conn:
            return jsonify({'success': False, 'message': 'No se pudo conectar al lector'})
        
        # Obtener usuarios del lector
        usuarios = conn.get_users()
        conn.disconnect()
        
        return jsonify({
            'success': True, 
            'message': f'Sincronización completada. {len(usuarios)} usuarios encontrados.',
            'usuarios': [{'uid': u.uid, 'nombre': u.name} for u in usuarios]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

# ==================== NÓMINA ====================

@main.route('/nomina')
def nomina():
    empleados = Empleado.query.filter_by(activo=True).all()
    nominas = Nomina.query.order_by(Nomina.fecha_calculo.desc()).limit(10).all()
    return render_template('nomina.html', empleados=empleados, nominas=nominas)

@main.route('/nomina/calcular', methods=['POST'])
def calcular_nomina():
    try:
        empleado_id = request.form['empleado_id']
        fecha_inicio = datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(request.form['fecha_fin'], '%Y-%m-%d').date()
        
        empleado = Empleado.query.get_or_404(empleado_id)
        
        # Calcular horas trabajadas en el periodo
        asistencias = Asistencia.query.filter(
            Asistencia.empleado_id == empleado_id,
            Asistencia.fecha >= fecha_inicio,
            Asistencia.fecha <= fecha_fin,
            Asistencia.hora_entrada != None,
            Asistencia.hora_salida != None
        ).all()
        
        horas_totales = 0
        for asistencia in asistencias:
            entrada = datetime.combine(date.min, asistencia.hora_entrada)
            salida = datetime.combine(date.min, asistencia.hora_salida)
            diferencia = salida - entrada
            horas_totales += diferencia.total_seconds() / 3600
        
        # Calcular salario
        salario_base = horas_totales * empleado.salario_hora
        
        nomina = Nomina(
            empleado_id=empleado_id,
            periodo_inicio=fecha_inicio,
            periodo_fin=fecha_fin,
            horas_trabajadas=round(horas_totales, 2),
            salario_base=round(salario_base, 2),
            bonificaciones=float(request.form.get('bonificaciones', 0)),
            deducciones=float(request.form.get('deducciones', 0))
        )
        nomina.calcular_total()
        
        db.session.add(nomina)
        db.session.commit()
        
        flash(f'Nómina calculada. Total neto: ${nomina.total_neto:.2f}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al calcular nómina: {str(e)}', 'danger')
    
    return redirect(url_for('main.nomina'))