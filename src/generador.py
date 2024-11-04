#!/usr/bin/python3

import sys
import http.server
import socketserver
import json
import threading
import config as cfg
import MySQLdb

def api_query(m_method, m_hostname="", m_ip="", m_user="", m_comment=""):
    """Realiza operaciones de consulta, inserción o eliminación en la base de datos según el método proporcionado."""

    # Conexión a la base de datos
    try:
        db_connection = MySQLdb.connect(
            host=cfg.MYSQL_HOST,
            user=cfg.MYSQL_USER,
            passwd=cfg.MYSQL_PASSWORD,
            db=cfg.MYSQL_DB
        )
    except MySQLdb.Error as e:
        print(f"Error de conexion a la base de datos: {e}")
        return "Error: No se pudo conectar a la base de datos."

    cursor = db_connection.cursor()

    # Método GET: Consulta posiciones libres y ocupadas
    if m_method.upper() == "GET":
        try:
            cursor.execute(
                "SELECT position, hostname FROM {}.hosts WHERE hostname LIKE %s ORDER BY position ASC".format(cfg.MYSQL_DB),
                (m_hostname + "%",)
            )
            registros = cursor.fetchall()
            posiciones = [item[0] for item in registros]
            respuesta = []

            for i in range(1, 1000):
                if i in posiciones:
                    respuesta.append(f"[{i}] {m_hostname}{i:03d}")
                else:
                    respuesta.append(f"[{i}] Libre")

            return "\n".join(respuesta).rstrip() + "\n"

        except MySQLdb.Error as e:
            return f"Error al consultar el prefijo [{m_hostname.lower()}]: {e}"
            
                # Método POST: Inserta un nuevo registro si hay una posición disponible
    elif m_method.upper() == "POST":
        try:
            cursor.execute(
                "SELECT position FROM {}.hosts WHERE prefix = %s ORDER BY position ASC".format(cfg.MYSQL_DB),
                (m_hostname,)
            )
            posiciones_ocupadas = {item[0] for item in cursor.fetchall()}

            for i in range(1, 1000):
                if i not in posiciones_ocupadas:
                    nuevo_hostname = f"{m_hostname.lower()}{i:03d}"
                    cursor.execute(
                        "INSERT INTO {}.hosts (`position`, `prefix`, `hostname`, `ip`, `user`, `comment`) VALUES (%s, %s, %s, %s, %s, %s)".format(cfg.MYSQL_DB),
                        (i, m_hostname.lower(), nuevo_hostname, m_ip, m_user, m_comment)
                    )
                    db_connection.commit()
                    print(f"Reservando el hostname: {nuevo_hostname}")
                    return nuevo_hostname

            return "No hay posiciones disponibles para reservar un hostname."

        except MySQLdb.Error as e:
            print(f"No se pudo reservar el hostname: {e}")
            return None

    # Método DELETE: Elimina un registro por hostname
    elif m_method.upper() == "DELETE":
        try:
            cursor.execute(
                "DELETE FROM {}.hosts WHERE hostname = %s".format(cfg.MYSQL_DB),
                (m_hostname.lower(),)
            )
            db_connection.commit()
            return f"Se elimino el hostname [{m_hostname.lower()}]"

        except MySQLdb.Error as e:
            return f"Error al eliminar el hostname [{m_hostname.lower()}]: {e}"

    return "Metodo no soportado"

class WebHandler(http.server.BaseHTTPRequestHandler):
    """Clase que maneja las solicitudes HTTP y responde con el resultado de las consultas a la base de datos."""

    def do_GET(self):
        print(f"Solicitud GET recibida en la ruta: {self.path}")
        if self.path == "/hostname":
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-type", "application/json")
            self.end_headers()

            try:
                longitud_contenido = int(self.headers.get('Content-Length'))
                cuerpo = self.rfile.read(longitud_contenido)
                datos = json.loads(cuerpo)

                if 'prefix' in datos:
                    respuesta = api_query("GET", datos['prefix'])
                    self.wfile.write(respuesta.encode('utf-8'))
                else:
                    self.wfile.write(b"Faltan parametros en la solicitud.")
                    print("Faltan parametros en la solicitud GET.")
            except Exception as e:
                print(f"Error en la solicitud GET: {e}")

        else:
            self.send_error(404, "Recurso no encontrado")

    def do_POST(self):
        print(f"Solicitud POST recibida en la ruta: {self.path}")
        if self.path == "/hostname":
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-type", "application/json")
            self.end_headers()

            try:
                longitud_contenido = int(self.headers.get('Content-Length'))
                cuerpo = self.rfile.read(longitud_contenido)
                datos = json.loads(cuerpo)

                if all(k in datos for k in ('prefix', 'ip', 'user', 'comment')):
                    respuesta = api_query("POST", datos['prefix'], datos['ip'], datos['user'], datos['comment'])
                    self.wfile.write(respuesta.encode('utf-8'))
                else:
                    self.wfile.write(b"Faltan parametros en la solicitud.")
                    print("Faltan parametros en la solicitud POST.")
            except Exception as e:
                print(f"Error en la solicitud POST: {e}")

        else:
            self.send_error(404, "Recurso no encontrado")
            
def do_DELETE(self):
        print(f"Solicitud DELETE recibida en la ruta: {self.path}")
        if self.path == "/hostname":
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-type", "application/json")
            self.end_headers()

            try:
                longitud_contenido = int(self.headers.get('Content-Length'))
                cuerpo = self.rfile.read(longitud_contenido)
                datos = json.loads(cuerpo)

                if 'hostname' in datos:
                    respuesta = api_query("DELETE", datos['hostname'])
                    self.wfile.write(respuesta.encode('utf-8'))
                else:
                    self.wfile.write(b"Faltan parametros en la solicitud.")
                    print("Faltan parametros en la solicitud DELETE.")
            except Exception as e:
                print(f"Error en la solicitud DELETE: {e}")

        else:
            self.send_error(404, "Recurso no encontrado")

def main():
    """Función principal para iniciar el servidor web."""
    print("Iniciando el generador...")

    with socketserver.TCPServer((cfg.WS_HOST, cfg.WS_PORT), WebHandler) as httpd:
        print(f"Servidor escuchando en TCP {cfg.WS_PORT}")
        try:
            print("Presiona Ctrl+C para finalizar el servidor.")
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor finalizado.")
            httpd.shutdown()
            sys.exit()


if __name__ == "__main__":
    main()
