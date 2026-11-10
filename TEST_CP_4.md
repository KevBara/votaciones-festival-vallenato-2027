# Pruebas Persona 4 (CP-01 a CP-10)

Se agregó `votaciones/test_persona4.py` sin reemplazar ni modificar `votaciones/tests.py`,
para conservar las pruebas automatizadas existentes de los integrantes anteriores.

## Ejecutar solo las pruebas de Persona 4

```powershell
python manage.py test votaciones.test_persona4
```

## Ejecutar todas las pruebas de la aplicación

```powershell
python manage.py test votaciones
```

Django debe poder conectarse a MySQL y el usuario de base de datos debe tener permisos
para crear y eliminar la base de datos temporal de pruebas. Las pruebas crean sus propios
datos; no requieren cargar `datos_prueba.sql`.

## Correspondencia CP

- CP-01: registro de usuario.
- CP-02: inicio de sesión.
- CP-03: cierre de sesión.
- CP-04: consulta de edición y categorías.
- CP-05: consulta de votaciones y opciones.
- CP-06: API de categorías en JSON.
- CP-07: bloqueo de voto sin autenticación.
- CP-08: registro de voto válido y persistencia.
- CP-09: prevención de votos duplicados.
- CP-10: historial personal y consulta administrativa.

## Importante

Los casos automatizados verifican respuestas y datos en la base de datos de pruebas de Django.
Para el informe académico, registra el resultado real de ejecución y conserva las capturas
del navegador, del JSON o de MySQL que correspondan. No declares una prueba aprobada
hasta ejecutarla en el entorno del proyecto.
