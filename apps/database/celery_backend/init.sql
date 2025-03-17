CREATE DATABASE IF NOT EXISTS celerybackend;
CREATE USER IF NOT EXISTS 'celeryuser'@'%' IDENTIFIED BY 'celerypassword';
GRANT ALL PRIVILEGES ON celerydb.* TO 'celeryuser'@'%';
FLUSH PRIVILEGES;

