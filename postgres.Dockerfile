FROM postgres:latest
RUN apt-get update && apt-get install -y postgresql-16-pgvector
COPY init.sql /docker-entrypoint-initdb.d
RUN chmod +x /docker-entrypoint-initdb.d/init.sql