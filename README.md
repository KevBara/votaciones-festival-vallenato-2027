# Sistema de votaciones — Festival de la Leyenda Vallenata 2027

Aplicación web construida con Django y MySQL para administrar ediciones,
categorías, votaciones y opciones participantes.

## Requisitos

- Python 3.9 o superior.
- MySQL Community Server 8.0 o superior, iniciado y accesible desde el equipo.
- MySQL Workbench (para ejecutar el script de datos de prueba).

## Instalación en Windows

Abre PowerShell en la carpeta del proyecto y crea/activa un entorno virtual:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Si PowerShell no permite activar el entorno, puedes ejecutar los comandos de
Django con `.\venv\Scripts\python.exe` sin activarlo.

## Configurar MySQL

1. Inicia el servicio de MySQL Server.
2. En MySQL Workbench, conéctate al servidor local y crea el esquema:

   ```sql
   CREATE DATABASE IF NOT EXISTS festival_vallenato
       CHARACTER SET utf8mb4
       COLLATE utf8mb4_unicode_ci;
   ```

3. En la raíz del proyecto, crea un archivo `.env` junto a `manage.py` con las
   credenciales del servidor local. Ajusta el usuario y la contraseña a los
   que configuraste en MySQL:

   ```dotenv
   DB_NAME=festival_vallenato
   DB_USER=root
   DB_PASSWORD=tu_contraseña_local
   DJANGO_DEBUG=True
   DJANGO_SECRET_KEY=clave-local-solo-para-desarrollo
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
   DJANGO_CSRF_TRUSTED_ORIGINS=
   ```

   `.env` no se debe compartir ni subir al repositorio. Estos valores son
   únicamente para desarrollo local; para producción configura una clave
   secreta nueva, `DJANGO_DEBUG=False` y los dominios/orígenes reales.

## Crear las tablas y cargar los datos de prueba

El orden es importante: **Django debe crear primero las tablas; después se
ejecuta el SQL de datos de prueba**. El script inserta datos, pero no sustituye
las migraciones.

1. Desde PowerShell, en la raíz del proyecto, aplica las migraciones:

   ```powershell
   .\venv\Scripts\python.exe manage.py migrate
   ```

   Esto crea las tablas de Django, incluidas las de votaciones, usuarios y
   sesiones. Si falla con un error de conexión, verifica que MySQL esté
   iniciado y que `DB_NAME`, `DB_USER` y `DB_PASSWORD` en `.env` sean correctos.

2. En MySQL Workbench, abre el archivo
   [`votaciones/datos_prueba.sql`](votaciones/datos_prueba.sql) y ejecútalo
   completo contra el servidor local. El script selecciona el esquema
   `festival_vallenato` y carga una edición 2027 con categorías, votaciones
   abiertas y opciones de demostración. Es idempotente para esos datos y no
   crea usuarios ni contraseñas.

3. (Opcional) Comprueba en Workbench el resultado de la consulta `SELECT` que
   está al final del script.

**No ejecutes este SQL en producción.** Las opciones de ejemplo no incluyen
imágenes; la aplicación mostrará un placeholder. Para probar imágenes, edita
una opción en el admin de Django y configura su URL de imagen.

## Iniciar y probar la aplicación

Inicia el servidor desde PowerShell:

```powershell
.\venv\Scripts\python.exe manage.py runserver
```

Abre <http://127.0.0.1:8000/>. Crea una cuenta desde la aplicación e inicia
sesión; el script SQL no genera usuarios. Luego:

1. En Inicio, abre **Ediciones disponibles** y selecciona la edición 2027.
2. Entra a una categoría, abre su votación, elige una opción y confirma el voto.
3. Vuelve al detalle de esa votación para comprobar que se muestra tu elección
   y que no puedes votar una segunda vez.
4. Registra otro usuario para comprobar que puede votar de forma independiente.
5. Para probar una votación cerrada, cambia su estado o sus fechas desde el
   admin de Django.

Para acceder al admin, crea una cuenta de administración desde otra consola:

```powershell
.\venv\Scripts\python.exe manage.py createsuperuser
```

Para ejecutar las pruebas automatizadas:

```powershell
.\venv\Scripts\python.exe manage.py test votaciones
```

La restricción única de la base de datos y el bloqueo de la votación protegen
contra votos duplicados, incluidas solicitudes simultáneas.
