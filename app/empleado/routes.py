from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models import Empleado, Asistencia, Nomina, Novedad
from datetime import date

empleado = Blueprint('empleado', __name__)


@empleado.route('/panel')
@login_required
def panel():
    """Panel principal del empleado"""
    if current_user.es_admin():
        return redirect(url_for('admin.dashboard'))
    
    # Obtener información del empleado
    empleado = Empleado.query.get(current_user.empleado_id)
    
    if not empleado:
        return "Error: No se encontró información del empleado", 404
    
    # Últimas asistencias
    ultimas_asistencias = Asistencia.query.filter_by(empleado_id=empleado.id).order_by(Asistencia.fecha.desc()).limit(5).all()
    
    # Últimas nóminas
    ultimas_nominas = Nomina.query.filter_by(empleado_id=empleado.id).order_by(Nomina.fecha_calculo.desc()).limit(5).all()
    
    # Últimas novedades
    ultimas_novedades = Novedad.query.filter_by(empleado_id=empleado.id).order_by(Novedad.fecha_solicitud.desc()).limit(5).all()
    
    return render_template('empleado/panel.html',
                         empleado=empleado,
                         ultimas_asistencias=ultimas_asistencias,
                         ultimas_nominas=ultimas_nominas,
                         ultimas_novedades=ultimas_novedades)


@empleado.route('/solicitar-novedad', methods=['POST'])
@login_required
def solicitar_novedad():
    """Solicitar una novedad (vacaciones, incapacidad, etc.)"""
    if current_user.es_admin():
        return redirect(url_for('admin.dashboard'))
    
    try:
        tipo = request.form['tipo']
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        descripcion = request.form.get('descripcion', '')
        
        # Convertir fechas
        from datetime import datetime
        fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        # Calcular días
        dias = (fecha_fin_obj - fecha_inicio_obj).days + 1
        
        if dias <= 0:
            flash('La fecha de fin debe ser posterior a la fecha de inicio', 'danger')
            return redirect(url_for('empleado.panel'))
        
        # Crear novedad
        novedad = Novedad(
            empleado_id=current_user.empleado_id,
            tipo=tipo,
            fecha_inicio=fecha_inicio_obj,
            fecha_fin=fecha_fin_obj,
            dias=dias,
            descripcion=descripcion,
            estado='pendiente'
        )
        
        db.session.add(novedad)
        db.session.commit()
        
        flash(f'Solicitud de {tipo} enviada correctamente. Esperando aprobación.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al enviar solicitud: {str(e)}', 'danger')
    
    return redirect(url_for('empleado.panel'))