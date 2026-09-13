"""Punto de entrada para servidores WSGI de producción (Render usa esto,
no run.py, que es solo para desarrollo local con el servidor de Flask)."""
from app import create_app

app = create_app()
