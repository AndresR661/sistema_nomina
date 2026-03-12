from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Usuario, Empleado

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login dual: Admin o Empleado"""
    if current_user.is_authenticated:
        return redirect_user_by_role()
    
    if request.method == 'POST':
        tipo_login = request.form.get('tipo_login', 'admin')
        
        if tipo_login == 'admin':
            # Login de administrador
            username = request.form.get('username')
            password = request.form.get('password')
            
            usuario = Usuario.query.filter_by(username=username, rol='admin', activo=True).first()
            
            if usuario and usuario.check_password(password):
                login_user(usuario)
                flash('Bienvenido, Administrador', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Usuario o contraseña incorrectos', 'danger')
                
        else:
            # Login de empleado (por cédula o código biométrico)
            codigo = request.form.get('codigo_empleado')
            
            # Buscar por cédula o uid_biometrico
            empleado = Empleado.query.filter(
                (Empleado.cedula == codigo) | 
                (Empleado.uid_biometrico == codigo),
                Empleado.activo == True
            ).first()
            
            if empleado:
                # Buscar o crear usuario del empleado
                usuario = Usuario.query.filter_by(empleado_id=empleado.id).first()
                
                if not usuario:
                    # Crear usuario automáticamente para el empleado
                    usuario = Usuario(
                        username=f"emp_{empleado.cedula}",
                        rol='empleado',
                        empleado_id=empleado.id,
                        activo=True
                    )
                    usuario.set_password(empleado.cedula)  # Contraseña temporal = cédula
                    db.session.add(usuario)
                    db.session.commit()
                
                login_user(usuario)
                flash(f'Bienvenido, {empleado.nombre}', 'success')
                return redirect(url_for('empleado.panel'))
            else:
                flash('Empleado no encontrado. Verifique su cédula o código biométrico.', 'danger')
    
    return render_template('auth/login.html')


@auth.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('auth.login'))


def redirect_user_by_role():
    """Redirige al usuario según su rol"""
    if current_user.es_admin():
        return redirect(url_for('admin.dashboard'))
    else:
        return redirect(url_for('empleado.panel'))