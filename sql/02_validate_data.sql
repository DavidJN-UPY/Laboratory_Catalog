-- 1. Verificar los conteos esperados por tabla (Esperado: 4, 3, 3, 8, 2)
SELECT 'categories' AS table_name, COUNT(*) AS rows FROM categories
UNION ALL
SELECT 'physical_locations', COUNT(*) FROM physical_locations
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'catalog_items', COUNT(*) FROM catalog_items
UNION ALL
SELECT 'audit_logs', COUNT(*) FROM audit_logs;

-- 2. Relaciones: Listar cada equipo con su categoría y ubicación exacta
SELECT i.internal_code, i.standardized_name, c.name AS category, 
       CONCAT(p.building, ' - ', p.lab, ' (', p.shelf_cabinet, ')') AS exact_location
FROM catalog_items AS i
JOIN categories AS c ON c.category_id = i.category_id
JOIN physical_locations AS p ON p.location_id = i.location_id
ORDER BY i.item_id;

-- 3. Prueba de integridad referencial: Debe retornar cero filas (sin referencias rotas)
SELECT i.item_id, i.category_id
FROM catalog_items AS i
LEFT JOIN categories AS c ON c.category_id = i.category_id
WHERE c.category_id IS NULL;