from controllers.funciones_login import *
from app import app
from flask import render_template, request, flash, redirect, url_for, session,  jsonify
from mysql.connector.errors import Error
import mysql.connector


# Importando cenexión a BD
from controllers.funciones_home import *
@app.route('/empresa', methods=['GET'])
def empresa():
    if 'conectado' in session:
        return render_template('public/usuarios/empresa.html', empresa=lista_empresasBD(), dataLogin=dataLoginSesion())
    else:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('inicio'))


@app.route('/lista-de-areas', methods=['GET'])
def lista_areas():
    if 'conectado' in session:
        return render_template('public/usuarios/lista_areas.html',  areas=lista_areasBD(), dataLogin=dataLoginSesion())
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route("/lista-de-usuarios", methods=['GET'])
def usuarios():
    if 'conectado' in session:
        return render_template('public/usuarios/lista_usuarios.html',  resp_usuariosBD=lista_usuariosBD(), dataLogin=dataLoginSesion(), areas=lista_areasBD(), roles = lista_rolesBD())
    else:
        return redirect(url_for('inicioCpanel'))

#Ruta especificada para eliminar un usuario
@app.route('/borrar-usuario/<string:id>', methods=['GET'])
def borrarUsuario(id):
    resp = eliminarUsuario(id)
    if resp:
        flash('El Usuario fue eliminado correctamente', 'success')
        return redirect(url_for('usuarios'))
    
    
@app.route('/borrar-area/<string:id_area>/', methods=['GET'])
def borrarArea(id_area):
    resp = eliminarArea(id_area)
    if resp:
        flash('El Empleado fue eliminado correctamente', 'success')
        return redirect(url_for('lista_areas'))
    else:
        flash('Hay usuarios que pertenecen a esta área', 'error')
        return redirect(url_for('lista_areas'))


@app.route("/descargar-informe-accesos/", methods=['GET'])
def reporteBD():
    if 'conectado' in session:
        return generarReporteExcel()
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
@app.route("/reporte-accesos", methods=['GET'])
def reporteAccesos():
    if 'conectado' in session:
        userData = dataLoginSesion()
        return render_template('public/perfil/reportes.html',  reportes=dataReportes(),lastAccess=lastAccessBD(userData.get('cedula')), dataLogin=dataLoginSesion())

@app.route("/interfaz-clave", methods=['GET','POST'])
def claves():
    return render_template('public/usuarios/generar_clave.html', dataLogin=dataLoginSesion())
    
@app.route('/generar-y-guardar-clave/<string:id>', methods=['GET','POST'])
def generar_clave(id):
    print(id)
    clave_generada = crearClave()  # Llama a la función para generar la clave
    guardarClaveAuditoria(clave_generada,id)
    return clave_generada
#CREAR AREA
@app.route('/crear-area', methods=['GET','POST'])
def crearArea():
    if request.method == 'POST':
        area_name = request.form['nombre_area']  # Asumiendo que 'nombre_area' es el nombre del campo en el formulario
        resultado_insert = guardarArea(area_name)
        if resultado_insert:
            # Éxito al guardar el área
            flash('El Area fue creada correctamente', 'success')
            return redirect(url_for('lista_areas'))
            
        else:
            # Manejar error al guardar el área
            return "Hubo un error al guardar el área."
    return render_template('public/usuarios/lista_areas')

##ACTUALIZAR AREA
@app.route('/actualizar-area', methods=['POST'])
def updateArea():
    if request.method == 'POST':
        nombre_area = request.form['nombre_area']  # Asumiendo que 'nuevo_nombre' es el nombre del campo en el formulario
        id_area = request.form['id_area']
        resultado_update = actualizarArea(id_area, nombre_area)
        if resultado_update:
           # Éxito al actualizar el área
            flash('El actualizar fue creada correctamente', 'success')
            return redirect(url_for('lista_areas'))
        else:
            # Manejar error al actualizar el área
            return "Hubo un error al actualizar el área."

    return redirect(url_for('lista_areas'))

#Datos sensor tempertura
@app.route('/sensor-temperatura', methods=['GET'])
def sensor_temp():
    if 'conectado' in session:
        try:
            # Obtiene los datos de los sensores de temperatura desde la base de datos
            datos_sensor_temperatura = sensor_temperatura()

            # Renderiza la plantilla con los datos
            return render_template('public/usuarios/sensortemperatura.html', datos_sensor_temperatura = sensor_temperatura(), dataLogin=dataLoginSesion())
        except Exception as e:
            flash(f"Error al obtener datos de sensor de temperatura: {e}", 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

# Eliminar registro sensor temperatura
@app.route('/eliminar-sensor-temperatura/<int:id_sensor>', methods=['GET', 'POST'])
def eliminar_sensor_temperatura_route(id_sensor):
    if 'conectado' in session:
        try:
            # Llama a la función para eliminar el registro del sensor de temperatura
            eliminarSensorTemperatura(id_sensor)  # Asegúrate de definir esta función

            flash('Registro del sensor de temperatura eliminado con éxito.', 'success')
        except Exception as e:
            flash(f"Error al eliminar el registro del sensor de temperatura: {e}", 'error')

        # Redirige a la página de los datos del sensor de temperatura después de la eliminación
        return redirect(url_for('sensor_temp'))  # O a donde desees redirigir
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route('/sensor-humo', methods=['GET'])
def sensor_humo():
    if 'conectado' in session:
        try:
            # Obtiene los datos de los sensores de humo desde la base de datos
            datos_sensor_humo = obtener_datos_sensor_humo()  # Solo una llamada aquí

            # Renderiza la plantilla con los datos obtenidos
            return render_template('public/usuarios/sensorhumo.html', 
                                   datos_sensor_humo=datos_sensor_humo,  # Se pasan los datos correctos
                                   dataLogin=dataLoginSesion())  # Asegúrate de que esta función esté definida correctamente
        except Exception as e:
            flash(f"Error al obtener datos de sensor de humo: {e}", 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

    
# Eliminar registro sensor de humo
@app.route('/eliminar-sensor-humo/<int:id_sensor>', methods=['GET', 'POST'])
def eliminar_sensor_humo_route(id_sensor):
    if 'conectado' in session:
        try:
            # Llama a la función para eliminar el registro del sensor de humo
            eliminarSensorHumo(id_sensor)

            flash('Registro del sensor de humo eliminado con éxito.', 'success')
        except Exception as e:
            flash(f"Error al eliminar el registro del sensor de humo: {e}", 'error')

        # Redirige a la página de los datos del sensor de humo después de la eliminación
        return redirect(url_for('sensor_humo'))  # O a donde desees redirigir
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/tarjeta-rfid', methods=['GET'])
def tarjeta_rfid():
    # Verificamos si el usuario está conectado en la sesión
    if 'conectado' in session:
        try:
            # Llamamos a la función que obtiene los datos de la base de datos
            datos_tarjeta = tarjeta_bd_frid()

            # Renderiza la plantilla y pasa los datos necesarios
            return render_template('public/usuarios/tarjeta.html', datos_tarjeta=datos_tarjeta, dataLogin=dataLoginSesion())
        except Exception as e:
            # Si ocurre un error, mostramos un mensaje y redirigimos
            flash(f"Error al obtener datos de tarjeta RFID: {e}", 'error')
            return redirect(url_for('inicio'))  # Redirige al inicio si hay error
    else:
        # Si no está conectado, mostramos un mensaje de error y redirigimos
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))  # Redirige al inicio si no está conectado
    
#Intento de funcionabilidad de scanerar
@app.route('/tarjeta-rfid/ultimo', methods=['GET'])
def obtener_ultimo_rfid():
    try:
        # Establecemos la conexión a la base de datos
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                # Consulta para obtener el último registro de la tarjeta RFID
                querySQL = "SELECT tarjeta FROM tarjeta_rfid ORDER BY fecha_hora DESC LIMIT 1"
                cursor.execute(querySQL)
                ultimo_registro = cursor.fetchone()  # Obtiene el último registro

        # Devuelve el registro en formato JSON
        return jsonify(ultimo_registro if ultimo_registro else {'tarjeta': None})
    except Exception as e:
        print(f"Error al obtener el último registro de tarjeta RFID: {e}")
        return jsonify({'error': 'Error al obtener el registro de la tarjeta RFID'}), 500


## intento sensor de movimiento
@app.route('/sensor-movimiento', methods=['GET'])
def sensor_movimiento():
    if 'conectado' in session:
        try:
            # Obtiene los datos de la tabla sensor_movimiento
            datos_movimiento = obtener_datos_sensor_movimiento()

            # Renderiza la plantilla y pasa los datos correctamente
            return render_template(
                'public/usuarios/sensormovimiento.html',
                datos_movimiento=datos_movimiento,
                dataLogin=dataLoginSesion()
            )
        except Exception as e:
            flash(f"Error al obtener datos de sensores de movimiento: {e}", 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

# Ruta para borrar empresa
@app.route('/borrar-empresa/<string:id_empresa>', methods=['GET'])
def borrarEmpresa(id_empresa):
    if 'conectado' in session:
        try:
            resp = eliminarEmpresa(id_empresa)
            if resp:
                flash('Empresa eliminada correctamente', 'success')
            else:
                flash('Error al eliminar la empresa', 'error')
        except Exception as e:
            flash(f'Error en base de datos: {str(e)}', 'error')
        return redirect(url_for('empresa'))
    else:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('inicio'))

# Ruta para crear empresa
@app.route('/crear-empresa', methods=['POST'])
def crear_empresa():
    if 'conectado' in session:
        if request.method == 'POST':
            # Imprime los datos recibidos
            print(request.form)
            nombre_empresa = request.form.get('nombre_empresa', '').strip()
            direccion_empresa = request.form.get('direccion_empresa', '').strip()
            telefono_empresa = request.form.get('telefono_empresa', '').strip()
            email_empresa = request.form.get('email_empresa', '').strip() or None

            # Validar campos obligatorios
            if not all([nombre_empresa, direccion_empresa, telefono_empresa]):
                flash('Nombre, dirección y teléfono son campos obligatorios', 'error')
                return redirect(url_for('empresa'))

            # Validar formato del teléfono (solo números)
            if not telefono_empresa.isdigit():
                flash('El teléfono debe contener solo números', 'error')
                return redirect(url_for('empresa'))

            try:
                resultado = guardarEmpresa(nombre_empresa, direccion_empresa, telefono_empresa, email_empresa)
                if resultado:
                    flash('Empresa creada exitosamente', 'success')
                else:
                    flash('Error al crear la empresa', 'error')
            except Exception as e:
                flash(f'Error en base de datos: {str(e)}', 'error')

            return redirect(url_for('empresa'))
    else:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('inicio'))
