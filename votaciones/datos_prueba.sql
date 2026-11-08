-- Base de datos local usada por core/settings.py (DB_NAME=festival_vallenato).
-- Primero ejecutar: python manage.py migrate
-- Luego ejecutar este archivo completo en MySQL Workbench.
-- No usar en producción.
CREATE DATABASE IF NOT EXISTS festival_vallenato
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE festival_vallenato;

START TRANSACTION;

INSERT INTO votaciones_edicion
    (nombre, anio, fecha_inicio, fecha_fin, descripcion)
SELECT
    'Festival de la Leyenda Vallenata',
    2027,
    '2027-04-01',
    '2027-04-30',
    'Edición local de prueba'
WHERE NOT EXISTS (
    SELECT 1 FROM votaciones_edicion WHERE anio = 2027
);

SET @edicion_id = (
    SELECT id FROM votaciones_edicion WHERE anio = 2027
);

INSERT INTO votaciones_categoria
    (edicion_id, nombre, descripcion, habilitada)
SELECT @edicion_id, datos.nombre, datos.descripcion, 1
FROM (
    SELECT 'Acordeoneros' AS nombre, 'Categoría de acordeoneros' AS descripcion
    UNION ALL
    SELECT 'Canción inédita', 'Categoría de canciones inéditas'
    UNION ALL
    SELECT 'Piqueria', 'Categoría de piqueria'
) AS datos
WHERE NOT EXISTS (
    SELECT 1
    FROM votaciones_categoria c
    WHERE c.edicion_id = @edicion_id AND c.nombre = datos.nombre
);

UPDATE votaciones_categoria
SET habilitada = 1
WHERE edicion_id = @edicion_id;

INSERT INTO votaciones_votacion
    (categoria_id, titulo, descripcion, fecha_inicio, fecha_fin, activa)
SELECT c.id, CONCAT('Votación de prueba: ', c.nombre),
       'Votación de demostración. No usar en producción.',
       UTC_TIMESTAMP() - INTERVAL 1 DAY,
       UTC_TIMESTAMP() + INTERVAL 30 DAY,
       1
FROM votaciones_categoria c
WHERE c.edicion_id = @edicion_id
  AND NOT EXISTS (
      SELECT 1
      FROM votaciones_votacion v
      WHERE v.categoria_id = c.id
        AND v.titulo = CONCAT('Votación de prueba: ', c.nombre)
  );

UPDATE votaciones_votacion v
JOIN votaciones_categoria c ON c.id = v.categoria_id
SET v.activa = 1,
    v.fecha_inicio = UTC_TIMESTAMP() - INTERVAL 1 DAY,
    v.fecha_fin = UTC_TIMESTAMP() + INTERVAL 30 DAY
WHERE c.edicion_id = @edicion_id
  AND v.id > 0
  AND v.titulo = CONCAT('Votación de prueba: ', c.nombre);

INSERT INTO votaciones_opcion
    (votacion_id, nombre, descripcion, imagen_url)
SELECT v.id, datos.nombre, datos.descripcion, ''
FROM votaciones_votacion v
JOIN votaciones_categoria c ON c.id = v.categoria_id
JOIN (
    SELECT 'Acordeoneros' AS categoria, 'Participante A' AS nombre,
           'Opción de demostración' AS descripcion
    UNION ALL
    SELECT 'Acordeoneros', 'Participante B', 'Opción de demostración'
    UNION ALL
    SELECT 'Canción inédita', 'Canción de prueba A', 'Opción de demostración'
    UNION ALL
    SELECT 'Canción inédita', 'Canción de prueba B', 'Opción de demostración'
    UNION ALL
    SELECT 'Piqueria', 'Verseador de prueba A', 'Opción de demostración'
    UNION ALL
    SELECT 'Piqueria', 'Verseador de prueba B', 'Opción de demostración'
) AS datos ON datos.categoria = c.nombre
WHERE c.edicion_id = @edicion_id
  AND v.titulo = CONCAT('Votación de prueba: ', c.nombre)
  AND NOT EXISTS (
      SELECT 1
      FROM votaciones_opcion o
      WHERE o.votacion_id = v.id AND o.nombre = datos.nombre
  );

COMMIT;

-- Para comprobar las opciones y URLs desde el navegador:
SELECT e.anio, c.nombre AS categoria, v.id AS votacion_id,
       v.titulo, o.id AS opcion_id, o.nombre AS opcion
FROM votaciones_edicion e
JOIN votaciones_categoria c ON c.edicion_id = e.id
JOIN votaciones_votacion v ON v.categoria_id = c.id
JOIN votaciones_opcion o ON o.votacion_id = v.id
WHERE e.anio = 2027
  AND v.titulo = CONCAT('Votación de prueba: ', c.nombre)
ORDER BY c.nombre, o.id;
