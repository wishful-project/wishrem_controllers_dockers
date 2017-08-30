FROM mysql

RUN apt-get update

RUN apt-get install -y python3

RUN apt-get install -y python3-mysql.connector

COPY MySQLtables.py /app/

COPY start.sh /docker-entrypoint-initdb.d/
