-- OPCIONAL Y DESTRUCTIVO: Borra todas las tablas del proyecto y sus datos.
-- Utilízalo únicamente si necesitas reiniciar la base de datos desde cero.

DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS catalog_items CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS physical_locations CASCADE;
DROP TABLE IF EXISTS categories CASCADE;