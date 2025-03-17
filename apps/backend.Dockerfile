FROM mariadb:latest
LABEL authors="Gukhwan Hyun"
LABEL build_date="2025-03"

# Expose the default MariaDB port
EXPOSE 3306


# If you're using MariaDB or PostgreSQL official Docker images,
# any .sql file inside /docker-entrypoint-initdb.d/ is automatically executed
# when the container starts for the first time
COPY /database/celery_backend/init.sql /docker-entrypoint-initdb.d/

# Set root password for MariaDB (ensure this is set via Kubernetes Secrets later)
ENV MARIADB_ROOT_PASSWORD=raven
ENV MARIADB_DATABASE=celerybackend
ENV MARIADB_USER=celeryuser
ENV MARIADB_PASSWORD=celerypassword
