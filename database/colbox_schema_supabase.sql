-- =====================================================================
-- COLBOX - Módulo de Seguridad y Control de Acceso Centralizado
-- Script de creación de base de datos (PostgreSQL / Supabase)
-- Ejecuta esto en Supabase -> SQL Editor -> New query
-- =====================================================================

CREATE TABLE IF NOT EXISTS "Perfiles" (
    "IdPerfil"          SERIAL PRIMARY KEY,
    "Nombre"            VARCHAR(100) NOT NULL,
    "Descripcion"       VARCHAR(255),
    "EstadoRegistro"    BOOLEAN NOT NULL DEFAULT TRUE,
    "FechaCreacion"     TIMESTAMP NOT NULL DEFAULT NOW(),
    "FechaModificacion" TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS "Usuario" (
    "IdUsuario"         SERIAL PRIMARY KEY,
    "DNI"               VARCHAR(15),
    "Nombres"           VARCHAR(100) NOT NULL,
    "ApellidoPaterno"   VARCHAR(100) NOT NULL,
    "ApellidoMaterno"   VARCHAR(100),
    "Celular"           VARCHAR(20),
    "Email"             VARCHAR(150) NOT NULL UNIQUE,
    "Password"          VARCHAR(255) NOT NULL,
    "EstadoRegistro"    BOOLEAN NOT NULL DEFAULT TRUE,
    "FechaCreacion"     TIMESTAMP NOT NULL DEFAULT NOW(),
    "FechaModificacion" TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS "Usuario_Perfiles" (
    "IdUsuarioPerfil" SERIAL PRIMARY KEY,
    "IdUsuario"       INT NOT NULL REFERENCES "Usuario"("IdUsuario") ON DELETE CASCADE,
    "IdPerfil"        INT NOT NULL REFERENCES "Perfiles"("IdPerfil") ON DELETE CASCADE,
    "EstadoRegistro"  BOOLEAN NOT NULL DEFAULT TRUE,
    "FechaCreacion"   TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE ("IdUsuario", "IdPerfil")
);

CREATE TABLE IF NOT EXISTS "OpcionesMenu" (
    "IdOpcionMenu"   SERIAL PRIMARY KEY,
    "Nombre"         VARCHAR(100) NOT NULL,
    "Icono"          VARCHAR(100),
    "Ruta"           VARCHAR(150),
    "IdPadre"        INT REFERENCES "OpcionesMenu"("IdOpcionMenu") ON DELETE SET NULL,
    "Orden"          INT NOT NULL DEFAULT 0,
    "EstadoRegistro" BOOLEAN NOT NULL DEFAULT TRUE,
    "FechaCreacion"  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS "OpcionesMenu_Perfiles" (
    "IdOpcionMenuPerfil" SERIAL PRIMARY KEY,
    "IdOpcionMenu"       INT NOT NULL REFERENCES "OpcionesMenu"("IdOpcionMenu") ON DELETE CASCADE,
    "IdPerfil"           INT NOT NULL REFERENCES "Perfiles"("IdPerfil") ON DELETE CASCADE,
    "EstadoRegistro"     BOOLEAN NOT NULL DEFAULT TRUE,
    "FechaCreacion"      TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE ("IdOpcionMenu", "IdPerfil")
);

-- Datos de ejemplo
INSERT INTO "Perfiles" ("Nombre", "Descripcion") VALUES
    ('Administrador', 'Acceso total al sistema COLBOX'),
    ('Operativo', 'Gestión de almacén y stock'),
    ('Logística', 'Gestión de despachos y rutas')
ON CONFLICT DO NOTHING;

INSERT INTO "OpcionesMenu" ("Nombre", "Icono", "Ruta", "IdPadre", "Orden") VALUES
    ('Inicio', 'home', '/inicio', NULL, 1),
    ('Gestión de Usuarios', 'users', NULL, NULL, 2),
    ('Inventario', 'box', NULL, NULL, 3)
ON CONFLICT DO NOTHING;
