
from app import app
from flask import render_template, request, flash, redirect, url_for, session

# Importando mi conexión a BD
from conexion.conexionBD import connectionBD

# Para encriptar contraseña generate_password_hash
from werkzeug.security import check_password_hash

# Importando controllers para el modulo de login
from controllers.funciones_login import *
from controllers.funciones_home import *
PATH_URL_LOGIN = "/public/login"


@app.route('/', methods=['GET'])
def inicio():
    if 'conectado' in session:
        return render_template('public/base_cpanel.html', dataLogin=dataLoginSesion())
    else:
        return render_template(f'{PATH_URL_LOGIN}/base_login.html')


@app.route('/mi-perfil/<string:id>', methods=['GET'])
def perfil(id):
    if 'conectado' in session:
        
        return render_template(f'public/perfil/perfil.html', info_perfil_session=info_perfil_session(id), dataLogin=dataLoginSesion(), areas=lista_areasBD(), roles=lista_rolesBD())
    else:
        return redirect(url_for('inicio'))


# Crear cuenta de usuario
@app.route('/register-user', methods=['GET'])
def cpanelRegisterUser():
        return render_template(f'{PATH_URL_LOGIN}/auth_register.html',dataLogin = dataLoginSesion(),areas=lista_areasBD(), roles=lista_rolesBD())


# Recuperar cuenta de usuario
@app.route('/recovery-password', methods=['GET'])
def cpanelRecoveryPassUser():
    if 'conectado' in session:
        return redirect(url_for('inicio'))
    else:
        return render_template(f'{PATH_URL_LOGIN}/auth_forgot_password.html')


# Crear cuenta de usuario
@app.route('/saved-register', methods=['POST'])
def cpanelRegisterUserBD():
    if request.method == 'POST' and 'cedula' in request.form and 'pass_user' in request.form:
        cedula = request.form['cedula']
        name = request.form['name']
        surname = request.form['surname']
        id_area = request.form['selectArea']
        id_rol = request.form['selectRol']
        fecha_creacion = request.form['fecha_creacion']
        fecha_expiracion = request.form['fecha_expiracion']
        tarjeta_id = request.form['tarjeta_id']
        pass_user = request.form['pass_user']

        resultData = recibeInsertRegisterUser(
            cedula, name, surname, id_area,id_rol,fecha_creacion,fecha_expiracion,tarjeta_id,pass_user)
        if (resultData != 0):
            flash('la cuenta fue creada correctamente.', 'success')
            return redirect(url_for('inicio'))
        else:
            return redirect(url_for('inicio'))
    else:
        flash('el método HTTP es incorrecto', 'error')
        return redirect(url_for('inicio'))


# Actualizar datos de mi perfil
@app.route("/actualizar-datos-perfil/<int:id>", methods=['POST'])
def actualizarPerfil(id):
    if request.method == 'POST':
        if 'conectado' in session:
            respuesta = procesar_update_perfil(request.form,id)
            if respuesta == 1:
                flash('Los datos fuerón actualizados correctamente.', 'success')
                return redirect(url_for('inicio'))
            elif respuesta == 0:
                flash(
                    'La contraseña actual esta incorrecta, por favor verifique.', 'error')
                return redirect(url_for('perfil',id=id))
            elif respuesta == 2:
                flash('Ambas claves deben se igual, por favor verifique.', 'error')
                return redirect(url_for('perfil',id=id))
            elif respuesta == 3:
                flash('La Clave actual es obligatoria.', 'error')
                return redirect(url_for('perfil',id=id))
            else: 
                flash('Clave actual incorrecta', 'error')
                return redirect(url_for('perfil',id=id))
        else:
            flash('primero debes iniciar sesión.', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


from datetime import datetime

@app.route('/login', methods=['GET', 'POST'])
def loginCliente():
    if 'conectado' in session:
        return redirect(url_for('inicio'))
    else:
        if request.method == 'POST' and 'cedula' in request.form and 'pass_user' in request.form:

            cedula = str(request.form['cedula'])
            pass_user = str(request.form['pass_user'])
            conexion_MySQLdb = connectionBD()
            cursor = conexion_MySQLdb.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM usuarios WHERE cedula = %s", [cedula])
            account = cursor.fetchone()

            if account:
                fecha_expiracion = account.get('fecha_expiracion')
                fecha_actual = datetime.today().date()

                if fecha_expiracion and fecha_actual >= fecha_expiracion:
                    flash('Tu cuenta ha expirado, contacta con el administrador.', 'error')
                    return render_template(f'{PATH_URL_LOGIN}/base_login.html')

                if check_password_hash(account['password'], pass_user):
                    session['conectado'] = True
                    session['id'] = account['id_usuario']
                    session['name'] = account['nombre_usuario']
                    session['cedula'] = account['cedula']
                    session['rol'] = account['id_rol']

                    flash('La sesión fue correcta.', 'success')
                    return redirect(url_for('inicio'))
                else:
                    flash('Datos incorrectos, por favor revisa.', 'error')
                    return render_template(f'{PATH_URL_LOGIN}/base_login.html')
            else:
                flash('El usuario no existe, por favor verifica.', 'error')
                return render_template(f'{PATH_URL_LOGIN}/base_login.html')
        else:
            flash('Primero debes iniciar sesión.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/base_login.html')


@app.route('/closed-session',  methods=['GET'])
def cerraSesion():
    if request.method == 'GET':
        if 'conectado' in session:
            # Eliminar datos de sesión, esto cerrará la sesión del usuario
            session.pop('conectado', None)
            session.pop('id', None)
            session.pop('name_surname', None)
            session.pop('email', None)
            flash('tu sesión fue cerrada correctamente.', 'success')
            return redirect(url_for('inicio'))
        else:
            flash('recuerde debe iniciar sesión.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/base_login.html')
    
