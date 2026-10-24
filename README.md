# votaciones-festival-vallenato-2027
Sistema web de votaciones para el Festival de la Leyenda Vallenata 2027. Desarrollado con Python, Django y MySQL para la administración de ediciones, categorías y opciones de votación.

# Sistema Web de Votaciones - Festival de la Leyenda Vallenata 2027

Este repositorio contiene el código fuente correspondiente a la **Entrega 2** del sistema de votaciones web para el Festival de la Leyenda Vallenata 2027. Desarrollado bajo la arquitectura Django MVT (Model-View-Template) y base de datos relacional MySQL.

**Requisitos Previos**
- Python 3.9 o superior.
- MySQL Community Server (v8.0+) y MySQL Workbench.
- Git.

**1. Clonar el repositorio y preparar el entorno**
Clona el proyecto en tu máquina local y accede a la carpeta raíz:
```bash
git clone <AQUI_PEGAS_LA_URL_DE_TU_REPOSITORIO>
cd <AQUI_PONES_EL_NOMBRE_DE_LA_CARPETA>
Crea y activa un entorno virtual para aislar las dependencias:

Windows:

Bash
python -m venv venv
venv\Scripts\activate
Mac/Linux:

Bash
python3 -m venv venv
source venv/bin/activate
Instala las librerías necesarias ejecutando:

Bash
pip install -r requirements.txt
2. Configuración de la Base de Datos (MySQL)
Abre MySQL Workbench, inicia sesión con tu usuario root y ejecuta la siguiente instrucción SQL para crear la base de datos del proyecto:

SQL
CREATE DATABASE festival_vallenato;
3. Variables de Entorno (.env)
Para proteger las credenciales locales, este proyecto utiliza variables de entorno. Crea un archivo llamado estrictamente .env en la raíz del proyecto (al mismo nivel que manage.py) y agrega el siguiente contenido, reemplazando la contraseña por la de tu instalación local de MySQL:

Fragmento de código
DB_NAME=festival_vallenato
DB_USER=root
DB_PASSWORD=tu_contraseña_real_aqui
(Nota: El archivo .env está excluido del repositorio por seguridad en el .gitignore).

4. Migraciones y Ejecución
Conecta la estructura de Django a tu base de datos local y levanta el servidor de desarrollo:

Bash
python manage.py migrate
python manage.py runserver
Abre tu navegador web e ingresa a http://127.0.0.1:8000/ para visualizar la aplicación en funcionamiento.

Equipo de Desarrollo

Integrante 1: Arquitectura, Infraestructura y Repositorio.

Integrante 2: Modelado de Datos y Backend.

Integrante 3: Autenticación y Vistas (Frontend).

Integrante 4: QA, Administración (Django Admin) y Documentación.