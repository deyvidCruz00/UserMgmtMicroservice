-- Crear base de datos y tabla de clientes
CREATE DATABASE IF NOT EXISTS usermgmt_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE usermgmt_db;

CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document VARCHAR(50) NOT NULL UNIQUE,
    firstname VARCHAR(100) NOT NULL,
    lastname VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    INDEX idx_document (document),
    INDEX idx_email (email)
);

INSERT INTO customers (document, firstname, lastname, address, phone, email) VALUES
('12345678', 'Juan', 'Pérez', 'Calle 123 #45-67', '3001234567', 'juan.perez@email.com'),
('87654321', 'María', 'González', 'Carrera 45 #23-89', '3009876543', 'maria.gonzalez@email.com')
ON DUPLICATE KEY UPDATE id=id;

-- Eliminar usuario si existe (para reinicios)
DROP USER IF EXISTS 'fastapi'@'%';

-- Crear usuario con mysql_native_password
CREATE USER 'fastapi'@'%' IDENTIFIED WITH mysql_native_password BY 'fastapipass';

-- Dar permisos sobre la base de datos
GRANT ALL PRIVILEGES ON usermgmt_db.* TO 'fastapi'@'%';
FLUSH PRIVILEGES;

FLUSH PRIVILEGES;