from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import Usuario
from app.routes.usuarios import validar_email_institucional, perfiles_de

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/registro")
def registro():
    """Autoregistro de un colaborador con correo institucional.
    Queda SIN perfil asignado — un Administrador debe asignarle uno
    después desde la pantalla de Usuarios (así se respeta RF-02:
    el perfil lo controla el módulo de seguridad, no el propio usuario)."""
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    nombres = (data.get("nombres") or "").strip()
    apellido_paterno = (data.get("apellidoPaterno") or "").strip()
    password = data.get("password") or ""

    if not nombres or not apellido_paterno:
        return jsonify({"error": "Nombres y apellido paterno son obligatorios"}), 400
    if not email:
        return jsonify({"error": "El correo es obligatorio"}), 400
    if not validar_email_institucional(email):
        dominio = current_app.config.get("DOMINIO_CORREO_INSTITUCIONAL")
        return jsonify({"error": f"El correo debe pertenecer al dominio {dominio}"}), 400
    if Usuario.query.filter_by(Email=email).first():
        return jsonify({"error": "Ya existe una cuenta con ese correo"}), 409
    if not password or len(password) < 6:
        return jsonify({"error": "La clave debe tener al menos 6 caracteres"}), 400

    usuario = Usuario(
        DNI=(data.get("dni") or "").strip() or None,
        Nombres=nombres,
        ApellidoPaterno=apellido_paterno,
        ApellidoMaterno=(data.get("apellidoMaterno") or "").strip() or None,
        Celular=(data.get("celular") or "").strip() or None,
        Email=email,
        Password=generate_password_hash(password),
        EstadoRegistro=True,
    )
    db.session.add(usuario)
    db.session.commit()

    return jsonify(usuario.to_dict(incluir_perfiles=[])), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Correo y clave son obligatorios"}), 400

    usuario = Usuario.query.filter_by(Email=email).first()
    if not usuario or not check_password_hash(usuario.Password, password):
        return jsonify({"error": "Correo o clave incorrectos"}), 401
    if not usuario.EstadoRegistro:
        return jsonify({"error": "Esta cuenta está desactivada. Contacta a un administrador."}), 403

    return jsonify(usuario.to_dict(incluir_perfiles=perfiles_de(usuario.IdUsuario))), 200
