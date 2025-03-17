FROM mariadb:latest
LABEL authors="Gukhwan Hyun"
LABEL build_date="2025-03"

EXPOSE 3306

# Set environment variables for MariaDB
ENV MARIADB_ROOT_PASSWORD=raven
ENV MARIADB_DATABASE=chat_history
ENV MARIADB_USER=admin
ENV MARIADB_PASSWORD=raven

# Copy the schema setup file into the container
COPY /database/storage/init.sql /docker-entrypoint-initdb.d/