import sys
import os

# Agregar la carpeta raíz al path para poder importar config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configurar login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicie sesión para acceder.'
    login_manager.login_message_category = 'warning'
    
    # Registrar blueprints
    from app.routes import main
    from app.auth import auth
    from app.admin import admin
    from app.empleado import empleado
    
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(empleado, url_prefix='/empleado')
    
    # Crear tablas y usuario admin por defecto
    with app.app_context():
        db.create_all()
        crear_usuario_admin()
        crear_configuracion_default()
    
      # Context processor para variables globales en templates
    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        from app.models import Novedad
        if current_user.is_authenticated and current_user.es_admin():
            novedades_pendientes = Novedad.query.filter_by(estado='pendiente').count()
        else:
            novedades_pendientes = 0
        return dict(novedades_pendientes=novedades_pendientes)

    return app


def crear_usuario_admin():
    """Crea usuario admin por defecto si no existe"""
    from app.models import Usuario
    
    admin = Usuario.query.filter_by(username='admin').first()
    if not admin:
        admin = Usuario(
            username='admin',
            rol='admin',
            activo=True
        )
        admin.set_password('admin123')  # Cambiar en producción
        db.session.add(admin)
        db.session.commit()
        print('✅ Usuario admin creado: usuario=admin, contraseña=admin123')


def crear_configuracion_default():
    """Crea configuración de nómina por defecto"""
    from app.models import Configuracion
    
    config = Configuracion.query.first()
    if not config:
        config = Configuracion()
        db.session.add(config)
        db.session.commit()
        print('✅ Configuración de nómina creada con valores 2026')


@login_manager.user_loader
def load_user(user_id):
    from app.models import Usuario
    return Usuario.query.get(int(user_id))