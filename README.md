# Generador de Hostnames

Este proyecto permite realizar consultas, altas y bajas de hostnames mediante una API expuesta a través de un contenedor Docker. La CLI incluida permite interactuar con la API para gestionar los registros de hostname.

## Configuración

### Archivo `config.py`

Antes de ejecutar el proyecto, debes configurar el archivo `config.py` con los detalles de tu base de datos MySQL y los parámetros de la API. Asegúrate de tener este archivo en la ruta adecuada o crea un archivo `config.py` con el siguiente contenido:

```python
# Configuración del servidor web
WS_HOST = '0.0.0.0'        # Dirección de escucha del servidor
WS_PORT = 8080              # Puerto de escucha del servidor

# Configuración de la base de datos MySQL
MYSQL_HOST = "mysql"        # Host de la base de datos MySQL
MYSQL_USER = "generador"    # Usuario de la base de datos
MYSQL_PASSWORD = ""         # Contraseña del usuario MySQL
MYSQL_DB = 'generador'      # Nombre de la base de datos
```

### Crear el archivo `config.py`

Guarda el archivo `config.py` en una carpeta accesible en el host, como `/generador_hostnames/config.py`. Este archivo será montado en el contenedor durante la ejecución.

## Construcción del Proyecto

Para construir el proyecto, puedes utilizar el siguiente Dockerfile, ubicado en la carpeta `src` del proyecto:

### Dockerfile

```Dockerfile
FROM python:3
WORKDIR /generador
COPY src/ /generador/
RUN pip3 install mysqlclient
EXPOSE 8080
CMD ["python", "/generador/generador_hostname.py"]
```

### Construcción del Contenedor

Ejecuta el siguiente comando para construir el contenedor Docker desde el Dockerfile:

```bash
docker build -t telecomcloudvalley/generador_hostname:latest .
```

Este comando creará una imagen con el nombre `telecomcloudvalley/generador_hostname` y la etiqueta `latest`.

## Ejecución del Contenedor

Una vez que hayas creado la imagen y configurado `config.py`, ejecuta el contenedor con el siguiente comando:

```bash
docker run -d -it \
  --name generador_hostnames \
  -p 8080:8080 \
  -v /generador_hostnames/config.py:/generador/config.py \
  --network apptomation_app-network \
  --restart always \
  telecomcloudvalley/generador_hostname:latest
```

**Parámetros del comando:**

- `--name generador_hostnames`: Asigna un nombre al contenedor para facilitar su identificación.
- `-p 8080:8080`: Publica el puerto `8080` del contenedor para el acceso a la API.
- `-v /generador_hostnames/config.py:/generador/config.py`: Monta el archivo `config.py` en el contenedor.
- `--network apptomation_app-network`: Conecta el contenedor a la red Docker especificada.
- `--restart always`: Configura el contenedor para reiniciarse automáticamente en caso de fallo.
- `telecomcloudvalley/generador_hostname:latest`: Especifica la imagen de Docker y la etiqueta para ejecutar.

## Uso de la CLI

La CLI interactúa con el servicio y permite realizar consultas, altas y bajas de hostnames. Asegúrate de que el servicio esté en ejecución y escucha en `http://localhost:8080`.

### Ejecutar la CLI

Para ejecutar la CLI, utiliza el siguiente comando:

```bash
bash cli.sh
```

