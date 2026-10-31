-- Ejecutar únicamente después de haber creado la base de datos en pgAdmin.
-- Las tablas independientes se crean primero, seguidas por las dependientes con llaves foráneas.

-- 1. Tabla de Categorías (Taxonomía controlada)
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    CONSTRAINT chk_category_name 
        CHECK (length(btrim(name)) > 0)
);

-- 2. Tabla de Ubicaciones Físicas (Edificio, Laboratorio, Anaquel)
CREATE TABLE IF NOT EXISTS physical_locations (
    location_id INTEGER PRIMARY KEY,
    building VARCHAR(100) NOT NULL,
    lab VARCHAR(100) NOT NULL,
    shelf_cabinet VARCHAR(100) NOT NULL,
    CONSTRAINT chk_location_details 
        CHECK (length(btrim(building)) > 0 AND length(btrim(lab)) > 0 AND length(btrim(shelf_cabinet)) > 0)
);

-- 3. Tabla de Usuarios (Para control de acceso basado en roles - RBAC)
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    role VARCHAR(50) NOT NULL,
    CONSTRAINT chk_user_email 
        CHECK (position('@' IN email) > 1),
    CONSTRAINT chk_user_role 
        CHECK (length(btrim(role)) > 0)
);

-- 4. Tabla Principal: Elementos del Catálogo (Catalog Items)
CREATE TABLE IF NOT EXISTS catalog_items (
    item_id INTEGER PRIMARY KEY,
    internal_code VARCHAR(100) NOT NULL UNIQUE,
    serial_number VARCHAR(100) UNIQUE,
    standardized_name VARCHAR(255) NOT NULL,
    technical_description TEXT NOT NULL,
    brand VARCHAR(255),
    model VARCHAR(255),
    category_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    CONSTRAINT fk_item_category 
        FOREIGN KEY (category_id) 
        REFERENCES categories (category_id) 
        ON DELETE RESTRICT,
    CONSTRAINT fk_item_location 
        FOREIGN KEY (location_id) 
        REFERENCES physical_locations (location_id) 
        ON DELETE RESTRICT,
    CONSTRAINT chk_item_name 
        CHECK (length(btrim(standardized_name)) > 0),
    CONSTRAINT chk_item_code 
        CHECK (length(btrim(internal_code)) > 0)
);

-- 5. Tabla de Registro de Auditoría (Audit Log - Historial de cambios inmutable)
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INTEGER PRIMARY KEY,
    item_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    action_performed VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    modified_attributes TEXT,
    CONSTRAINT fk_audit_item 
        FOREIGN KEY (item_id) 
        REFERENCES catalog_items (item_id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_audit_user 
        FOREIGN KEY (user_id) 
        REFERENCES users (user_id) 
        ON DELETE RESTRICT,
    CONSTRAINT chk_audit_action 
        CHECK (length(btrim(action_performed)) > 0)
);

-- Creación de índices en columnas de llaves foráneas para optimizar búsquedas y filtros
CREATE INDEX IF NOT EXISTS idx_items_category 
    ON catalog_items (category_id);

CREATE INDEX IF NOT EXISTS idx_items_location 
    ON catalog_items (location_id);

CREATE INDEX IF NOT EXISTS idx_audit_item 
    ON audit_logs (item_id);

CREATE INDEX IF NOT EXISTS idx_audit_user 
    ON audit_logs (user_id);