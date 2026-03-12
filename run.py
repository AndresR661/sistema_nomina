from app import create_app, db
from app.models import Empleado, Asistencia, Nomina, Usuario, Configuracion

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Empleado': Empleado,
        'Asistencia': Asistencia,
        'Nomina': Nomina,
        'Usuario': Usuario,
        'Configuracion': Configuracion
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)