from sqlite3 import IntegrityError
from flask import jsonify, render_template, redirect, url_for, request, flash, current_app, Flask, send_file
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import extract
from . import db
from .models import Concepto, Egreso, Ingreso, Producto, Cliente, SeguimientoCobranza, SeguimientoVenta, User, Venta, Cuota,Marca, Modelo, Gasto, PagoCuota
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime
#import pandas as pd
import io
#from openpyxl import Workbook
#from pyexcel_ods3 import save_data

@current_app.route('/login', methods=['GET', 'POST'])
@current_app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            user = User.query.filter_by(username=username).first()

            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('index'))
            else:  # Mensaje para credenciales inválidas
                flash('Credenciales inválidas. Por favor, inténtalo de nuevo.', 'danger') # Usando flash

        return render_template('login.html')

    except Exception as e:  # Captura cualquier excepción no controlada
        error_message = str(e)  # Convierte el error a string

        # Dos opciones para mostrar el error:

        # 1. Mostrar mensaje flash en la página (recomendado para usuarios):
        flash(f'Ocurrió un error: {error_message}', 'danger')  # Flash message
        return render_template('login.html')  # Renderiza la página de login para que el usuario vea el mensaje

        # 2. Imprimir en la consola (útil para desarrollo y depuración):
        print(f"Error en la ruta /login: {error_message}") # Imprime en la consola del servidor
        # También puedes usar current_app.logger.error(f"Error en /login: {error_message}") para un mejor manejo de logs
        return render_template('login.html') # O podrías redirigir a una página de error genérica si lo deseas

@current_app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
@current_app.route('/')
@login_required
def index():
    productos = Producto.query.all()
    return render_template('index.html', productos=productos)

@current_app.route('/producto/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_producto():
    if request.method == 'POST':
        try:
            print("Form Data:", request.form)
            #print("Files Data:", request.files)
            #print("Request Data:", request.data)
            #print("Request JSON:", request.json)
            # Recopilar datos del formulario
            numero_chasis = request.form.get('numero_chasis')
            marca_id = request.form.get('marca_id')
            modelo_id = request.form.get('modelo_id')
            año_fabricacion = request.form.get('año_fabricacion')
            color = request.form.get('color')
            precio_venta = request.form.get('precio_venta')
            ubicacion = request.form.get('ubicacion')
            # Crear instancia del Producto
            nuevo_producto = Producto(
                numero_chasis=numero_chasis,
                marca_id=marca_id,
                modelo_id=modelo_id,
                año_fabricacion=int(año_fabricacion),
                color=color,
                precio_venta=float(precio_venta),
                ubicacion=ubicacion
            )
            db.session.add(nuevo_producto)
            db.session.commit()  # Commit para obtener el ID del producto
            
            # Procesar detalles de gastos
            descripciones = request.form.getlist('descripcion[]')
            montos = request.form.getlist('monto[]')
            monedas = request.form.getlist('moneda[]')
            tasas_cambio = request.form.getlist('tasa_cambio[]')
            for descripcion, monto, moneda, tasa_cambio in zip(descripciones, montos, monedas, tasas_cambio):
                if descripcion and monto and moneda:
                    nuevo_gasto = Gasto(
                        producto_id=nuevo_producto.id,
                        descripcion=descripcion,
                        monto=float(monto),
                        moneda=moneda,
                        tasa_cambio=float(tasa_cambio) if moneda == 'USD' and tasa_cambio else None
                    )
                    db.session.add(nuevo_gasto)
            
            db.session.commit()
            flash('Producto y gastos registrados exitosamente!', 'success')
            return redirect(url_for('lista_productos'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar el producto y los gastos: {str(e)}', 'danger')
            #return redirect(url_for('nuevo_producto'))
    
    # Cargar marcas y modelos para el formulario
    marcas = Marca.query.all()
    modelos = Modelo.query.all()
    return render_template('nuevo_producto.html', marcas=marcas, modelos=modelos)

@current_app.route('/informes_stock')
@login_required
def informes_stock():
    productos = Producto.query.all()
    return render_template('informes_stock.html', productos=productos)

@current_app.route('/estado_cuentas_clientes')
@login_required
def estado_cuentas_clientes():
    clientes = Cliente.query.all()
    return render_template('estado_cuentas_clientes.html', clientes=clientes)

@current_app.route('/marca/nueva', methods=['POST'])
@login_required
def nueva_marca():
    nombre = request.form.get('nombre')
    marca = Marca(nombre=nombre)
    db.session.add(marca)
    db.session.commit()
    return redirect(url_for('nuevo_producto'))

@current_app.route('/modelo/nuevo', methods=['POST'])
@login_required
def nuevo_modelo():
    nombre = request.form.get('nombre')
    marca_id = request.form.get('marca_id')
    modelo = Modelo(nombre=nombre, marca_id=marca_id)
    db.session.add(modelo)
    db.session.commit()
    return redirect(url_for('nuevo_producto'))

@current_app.route('/crear_cliente', methods=['GET', 'POST'])
@login_required
def crear_cliente():
    if request.method=="POST":
        try:
            nombre = request.form.get('nombre')
            apellido = request.form.get('apellido')
            direccion = request.form.get('direccion')
            fecha_nacimiento_str = request.form.get('fecha_nacimiento')
            numero_documento = request.form.get('numero_documento')
            telefono = request.form.get('telefono')  # Nuevo campo
            # Convertir la cadena de fecha a un objeto datetime.date
            fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()

            cliente = Cliente(
                nombre=nombre,
                apellido=apellido,
                direccion=direccion,
                fecha_nacimiento=fecha_nacimiento,
                numero_documento=numero_documento,
                telefono= telefono
            )
            db.session.add(cliente)
            db.session.commit()

            return redirect(url_for('gestionar_cliente', cliente_id=cliente.id))

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    else:
        return render_template('crear_cliente.html')
    
def calcular_dias_atraso(venta):
    dias_atraso = 0
    for cuota in venta.cuotas:
        if cuota.fecha_vencimiento.date() < datetime.now().date() and not cuota.pagado:
            print(f'iterando por cuotas de venta {venta.id}')
            dias_atraso += (datetime.now().date() - cuota.fecha_vencimiento.date()).days
    print(f'Dias de atraso de venta {venta.id} {dias_atraso}')
    return dias_atraso 
def obtener_valor_o_cero(valor):
    return float(valor) if valor is not None else 0.0
@current_app.route('/consultar_ventas')
@login_required
def consultar_ventas():
    ventas = Venta.query.order_by(Venta.fecha).all()
    for venta in ventas:
        print(f"Calculando dias de atraso {venta.id}")
        venta.dias_atraso = calcular_dias_atraso(venta)  # Añade los días de atraso a cada venta
    # for venta in ventas:
    #     if venta.tipo_pago == 'credito':
    #         # Maneja valores None al convertir a float
    #         cuotas_pagadas = sum(obtener_valor_o_cero(cuota.importe) for cuota in venta.cuotas if cuota.pagado)
    #         entrega_inicial = obtener_valor_o_cero(venta.entrega_inicial)
    #         total = obtener_valor_o_cero(venta.total)
    #         saldo = total - (cuotas_pagadas + entrega_inicial)
    #     else:
    #         saldo = 0  # Ventas al contado siempre tienen saldo 0

    #     venta.saldo = saldo
    return render_template('consultar_ventas.html', ventas=ventas)

@current_app.route('/venta/nueva', methods=['GET', 'POST'])
@login_required
def nueva_venta():
    cliente_id = request.args.get('cliente_id')  # Obtener el ID del cliente si se pasa como parámetro
    cliente = None
    if cliente_id:
        cliente = Cliente.query.get(cliente_id)  # Obtener los detalles del cliente
    if request.method == 'GET':
        productos = Producto.query.all()
        clientes = Cliente.query.all()
        cliente_id = request.args.get('cliente_id')  # Obtener el ID del cliente si se pasa como parámetro
        cliente = None
        if cliente_id:
            cliente = Cliente.query.get(cliente_id)  # Obtener los detalles del cliente
        return render_template('nueva_venta.html', productos=productos, clientes=clientes, cliente=cliente)
    print("itentando registrar venta")
    if request.method == 'POST':
        print("itentando registrar venta")
        try:
            producto_id = request.form.get('producto_id')
            cliente_id = request.form.get('cliente_id')
            tipo_pago = request.form.get('tipo_pago')
            codigo_interno = request.form.get('codigo_interno')
            total = request.form.get('total').replace(',', '').replace('.', '')  # Eliminar comas para convertir a float
            entrega_inicial = 0
            total = round(float(total))
            fecha_venta_str = request.form.get('fecha_venta')
            fecha_venta = datetime.strptime(fecha_venta_str, '%Y-%m-%d')
            # Verificar si se envió información de cuotas para ventas a crédito
            cuotas = []
            if tipo_pago == 'credito':
                importes = request.form.getlist('importe_cuota[]')
                #datetime.strptime(vencimiento, '%Y-%m-%d')
                vencimientos = request.form.getlist('vencimiento_cuota[]')
                #datetime.strptime(vencimiento, '%Y-%m-%d').date()
                entrega_inicial = request.form.get('entrega_inicial').replace(',', '').replace('.', '')
                for importe, vencimiento in zip(importes, vencimientos):
                    cuotas.append(Cuota(importe=float(importe), fecha_vencimiento=datetime.strptime(vencimiento, '%Y-%m-%d').date()))

            venta = Venta(
                producto_id=producto_id,
                cliente_id=cliente_id,
                tipo_pago=tipo_pago,
                total=float(total),
                entrega_inicial=float(entrega_inicial),
                codigo_interno=codigo_interno,
                fecha=fecha_venta  # Asigna la fecha actual
            )
            db.session.add(venta)
            db.session.commit()
            
            producto = Producto.query.get(producto_id)
            if producto:
                producto.ubicacion = "VENDIDO"
                db.session.add(producto)

            db.session.commit()
            if tipo_pago == 'credito':
                for cuota in cuotas:
                    cuota.venta_id = venta.id
                    db.session.add(cuota)
                db.session.commit()
            # Obtener nombre y apellido del cliente
            cliente = Cliente.query.get(cliente_id)
            cliente_nombre = f"{cliente.nombre} {cliente.apellido}" if cliente else "N/A"

            # Determinar el concepto del ingreso
            concepto_nombre = ''
            descripcion = f"Venta {codigo_interno} - Cliente: {cliente_nombre}"
            monto = 0
            moneda ='PYG'
            tasa_cambio = 1
            if tipo_pago == 'contado':
                concepto_nombre = 'VENTA CONTADO'
                monto = total
            elif tipo_pago == 'credito' and float(entrega_inicial) > 0:
                concepto_nombre = 'ENTREGA INICIAL'
                monto = float(entrega_inicial)

            # Buscar el ID del concepto por nombre
            if concepto_nombre:  # Solo buscar si hay un concepto definido
                concepto = Concepto.query.filter_by(nombre=concepto_nombre, tipo='ingreso').first()
                if concepto:
                    ingreso = Ingreso(
                        concepto_id=concepto.id,
                        importe=monto,
                        moneda = moneda,
                        tasa_cambio = tasa_cambio,
                        descripcion=descripcion,
                        fecha=fecha_venta  # O cualquier otra fecha que quieras usar para el registro
                    )
                    db.session.add(ingreso)
                    db.session.commit()
                else:
                    print(f'Error: No se encontró un concepto de ingreso llamado "{concepto_nombre}".')
                    flash(f'Error: No se encontró un concepto de ingreso llamado "{concepto_nombre}".', 'danger')

            flash('Venta registrada exitosamente.', 'success')
            return redirect(url_for('index'))
            #return jsonify({'status': 'success'})
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la venta: {e}', 'danger')
            print(f'Error al registrar la venta: {e}')
            return jsonify({'status': 'error', 'message': str(e)}), 400
    
    #productos = Producto.query.all()
    #clientes = Cliente.query.all()
    #return render_template('nueva_venta.html', productos=productos, clientes=clientes)

@current_app.route('/consultar_cuotas', methods=['GET'])
@login_required
def consultar_cuotas():
    # Obtener todas las cuotas y ordenarlas por fecha de vencimiento
    cuotas = Cuota.query.join(Venta).order_by(Cuota.fecha_vencimiento).all()
    current_time = datetime.now()
    # Renderizar el template con el listado completo de cuotas
    return render_template('consultar_cuotas.html', cuotas=cuotas, current_time=current_time)
@current_app.route('/producto/editar/<int:producto_id>', methods=['GET', 'POST'])
@login_required
def editar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    marcas = Marca.query.all()
    modelos = Modelo.query.all()
    
    if request.method == 'POST':
        producto.numero_chasis = request.form['numero_chasis']
        producto.marca_id = request.form['marca_id']
        producto.modelo_id = request.form['modelo_id']
        producto.año_fabricacion = request.form['año_fabricacion']
        producto.color = request.form['color']
        producto.precio_venta = float(request.form['precio_venta'])
        
       # Eliminar gastos existentes asociados al producto
        Gasto.query.filter_by(producto_id=producto_id).delete()
        
        # Recuperar los datos de los gastos del formulario
        descripciones = request.form.getlist('descripcion[]')
        montos = request.form.getlist('monto[]')
        monedas = request.form.getlist('moneda[]')
        tasas_cambio = request.form.getlist('tasa_cambio[]')
        print(f'descripciones de gastos {descripciones}')
        print(f'montos de gastos {montos}')
        print(f'monedas {monedas}')
        print(f'tasas_cambio {tasas_cambio}')
        if not descripciones:
            flash('Debe proporcionar al menos un gasto.', 'danger')
            return render_template('nuevo_producto.html', producto=producto, marcas=marcas, modelos=modelos)
        
        for descripcion, monto, moneda, tasa_cambio in zip(descripciones, montos, monedas, tasas_cambio):
            if monto:  # Solo agregar si el monto no está vacío
                monto = float(monto)
                if moneda == 'USD' and tasa_cambio:
                    tasa_cambio = float(tasa_cambio)
                else:
                    tasa_cambio = 1  # Si la moneda es PY, tasa de cambio es 1
                
                print(f'Datos de gasto a actualizar: {producto_id} {descripcion} {monto} {moneda} {tasa_cambio}')
                nuevo_gasto = Gasto(
                    producto_id=producto_id,
                    descripcion=descripcion,
                    monto=monto,
                    moneda=moneda,
                    tasa_cambio=tasa_cambio
                )
                db.session.add(nuevo_gasto)
        
        try:
            db.session.commit()
            flash('Producto actualizado correctamente.', 'success')
            print('Producto actualizado correctamente.')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            print(f'Error al actualizar el producto: {e}')
            flash(f'Error al actualizar el producto: {e}', 'danger')
    else:
        return render_template('nuevo_producto.html', producto=producto, marcas=marcas, modelos=modelos)
@current_app.route('/buscar_producto', methods=['GET'])
@login_required
def buscar_producto():
    numero_chasis = request.args.get('numero_chasis')
    if not numero_chasis:
        return jsonify({'error': 'Número de chasis es requerido'}), 400

    producto = Producto.query.filter_by(numero_chasis=numero_chasis).first()
    if producto:
        try:
            response = {
                'id': producto.id,
                'descripcion': f"{producto.marca.nombre} {producto.modelo.nombre} {producto.año_fabricacion} {producto.color} {producto.numero_chasis}",
                'precio_venta': producto.precio_venta
            }
            return jsonify(response)
        except Exception as e:
            print(f'Error al buscar producto: {e}')
            
    else:
        return jsonify({'error': 'Producto no encontrado'}), 404
@current_app.route('/producto/eliminar/<int:producto_id>', methods=['POST'])
@login_required
def eliminar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
   
    try:
        gastos = Gasto.query.filter_by(producto_id=producto_id).all()
        for gasto in gastos:
                db.session.delete(gasto)
         # Eliminar ventas relacionadas
        ventas = Venta.query.filter_by(producto_id=producto_id).all()
        for venta in ventas:
            cuotas = Cuota.query.filter_by(venta_id=venta.id).all()
            for cuota in cuotas:
                db.session.delete(cuota)
            db.session.delete(venta)
        db.session.delete(producto)
        db.session.commit()
        return jsonify({'success': True})
    except IntegrityError as e:
        db.session.rollback()  # Revertir la transacción en caso de error
        return jsonify({'error': 'No se puede eliminar el producto. Tiene referencias en otras tablas.'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
    return redirect(url_for('index'))
@current_app.route('/cliente/gestionar', methods=['GET', 'POST'])
@login_required
def gestionar_cliente():
    if request.method == 'POST':
        numero_documento = request.form.get('numero_documento')
        nombre_cliente = request.form.get('nombre_cliente')
        
        if numero_documento:
            clientes = Cliente.query.filter_by(numero_documento=numero_documento).all()
        elif nombre_cliente:
            # Eliminar espacios adicionales y preparar el patrón de búsqueda
            nombre_cliente = nombre_cliente.strip()
            search_pattern = f"%{nombre_cliente}%"
            # Concatenar nombre y apellido y realizar búsqueda con ilike
            clientes = Cliente.query.filter(
                db.func.lower(Cliente.nombre + ' ' + Cliente.apellido).ilike(search_pattern)
            ).all()
            # Concatenación de nombre y apellido y búsqueda insensible a mayúsculas
            # clientes = Cliente.query.filter(
            # db.func.lower((Cliente.nombre || ' ' || Cliente.apellido)).like(f"%{nombre_cliente}%")
            # ).all()
        else:
            clientes = []
        
        if len(clientes) == 1:
            cliente = clientes[0]
            return redirect(url_for('gestionar_cliente', cliente_id=cliente.id))
        elif len(clientes) > 1:
            return render_template('seleccionar_cliente.html', clientes=clientes)
        else:
            flash('No se encontraron clientes con los criterios proporcionados.')
            return redirect(url_for('crear_cliente'))  # Redirigir a la creación de cliente


        # # Buscar el cliente por número de documento
        # cliente = Cliente.query.filter_by(numero_documento=numero_documento).first()

        # if cliente:
        #     # Si el cliente existe, redirigir a la página de gestión con los datos del cliente
        #     return redirect(url_for('gestionar_cliente', cliente_id=cliente.id))
        # else:
        #     # Si el cliente no existe, preguntar si desea crear un nuevo cliente
        #     flash('Cliente no encontrado. ¿Desea crear un nuevo cliente?', 'warning')

    # Obtener el ID del cliente si se proporcionó como parámetro
    cliente_id = request.args.get('cliente_id')
    cliente = None
    ventas = []
    cobranzas = []
    seguimientos_venta = []
    seguimientos_cobranza = []

    if cliente_id:
        cliente = Cliente.query.get(cliente_id)
        if cliente:
            # Obtener todas las ventas, cobranzas y seguimientos asociados al cliente
            ventas = Venta.query.filter_by(cliente_id=cliente.id).all()
            #cobranzas = PagoCuota.query.filter_by(cliente_id=cliente.id).all()
            seguimientos_venta = SeguimientoVenta.query.filter_by(cliente_id=cliente.id).all()
            seguimientos_cobranza = SeguimientoCobranza.query.filter_by(cliente_id=cliente.id).all()

    return render_template('gestionar_cliente.html', cliente=cliente, ventas=ventas, seguimientos_venta=seguimientos_venta, seguimientos_cobranza=seguimientos_cobranza)
@current_app.route('/registrar_seguimiento_venta/<int:cliente_id>', methods=['GET', 'POST'])
@login_required
def registrar_seguimiento_venta(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)

    if request.method == 'POST':
        fecha_str = request.form['fecha']
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        detalle = request.form['detalle']

        fecha_proximo_contacto_str = request.form.get('fecha_proximo_contacto')
        fecha_proximo_contacto = None
        
        # Maneja la conversión si el campo no está vacío
        if fecha_proximo_contacto_str:
            try:
                fecha_proximo_contacto = datetime.strptime(fecha_proximo_contacto_str, '%Y-%m-%d').date()
            except ValueError as e:
                flash(f'Error en la fecha de próximo contacto: {e}', 'danger')
                print(f'Error en la fecha de próximo contacto: {e}')
                return render_template('registrar_seguimiento_venta.html', cliente=cliente)

        try:
            nuevo_seguimiento_venta = SeguimientoVenta(
                cliente_id=cliente_id,
                fecha=fecha,
                fecha_proximo_contacto=fecha_proximo_contacto,
                detalle=detalle
            )
            db.session.add(nuevo_seguimiento_venta)
            db.session.commit()

            flash('Seguimiento de venta registrado correctamente', 'success')
            print('Seguimiento de venta registrado correctamente')
            return redirect(url_for('gestionar_cliente', cliente_id=cliente_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar seguimiento: {e}', 'danger')
            print(f'Error al registrar seguimiento: {e}')

    return render_template('registrar_seguimiento_venta.html', cliente=cliente)
    cliente = Cliente.query.get_or_404(cliente_id)

    if request.method == 'POST':
        #venta_id = request.form['venta_id']
        fecha_Str = request.form['fecha']
        fecha = datetime.strptime(fecha_Str, '%Y-%m-%d').date()
        print(f'fecha: {fecha}')
        detalle = request.form['detalle']
        print(f'detalle: {detalle}')
        fecha_proximo_contacto_str = request.form.get('fecha_proximo_contacto')
        fecha_proximo_contacto = request.form.get('fecha_proximo_contacto')
        print(f'fecha_proximo_contacto: {fecha_proximo_contacto}')

        nuevo_seguimiento_venta = SeguimientoVenta(
            cliente_id=cliente_id,
            fecha=fecha,
            fecha_proximo_contacto=datetime.strptime(fecha_proximo_contacto, '%Y-%m-%d'),
            detalle=detalle
        )
        db.session.add(nuevo_seguimiento_venta)
        db.session.commit()

        flash('Seguimiento de venta registrado correctamente', 'success')
        return redirect(url_for('gestionar_cliente', cliente_id=cliente_id))

    return render_template('registrar_seguimiento_venta.html', cliente=cliente)
@current_app.route('/seguimiento_cobranza/<int:cliente_id>', methods=['GET', 'POST'])
@login_required
def registrar_seguimiento_cobranza(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    
    if request.method == 'POST':
        detalle = request.form.get('detalle')
        fecha_str = request.form.get('fecha')
        
        # Convertir la cadena de fecha a un objeto datetime.date
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Formato de fecha inválido.', 'danger')
            return redirect(url_for('gestionar_cliente', cliente_id=cliente_id))
        
        if detalle:
            seguimiento = SeguimientoCobranza(cliente_id=cliente_id, detalle=detalle, fecha=fecha)
            try:
                db.session.add(seguimiento)
                db.session.commit()
                flash('Seguimiento de cobranza registrado correctamente.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error al registrar el seguimiento: {e}', 'danger')
        else:
            flash('El detalle del seguimiento no puede estar vacío.', 'danger')
        
        return redirect(url_for('gestionar_cliente', cliente_id=cliente_id))
    
    # Renderizar el formulario con el cliente
    return render_template('registrar_seguimiento_cobranza.html', cliente=cliente)
@current_app.route('/registrar_cobranza/<int:cliente_id>', methods=['GET', 'POST'])
@login_required
def registrar_cobranza(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)

    if request.method == 'POST':
        #venta_id = request.form['venta_id']
        fecha = request.form['fecha']
        detalle = request.form['detalle']

        nuevo_seguimiento_venta = SeguimientoVenta(
            cliente_id=cliente_id,
            fecha=fecha,
            
            detalle=detalle
        )
        db.session.add(nuevo_seguimiento_venta)
        db.session.commit()

        flash('Seguimiento de venta registrado correctamente', 'success')
        return redirect(url_for('gestionar_cliente', cliente_id=cliente_id))

    return render_template('registrar_seguimiento_venta.html', cliente=cliente)
@current_app.route('/gestionar_cuotas/<int:venta_id>', methods=['GET', 'POST'])
@login_required
def gestionar_cuotas(venta_id):
    venta = Venta.query.get_or_404(venta_id)
    cuotas_ordenadas = sorted(venta.cuotas, key=lambda c: c.fecha_vencimiento)
    total_cuotas = len(cuotas_ordenadas)
    for index, cuota in enumerate(cuotas_ordenadas):

        cuota.numero_pagare = f"{index + 1}/{total_cuotas}"
    if not venta.cuotas:
        flash('La venta no tiene cuotas asociadas.', 'info')
        

        return redirect(url_for('gestionar_cliente'))

    if request.method == 'POST':
        try:
            cuotas_actualizadas = False
            for cuota_id in request.form.getlist('cuota_id'):
                fecha_cancelacion_str = request.form.get(f'fecha_cancelacion_{cuota_id}')
                tipo_pago = request.form.get(f'tipo_pago_{cuota_id}')
                print(f'Tipo pago: {tipo_pago}')
                if fecha_cancelacion_str:  # Solo procesar si se ha ingresado una fecha
                    print("hay cuota a cancelar")
                    cuota = Cuota.query.get(cuota_id)
                    if cuota:
                        cuota.fecha_pago = datetime.strptime(fecha_cancelacion_str, '%Y-%m-%d').date()
                        cuota.tipo_pago = tipo_pago
                        print("actualizando cuota")
                        cuota.pagado = True
                        cuotas_actualizadas = True
                        # Buscar el concepto "PAGO DE CUOTA"
                        concepto = Concepto.query.filter_by(nombre='COBRO DE CUOTAS', tipo='ingreso').first()
                        if not concepto:
                            flash('Error: No se encontró un concepto de ingreso llamado "PAGO DE CUOTA".', 'danger')
                            return redirect(url_for('gestionar_cliente', cliente_id=venta.cliente_id))

                        # Obtener el nombre del cliente
                        cliente = Cliente.query.get(venta.cliente_id)
                        cliente_nombre = f"{cliente.nombre} {cliente.apellido}" if cliente else "N/A"

                        # Crear la descripción del ingreso
                        descripcion = f"Pago de cuota - Venta {venta.codigo_interno} - Cliente: {cliente_nombre}"
                        moneda = 'PYG'
                        tasa_cambio = 1
                        # Registrar el ingreso
                        ingreso = Ingreso(
                            concepto_id=concepto.id,
                            moneda = moneda,
                            tasa_cambio = tasa_cambio,
                            importe=cuota.importe,
                            descripcion=descripcion,
                            fecha=cuota.fecha_pago  # Fecha de pago de la cuota
                        )
                        db.session.add(ingreso)
            if cuotas_actualizadas:
                db.session.commit()
                print("cuotas actualizadas correctamente")
                flash('Cuotas actualizadas correctamente.', 'success')
            else:
                flash('No se han actualizado cuotas. Asegúrate de ingresar una fecha de cancelación.', 'info')
            return redirect(url_for('gestionar_cliente', cliente_id=venta.cliente_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar cuotas: {e}', 'danger')
            print(f'Error al actualizar cuotas: {e}')
            return redirect(url_for('gestionar_cliente', cliente_id=venta.cliente_id))

    return render_template('gestionar_cuotas.html', venta=venta)
@current_app.route('/editar_seguimiento_venta/<int:seguimiento_id>', methods=['GET', 'POST'])
@login_required
def editar_seguimiento_venta(seguimiento_id):
    seguimiento = SeguimientoVenta.query.get_or_404(seguimiento_id)
    
    if request.method == 'POST':
        seguimiento.fecha = request.form['fecha']
        seguimiento.detalle = request.form['detalle']
        try:
            db.session.commit()
            flash('Seguimiento de venta actualizado correctamente.', 'success')
            return redirect(url_for('gestionar_cliente', cliente_id=seguimiento.venta.cliente_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar seguimiento de venta: {e}', 'danger')
    
    return render_template('registrar_seguimiento_venta.html', seguimiento=seguimiento)

# Ruta para eliminar un seguimiento de venta
@current_app.route('/eliminar_seguimiento_venta/<int:seguimiento_id>', methods=['POST'])
@login_required
def eliminar_seguimiento_venta(seguimiento_id):
    seguimiento = SeguimientoVenta.query.get_or_404(seguimiento_id)
    cliente_id = seguimiento.cliente_id
    try:
        db.session.delete(seguimiento)
        db.session.commit()
        flash('Seguimiento de venta eliminado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar seguimiento de venta: {e}', 'danger')
    
    return redirect(url_for('gestionar_cliente', cliente_id=cliente_id))

# Ruta para editar un seguimiento de cobranza
@current_app.route('/editar_seguimiento_cobranza/<int:seguimiento_id>', methods=['GET', 'POST'])
@login_required
def editar_seguimiento_cobranza(seguimiento_id):
    seguimiento = SeguimientoCobranza.query.get_or_404(seguimiento_id)
    
    if request.method == 'POST':
        seguimiento.fecha = request.form['fecha']
        seguimiento.detalle = request.form['detalle']
        try:
            db.session.commit()
            flash('Seguimiento de cobranza actualizado correctamente.', 'success')
            return redirect(url_for('gestionar_cliente', cliente_id=seguimiento.cobranza.cliente_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar seguimiento de cobranza: {e}', 'danger')
    
    return render_template('registrar_seguimiento_cobranza.html', seguimiento=seguimiento)

# Ruta para eliminar un seguimiento de cobranza
@current_app.route('/eliminar_seguimiento_cobranza/<int:seguimiento_id>', methods=['POST'])
@login_required
def eliminar_seguimiento_cobranza(seguimiento_id):
    seguimiento = SeguimientoCobranza.query.get_or_404(seguimiento_id)
    cliente_id = seguimiento.cliente_id
    try:
        db.session.delete(seguimiento)
        db.session.commit()
        flash('Seguimiento de cobranza eliminado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar seguimiento de cobranza: {e}', 'danger')
    
    return redirect(url_for('gestionar_cliente', cliente_id=cliente_id))
@current_app.route('/conceptos', methods=['GET', 'POST'])
@login_required
def manage_concepts():
    if request.method == 'POST':
        nombre = request.form['nombre']
        tipo = request.form['tipo']  # 'ingreso' o 'egreso'
        nuevo_concepto = Concepto(nombre=nombre, tipo=tipo)
        db.session.add(nuevo_concepto)
        db.session.commit()
        flash('Concepto creado con éxito.')
        return redirect(url_for('manage_concepts'))

    conceptos = Concepto.query.all()
    return render_template('conceptos.html', conceptos=conceptos)

@current_app.route('/ingreso', methods=['GET', 'POST'])
@login_required
def register_income():
    if request.method == 'POST':
        concepto_id = request.form['concepto']
        fecha = request.form['fecha']
        importe = float(request.form['importe'])
        moneda = request.form['moneda']
        descripcion = request.form['descripcion']
        tasa_cambio = float(request.form.get('tasa_cambio', 1.0))
        nuevo_ingreso = Ingreso(concepto_id=concepto_id, fecha=datetime.strptime(fecha, '%Y-%m-%d'), 
                                importe=importe, moneda=moneda, tasa_cambio=tasa_cambio, descripcion=descripcion)
        db.session.add(nuevo_ingreso)
        db.session.commit()
        flash('Ingreso registrado con éxito.')
        return redirect(url_for('register_income'))

    conceptos = Concepto.query.filter_by(tipo='ingreso').all()
    return render_template('ingreso.html', conceptos=conceptos)

@current_app.route('/egreso', methods=['GET', 'POST'])
@login_required
def register_expense():
    if request.method == 'POST':
        concepto_id = request.form['concepto']
        fecha = request.form['fecha']
        importe = float(request.form['importe'])
        moneda = request.form['moneda']
        descripcion = request.form['descripcion']
        tasa_cambio = float(request.form.get('tasa_cambio', 1.0))
        nuevo_egreso = Egreso(concepto_id=concepto_id, fecha=datetime.strptime(fecha, '%Y-%m-%d'), 
                              importe=importe, moneda=moneda, tasa_cambio=tasa_cambio,descripcion=descripcion)
        db.session.add(nuevo_egreso)
        db.session.commit()
        flash('Egreso registrado con éxito.')
        return redirect(url_for('register_expense'))

    conceptos = Concepto.query.filter_by(tipo='egreso').all()
    return render_template('egreso.html', conceptos=conceptos)

@current_app.route('/flujo_caja', methods=['GET'])
@login_required
def cash_flow():
    # Obtén los parámetros del formulario de filtro
    mes = request.args.get('mes', type=int)
    anio = request.args.get('anio', type=int)

    # Consulta los ingresos y egresos, filtrando si se proporciona mes y año
    ingresos_query = Ingreso.query
    egresos_query = Egreso.query

    if mes and anio:
        fecha_inicio = datetime(anio, mes, 1)
        if mes == 12:
            fecha_fin = datetime(anio + 1, 1, 1)
        else:
            fecha_fin = datetime(anio, mes + 1, 1)
        ingresos_query = ingresos_query.filter(Ingreso.fecha >= fecha_inicio, Ingreso.fecha < fecha_fin)
        egresos_query = egresos_query.filter(Egreso.fecha >= fecha_inicio, Egreso.fecha < fecha_fin)

    ingresos = ingresos_query.all()
    egresos = egresos_query.all()

    # Procesa los datos de ingresos y egresos
    flujo = {}
    totales = {'ingresos': 0, 'egresos': 0}

    for ingreso in ingresos:
        mes = ingreso.fecha.strftime('%Y-%m')
        if mes not in flujo:
            flujo[mes] = {'ingresos': 0, 'egresos': 0, 'detalles': []}
        importe_convertido = ingreso.importe * ingreso.tasa_cambio
        flujo[mes]['ingresos'] += importe_convertido
        flujo[mes]['detalles'].append({
            'descripcion': ingreso.descripcion,
            'importe': importe_convertido,
            'concepto': ingreso.concepto.nombre,
            'tipo': 'Ingreso'
        })
        totales['ingresos'] += importe_convertido

    for egreso in egresos:
        mes = egreso.fecha.strftime('%Y-%m')
        if mes not in flujo:
            flujo[mes] = {'ingresos': 0, 'egresos': 0, 'detalles': []}
        importe_convertido = egreso.importe * egreso.tasa_cambio
        flujo[mes]['egresos'] += importe_convertido
        flujo[mes]['detalles'].append({
            'descripcion': egreso.descripcion,
            'importe': importe_convertido,
            'concepto': egreso.concepto.nombre,
            'tipo': 'Egreso'
        })
        totales['egresos'] += importe_convertido

    # Calcula el saldo mensual
    for valores in flujo.values():
        valores['saldo'] = valores['ingresos'] - valores['egresos']

    # Calcula la diferencia general (saldo total)
    totales['saldo'] = totales['ingresos'] - totales['egresos']

    # Renderiza la plantilla con los datos del flujo y los totales
    return render_template('flujo_caja.html', flujo=flujo, totales=totales, mes_filtro=mes, anio_filtro=anio)
    # Aquí deberías hacer la consulta a la base de datos para obtener los ingresos y egresos por mes
    flujo = {}
    
    ingresos = Ingreso.query.all()  # Obtén todos los ingresos
    egresos = Egreso.query.all()    # Obtén todos los egresos
    
    for ingreso in ingresos:
        mes = ingreso.fecha.strftime('%Y-%m')
        if mes not in flujo:
            flujo[mes] = {'ingresos': 0, 'egresos': 0, 'detalles': []}
        flujo[mes]['ingresos'] += ingreso.importe*ingreso.tasa_cambio
        flujo[mes]['detalles'].append({
            'descripcion': ingreso.descripcion,
            'importe': ingreso.importe*ingreso.tasa_cambio,
            'concepto': ingreso.concepto.nombre,
            'tipo': 'Ingreso'
        })
    
    for egreso in egresos:
        mes = egreso.fecha.strftime('%Y-%m')
        if mes not in flujo:
            flujo[mes] = {'ingresos': 0, 'egresos': 0, 'detalles': []}
        flujo[mes]['egresos'] += egreso.importe*egreso.tasa_cambio
        flujo[mes]['detalles'].append({
            'descripcion': egreso.descripcion,
            'importe': egreso.importe*egreso.tasa_cambio,
            'concepto': egreso.concepto.nombre,
            'tipo': 'Egreso'
        })

    for mes, valores in flujo.items():
        valores['saldo'] = valores['ingresos'] - valores['egresos']

    return render_template('flujo_caja.html', flujo=flujo)
@current_app.route('/consultar_seguimientos_venta')
@login_required
def consultar_seguimientos_venta():
    mes_actual = datetime.now().month
    año_actual = datetime.now().year
    seguimientos = SeguimientoVenta.query.filter(
        extract('month', SeguimientoVenta.fecha_proximo_contacto) == mes_actual,
        extract('year', SeguimientoVenta.fecha_proximo_contacto) == año_actual
    ).all()
    return render_template('consultar_seguimientos_venta.html', seguimientos=seguimientos)
@current_app.route('/eliminar_venta/<int:venta_id>', methods=['GET'])
def eliminar_venta(venta_id):
    try:
        # Primero obtener la venta para asegurar su existencia
        venta = Venta.query.get_or_404(venta_id)

        # Eliminar todas las entidades referenciadas
        db.session.delete(venta)
        db.session.commit()
        
        flash('Venta eliminada correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ocurrió un error al eliminar la venta: {}'.format(str(e)), 'danger')

    return redirect(url_for('consultar_ventas'))
@current_app.route('/exportar_datos', methods=['POST'])
@login_required
def exportar_datos():
    formato = request.form.get('formato', 'xls')

    # Suponiendo que tienes una función para obtener los datos
    productos = Producto.query.all()

    # # Crear el DataFrame de pandas
    # df = pd.DataFrame(productos)

    # output = io.BytesIO()

    # if formato == 'xls':
    #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    #         df.to_excel(writer, sheet_name='Productos', index=False)
    #     output.seek(0)
    #     return send_file(output, as_attachment=True, download_name='productos.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    # elif formato == 'ods':
    #     output.seek(0)
    #     df.to_excel(output, sheet_name='Productos', index=False, engine='odf')
    #     output.seek(0)
    #     return send_file(output, as_attachment=True, download_name='productos.ods', mimetype='application/vnd.oasis.opendocument.spreadsheet')

    # return "Formato no soportado", 400
