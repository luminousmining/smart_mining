FROM postgres:latest

COPY db.sql .
COPY install_db.sh /docker-entrypoint-initdb.d/

ENV POSTGRES_USER=luminousminer
ENV POSTGRES_PASSWORD=password

