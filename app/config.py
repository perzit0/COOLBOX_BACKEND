import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Supabase (PostgreSQL) — puedes usar la cadena completa con DATABASE_URL
    # (la que te da Supabase en Project Settings > Database > Connection string)
    # o armarla a partir de las piezas sueltas.
    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:
        # Supabase entrega el URI como "postgresql://...";
        # SQLAlchemy necesita el driver psycopg2 explícito.
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace(
            "postgresql://", "postgresql+psycopg2://", 1
        )
    else:
        DB_USER = os.getenv("DB_USER", "postgres")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "")
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = os.getenv("DB_PORT", "5432")
        DB_NAME = os.getenv("DB_NAME", "postgres")
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    JSON_SORT_KEYS = False

    # Dominio institucional permitido para el correo de Usuario
    DOMINIO_CORREO_INSTITUCIONAL = os.getenv("DOMINIO_CORREO_INSTITUCIONAL", "@coolbox.com")

    # En local dejamos "*" (cualquier origen). En producción (Render) se
    # setea ALLOWED_ORIGIN con la URL exacta del frontend en Vercel,
    # ej: https://colbox-frontend.vercel.app
    ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "*")
