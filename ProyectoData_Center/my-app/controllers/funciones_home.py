
# Para subir archivo tipo foto al servidor
from werkzeug.utils import secure_filename
import mysql.connector
import uuid  # Modulo de python para crear un string

from conexion.conexionBD import connectionBD  # Conexión a BD

import datetime
import re
import os

from os import remove  # Modulo  para remover archivo
from os import path  # Modulo para obtener la ruta o directorio


import openpyxl  # Para generar el excel
# biblioteca o modulo send_file para forzar la descarga
from flask import send_file, session

def accesosReporte():
    if session['rol'] == 1 :
        try:
            with connectionBD() as conexion_MYSQLdb:
                with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                    querySQL = ("""
                        SELECT a.id_acceso, u.cedula, a.fecha, r.nombre_area, a.clave 
                        FROM accesos a 
                        JOIN usuarios u 
                        JOIN area r
                        WHERE u.id_area = r.id_area AND u.id_usuario = a.id_usuario
                        ORDER BY u.cedula, a.fecha DESC
                                """) 
                    cursor.execute(querySQL)
                    accesosBD=cursor.fetchall()
                return accesosBD
        except Exception as e:
            print(
                f"Errro en la función accesosReporte: {e}")
            return None
    else:
        cedula = session['cedula']
        try:
            with connectionBD() as conexion_MYSQLdb:
                with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                    querySQL = ("""
                        SELECT 
                            a.id_acceso, 
                            u.cedula, 
                            a.fecha,
                            r.nombre_area, 
                            a.clave 
                            FROM accesos a 
                            JOIN usuarios u JOIN area r 
                            WHERE u.id_usuario = a.id_usuario AND u.id_area = r.id_area AND u.cedula = %s
                            ORDER BY u.cedula, a.fecha DESC
                                """) 
                    cursor.execute(querySQL,(cedula,))
                    accesosBD=cursor.fetchall()
                return accesosBD
        except Exception as e:
            print(
                f"Errro en la función accesosReporte: {e}")
            return None


def generarReporteExcel():
    dataAccesos = accesosReporte()
    wb = openpyxl.Workbook()
    hoja = wb.active

    # Agregar la fila de encabezado con los títulos
    cabeceraExcel = ("ID", "CEDULA", "FECHA", "ÁREA", "CLAVE GENERADA")

    hoja.append(cabeceraExcel)

    # Agregar los registros a la hoja
    for registro in dataAccesos:
        id_acceso = registro['id_acceso']
        cedula = registro['cedula']
        fecha = registro['fecha']
        area = registro['nombre_area']
        clave = registro['clave']

        # Agregar los valores a la hoja
        hoja.append((id_acceso, cedula, fecha,area, clave))

    fecha_actual = datetime.datetime.now()
    archivoExcel = f"Reporte_accesos_{session['cedula']}_{fecha_actual.strftime('%Y_%m_%d')}.xlsx"
    carpeta_descarga = "../static/downloads-excel"
    ruta_descarga = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), carpeta_descarga)

    if not os.path.exists(ruta_descarga):
        os.makedirs(ruta_descarga)
        # Dando permisos a la carpeta
        os.chmod(ruta_descarga, 0o755)

    ruta_archivo = os.path.join(ruta_descarga, archivoExcel)
    wb.save(ruta_archivo)

    # Enviar el archivo como respuesta HTTP
    return send_file(ruta_archivo, as_attachment=True)

def buscarAreaBD(search):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                querySQL = ("""
                        SELECT 
                            a.id_area,
                            a.nombre_area
                        FROM area AS a
                        WHERE a.nombre_area LIKE %s 
                        ORDER BY a.id_area DESC
                    """)
                search_pattern = f"%{search}%"  # Agregar "%" alrededor del término de búsqueda
                mycursor.execute(querySQL, (search_pattern,))
                resultado_busqueda = mycursor.fetchall()
                return resultado_busqueda

    except Exception as e:
        print(f"Ocurrió un error en def buscarEmpleadoBD: {e}")
        return []


# Lista de Usuarios creados
def lista_usuariosBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT id_usuario, cedula, nombre_usuario, apellido_usuario, id_area, id_rol, fecha_creacion, fecha_expiracion, id_empresa FROM usuarios"
                cursor.execute(querySQL,)
                usuariosBD = cursor.fetchall()
        return usuariosBD
    except Exception as e:
        print(f"Error en lista_usuariosBD : {e}")
        return []

def lista_areasBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT id_area, nombre_area FROM area"
                cursor.execute(querySQL,)
                areasBD = cursor.fetchall()
        return areasBD
    except Exception as e:
        print(f"Error en lista_areas : {e}")
        return []


def lista_empresasBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                    SELECT 
                        id_empresa,
                        nombre_empresa,
                        direccion_empresa,
                        telefono_empresa,
                        email_empresa 
                    FROM empresa
                """
                cursor.execute(querySQL)
                empresasBD = cursor.fetchall()
                print(f"Empresas encontradas: {empresasBD}")  # Imprimir las empresas
                if not empresasBD:
                    print("No se encontraron empresas")
        return empresasBD
    except Exception as e:
        print(f"Error en lista_empresasBD: {e}")
        return []


# Eliminar usuario
def eliminarUsuario(id):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM usuarios WHERE id_usuario=%s"
                cursor.execute(querySQL, (id,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminarUsuario : {e}")
        return []    

def eliminarArea(id):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM area WHERE id_area=%s"
                cursor.execute(querySQL, (id,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminarArea : {e}")
        return []
    
def dataReportes():
    try:
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                SELECT a.id_acceso, u.cedula, a.fecha, r.nombre_area, a.clave 
                FROM accesos a 
                JOIN usuarios u 
                JOIN area r
                WHERE u.id_area = r.id_area AND u.id_usuario = a.id_usuario
                ORDER BY u.cedula, a.fecha DESC
                """
                cursor.execute(querySQL)
                reportes = cursor.fetchall()
        return reportes
    except Exception as e:
        print(f"Error en listaAccesos : {e}")
        return []

def lastAccessBD(id):
    try:
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT a.id_acceso, u.cedula, a.fecha, a.clave FROM accesos a JOIN usuarios u WHERE u.id_usuario = a.id_usuario AND u.cedula=%s ORDER BY a.fecha DESC LIMIT 1"
                cursor.execute(querySQL,(id,))
                reportes = cursor.fetchone()
                print(reportes)
        return reportes
    except Exception as e:
        print(f"Error en lastAcceso : {e}")
        return []
import random
import string
def crearClave():
    caracteres = string.ascii_letters + string.digits  # Letras mayúsculas, minúsculas y dígitos
    longitud = 6  # Longitud de la clave

    clave = ''.join(random.choice(caracteres) for _ in range(longitud))
    print("La clave generada es:", clave)
    return clave
##GUARDAR CLAVES GENERADAS EN AUDITORIA
def guardarClaveAuditoria(clave_audi,id):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                    sql = "INSERT INTO accesos (fecha, clave, id_usuario) VALUES (NOW(),%s,%s)"
                    valores = (clave_audi,id)
                    mycursor.execute(sql, valores)
                    conexion_MySQLdb.commit()
                    resultado_insert = mycursor.rowcount
                    return resultado_insert 
        
    except Exception as e:
        return f'Se produjo un error en crear Clave: {str(e)}'
    
def lista_rolesBD():
    try:
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT * FROM rol"
                cursor.execute(querySQL)
                roles = cursor.fetchall()
                return roles
    except Exception as e:
        print(f"Error en select roles : {e}")
        return []
##CREAR AREA
def guardarArea(area_name):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                    sql = "INSERT INTO area (nombre_area) VALUES (%s)"
                    valores = (area_name,)
                    mycursor.execute(sql, valores)
                    conexion_MySQLdb.commit()
                    resultado_insert = mycursor.rowcount
                    return resultado_insert 
        
    except Exception as e:
        return f'Se produjo un error en crear Area: {str(e)}' 
    
##ACTUALIZAR AREA
def actualizarArea(area_id, area_name):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                sql = """UPDATE area SET nombre_area = %s WHERE id_area = %s"""
                valores = (area_name, area_id)
                mycursor.execute(sql, valores)
                conexion_MySQLdb.commit()
                resultado_update = mycursor.rowcount
                return resultado_update 
        
    except Exception as e:
        return f'Se produjo un error al actualizar el área: {str(e)}'

def sensor_temperatura():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                # Modifica la consulta según la estructura de tu base de datos
                querySQL = "SELECT id, fecha, valor , nivel_temperatura FROM sensor_temperatura order by fecha desc"
                cursor.execute(querySQL)
                datos_sensor_temperatura = cursor.fetchall()
        return datos_sensor_temperatura
    except Exception as e:
        print(f"Error al obtener datos de sensores de temperatura: {e}")
        return []
    
def eliminarSensorTemperatura(id_sensor):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor() as cursor:
                querySQL = "DELETE FROM sensor_temperatura WHERE id = %s"
                cursor.execute(querySQL, (id_sensor,))
                conexion_MySQLdb.commit()  # Asegúrate de hacer commit para guardar cambios
    except Exception as e:
        print(f"Error al eliminar el sensor de temperatura: {e}")
        raise  # Vuelve a lanzar la excepción para ser capturada en la vista

def tarjeta_bd_frid():
    try:
        # Establecemos la conexión a la base de datos
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                # Consulta SQL para obtener los datos de la tarjeta RFID
                querySQL = "SELECT id_usuario, fecha_hora, tarjeta, autorizada FROM tarjeta_rfid ORDER BY fecha_hora DESC"
                cursor.execute(querySQL)
                # Obtiene los resultados de la consulta
                datos_tarjeta = cursor.fetchall()
        return datos_tarjeta  # Retorna los datos obtenidos
    except Exception as e:
        # En caso de error, lo imprime en el log y retorna una lista vacía
        print(f"Error al obtener registros de la tarjeta RFID: {e}")
        return []  # Retorna una lista vacía en caso de error

    
def obtener_datos_sensor_humo():
    try:
        # Establece la conexión con la base de datos
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                # Consulta para obtener los datos del sensor de humo
                querySQL = "SELECT id, fecha, valor, nivel_humo FROM sensor_humo ORDER BY fecha DESC"
                cursor.execute(querySQL)
                # Obtiene todos los resultados de la consulta
                datos_sensor_humo = cursor.fetchall()
        
        # Si no se obtiene ningún dato, se podría devolver una lista vacía (por seguridad)
        if not datos_sensor_humo:
            print("No se encontraron registros para el sensor de humo.")
        
        # Retorna los datos obtenidos
        return datos_sensor_humo
    except Exception as e:
        # Maneja cualquier excepción que ocurra y muestra un mensaje de error
        print(f"Error al obtener registros de los sensores de humo: {e}")
        # Devuelve una lista vacía en caso de error
        return []




def obtener_datos_sensor_movimiento():
    try:
        # Conexión a la base de datos
        conexion_MySQLdb = mysql.connection  
        with conexion_MySQLdb.cursor(dictionary=True) as cursor:
            # Consulta SQL para obtener los datos de la tabla sensor_movimiento
            querySQL = """
            SELECT id, fecha, estado, sensor
            FROM sensor_movimiento ORDER BY fecha DESC
            """
            cursor.execute(querySQL)
            datos_sensor_movimiento = cursor.fetchall()  # Obtiene todos los registros
        return datos_sensor_movimiento  # Retorna los datos obtenidos
    except Exception as e:
        print(f"Error al obtener datos de sensores de movimiento: {e}")
        return []  # Retorna una lista vacía en caso de error
def guardarEmpresa(nombre, direccion, telefono, email=None):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = """INSERT INTO empresa 
                            (nombre_empresa, direccion_empresa, telefono_empresa, email_empresa)
                            VALUES (%s, %s, %s, %s)"""
                cursor.execute(querySQL, (nombre, direccion, telefono, email))
                conexion_MySQLdb.commit()
                return cursor.lastrowid  # Retorna el ID de la nueva empresa insertada
    except Exception as e:
        print(f"Error en guardarEmpresa: {e}")
        return False

def eliminarEmpresa(id_empresa):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                sql = "DELETE FROM empresa WHERE id_empresa = %s"
                cursor.execute(sql, (id_empresa,))
                conexion_MySQLdb.commit()
                return cursor.rowcount > 0  # Retorna True si se eliminó algún registro
    except Exception as e:
        print(f"Error en eliminarEmpresa: {e}")
        return False
