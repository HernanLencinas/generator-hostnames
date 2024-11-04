FROM python:3
WORKDIR /generador
COPY src/ /generador/
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
RUN pip install mysqlclient
EXPOSE 8080
CMD [ "python", "/generador/generador.py" ]