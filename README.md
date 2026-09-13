# COLBOX — Backend (Flask + PostgreSQL local)

API REST del Módulo de Seguridad de COLBOX: Perfiles, Usuarios (con
validación de correo institucional), Menú jerárquico y Permisos por
perfil. Corre todo en local — la base de datos también, por ahora
(Supabase lo dejamos para más adelante).

## 1. Requisitos previos
- Python 3.10+
- PostgreSQL instalado en tu máquina:
  - Windows: descarga el instalador en https://www.postgresql.org/download/windows/
    (incluye pgAdmin). Durante la instalación te pide una contraseña
    para el usuario `postgres` — anótala.
  - macOS: `brew install postgresql@16` (o Postgres.app)
  - Linux: `sudo apt install postgresql`

## 2. Crear la base de datos local
Con PostgreSQL instalado y corriendo, abre una terminal y ejecuta:
```bash
psql -U postgres -h localhost -c "CREATE DATABASE colbox_db;"
```
(Te pedirá la contraseña que pusiste al instalar. En Windows también
puedes hacerlo desde **pgAdmin**: clic derecho en "Databases" -> "Create" -> "Database...", nombre `colbox_db`.)

Luego carga las tablas:
```bash
psql -U postgres -h localhost -d colbox_db -f database/colbox_schema.sql
```
O ábrelo y ejecútalo desde el **Query Tool** de pgAdmin si prefieres GUI.
Esto crea las 5 tablas + datos de ejemplo (3 perfiles) **y un usuario
administrador semilla** para que puedas entrar desde cero:

- **Correo:** `admin@coolbox.com`
- **Clave:** `Admin123`

Ya tiene el perfil "Administrador" asignado, así que desde ese usuario
puedes crear/editar a los demás colaboradores y asignarles perfiles.

Si ya habías corrido el script antes (sin este usuario), puedes volver
a correrlo tal cual — usa `ON CONFLICT DO NOTHING`, así que no duplica
nada de lo que ya tienes.

## 3. Crear y activar el entorno virtual

**Windows (PowerShell):**
```powershell
cd backend
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
venv\Scripts\activate
```

**macOS / Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

## 4. Instalar las librerías
```bash
pip install -r requirements.txt
```
Incluye: Flask, Flask-SQLAlchemy, Flask-CORS, psycopg2-binary (driver de
Postgres — sirve igual para local que para Supabase más adelante),
python-dotenv, marshmallow y Werkzeug (hash de contraseñas).

## 5. Configurar las variables de entorno
```bash
copy .env.example .env      # Windows
cp .env.example .env        # macOS/Linux
```
Abre `.env` y coloca la contraseña que usaste al instalar PostgreSQL en
`DB_PASSWORD`. Ajusta `DOMINIO_CORREO_INSTITUCIONAL` si no es `@coolbox.com`.

## 6. Levantar el servidor
```bash
python run.py
```
Backend en `http://localhost:5000`.

**Cada vez que arranca**, el backend verifica si existe el usuario
`admin@coolbox.com` (clave `Admin123`) con el perfil "Administrador" —
si no existe, lo crea automáticamente. Así nunca te quedas sin forma
de entrar, sin importar en qué máquina levantes el proyecto.

## 7. Flujo de aprobación de cuentas nuevas
1. Un colaborador crea su cuenta desde la pantalla de login ("Crear cuenta").
2. Queda **sin perfil**, en estado "pendiente".
3. El Administrador entra con `admin@coolbox.com`, va a **Aprobaciones**,
   le asigna uno o más perfiles y confirma.
4. Desde ese momento el colaborador puede iniciar sesión con acceso normal.

## 7. Endpoints disponibles

**Perfiles** (`/api/perfiles`) — GET, GET/<id>, POST, PUT/<id>,
PATCH/<id>/desactivar, PATCH/<id>/activar, DELETE/<id>

**Usuarios** (`/api/usuarios`) — GET, GET/<id>, POST, PUT/<id>,
PATCH/<id>/desactivar, PATCH/<id>/activar
- Valida que el correo termine en el dominio institucional configurado.
- La clave se guarda con hash (nunca en texto plano).
- Un usuario puede tener **varios perfiles a la vez**: manda `idsPerfiles`
  como lista (sigue aceptando `idPerfil` con un solo valor por compatibilidad).

Ejemplo (POST /api/usuarios):
```json
{
  "dni": "89887997",
  "nombres": "Juan",
  "apellidoPaterno": "Palacios",
  "apellidoMaterno": "Torre",
  "celular": "988788779",
  "email": "juan.palacios@coolbox.com",
  "password": "claveSegura123",
  "idsPerfiles": [1, 2]
}
```

**Autenticación** (`/api/auth`)
- `POST /api/auth/registro` — autoregistro con correo institucional.
  Queda **sin perfil asignado**; un administrador se lo asigna después
  desde la pantalla de Usuarios (así se respeta RF-02: el perfil lo
  controla el módulo de seguridad, no el propio usuario).
- `POST /api/auth/login` — `{ "email": "...", "password": "..." }`,
  devuelve los datos del usuario y sus perfiles si la clave es correcta
  y la cuenta está activa.

**Menús** (`/api/menus`) — GET, POST, PUT/<id>,
PATCH/<id>/desactivar, PATCH/<id>/activar
- `idPadre` en null/omitido = opción raíz del menú; con valor = submenú.

**Permisos** (`/api/permisos`)
- `GET /api/permisos/perfil/<idPerfil>` — lista todas las opciones de menú
  marcando cuáles tiene asignadas ese perfil.
- `PUT /api/permisos/perfil/<idPerfil>` — reemplaza los permisos del perfil.
  Body: `{ "idsOpcionMenu": [1, 3, 5] }`

**Salud:** `GET /api/health`

## Notas
- Todo corre en `localhost` por ahora — incluida la base de datos.
  Cuando quieran pasar a Supabase, solo hay que cambiar las variables
  de `.env` (`DATABASE_URL`); el código no cambia, porque ya usa el
  mismo driver de PostgreSQL (`psycopg2`).
