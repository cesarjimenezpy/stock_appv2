from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key' 
    
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    
    Bootstrap(app)
    @app.template_filter('format_currency')
    def format_currency(value):
        try:
            return "{:,.0f}".format(float(value))
        except (ValueError, TypeError):
            return value
    with app.app_context():
        from . import routes  # Importar rutas después de que la app esté configurada
        #db.create_all()
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

    return app
