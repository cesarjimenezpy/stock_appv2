from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from config import Config
import re

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    login_manager = LoginManager()
    app.config.from_object(Config)
    # Configuración de LoginManager
    login_manager.init_app(app)
    login_manager.login_view = 'login'  # Nombre de la vista para el login
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    
    Bootstrap(app)
    @app.template_filter('format_currency')
    def format_currency(value):
        try:
            return "{:,.0f}".format(float(value))
        except (ValueError, TypeError):
            return value
    # with app.app_context():
    #     from . import routes  # Importar rutas después de que la app esté configurada
    #     #db.create_all()
    @app.template_filter('number_format')
    def number_format(value, decimal_places=0):
        """Formatea un número a un formato específico con separadores de miles."""
        if value is None:
            return ''
        try:
            formatted_value = f"{value:,.{decimal_places}f}"
            return formatted_value
        except (ValueError, TypeError):
            return value

    def limpiar_valor(valor):
        try:
            # Convertir a cadena por si viene en otro formato
            valor_str = str(valor)
            
            # Eliminar todo lo que no sean números o puntos
            valor_limpio = re.sub(r'[^\d.]', '', valor_str)
            
            # Si hay más de un punto, significa que probablemente es un separador de miles
            # Eliminar todos los puntos, excepto el último (que debe ser el decimal)
            if valor_limpio.count('.') > 1:
                partes = valor_limpio.split('.')
                valor_limpio = ''.join(partes[:-1]) + '.' + partes[-1]  # Mantener solo el último punto como decimal
            
            return float(valor_limpio) if valor_limpio else 0
        except Exception as e:
            print(f"Error al limpiar valor: {valor}, asignando 0. Detalles: {e}")
            return 0
    # Cargar el modelo de usuario
    from .models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        # Importar rutas después de que la app esté configurada
    with app.app_context():
        from . import routes
    app.jinja_env.globals.update(limpiar_valor=limpiar_valor)
    return app
