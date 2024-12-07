from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Crear usuarios de prueba
    # user1 = User(username='cesar', password=generate_password_hash('auto#2021#oferTAS'))
    # user2 = User(username='marcelo', password=generate_password_hash('auto#2021#oferTAS'))
    user2 = User(username='rocio', password=generate_password_hash('auto#2021#oferTAS'))

    # Agregar a la base de datos
    #db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

    print("Usuarios de prueba creados.")
