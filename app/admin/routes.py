from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Empleado, Asistencia, Nomina, Novedad
from datetime import date

admin = Blueprint('admin', __name__)


@admin.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal del administrador"""
    if not current_user.es_admin():
        return redirect(url_for('empleado.panel'))
    
    # Estadísticas
    total_empleados = Empleado.query.filter_by(activo=True).count()
    hoy = date.today()
    asistencias_hoy = Asistencia.query.filter_by(fecha=hoy).count()
    
    return render_template('admin/dashboard.html',
                         total_empleados=total_empleados,
                         asistencias_hoy=asistencias_hoy)


@admin.route('/novedades')
@login_required
def novedades():
    """Gestión de novedades solicitadas por empleados"""
    if not current_user.es_admin():
        return redirect(url_for('empleado.panel'))
    
    # Obtener todas las novedades ordenadas por fecha
    novedades_pendientes = Novedad.query.filter_by(estado='pendiente').order_by(Novedad.fecha_solicitud.desc()).all()
    novedades_historial = Novedad.query.filter(Novedad.estado != 'pendiente').order_by(Novedad.fecha_solicitud.desc()).limit(20).all()
    
    # Contar pendientes para el badge
    total_pendientes = len(novedades_pendientes)
    
    return render_template('admin/novedades.html',
                         novedades_pendientes=novedades_pendientes,
                         novedades_historial=novedades_historial,
                         total_pendientes=total_pendientes)


from flask import request, jsonify
from datetime import datetime


@admin.route('/novedad/<int:id>/aprobar', methods=['POST'])
@login_required
def aprobar_novedad(id):
    """Aprobar una novedad"""
    if not current_user.es_admin():
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    
    try:
        novedad = Novedad.query.get_or_404(id)
        novedad.estado = 'aprobada'
        novedad.fecha_respuesta = datetime.utcnow()
        novedad.respuesta_admin = 'Aprobada por administrador'
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Novedad aprobada'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin.route('/novedad/<int:id>/rechazar', methods=['POST'])
@login_required
def rechazar_novedad(id):
    """Rechazar una novedad"""
    if not current_user.es_admin():
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    
    try:
        data = request.get_json()
        motivo = data.get('motivo', 'Rechazada por administrador')
        
        novedad = Novedad.query.get_or_404(id)
        novedad.estado = 'rechazada'
        novedad.fecha_respuesta = datetime.utcnow()
        novedad.respuesta_admin = motivo
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Novedad rechazada'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    
    from flask import current_app

@admin.app_context_processor
def inject_novedades_count():
    """Inyecta el conteo de novedades pendientes en todos los templates"""
    def get_novedades_pendientes_count():
        if current_user.is_authenticated and current_user.es_admin():
            return Novedad.query.filter_by(estado='pendiente').count()
        return 0
    return dict(novedades_pendientes_count=get_novedades_pendientes_count)

