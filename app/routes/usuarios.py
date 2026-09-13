from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash
from app import db
from app.models import Usuario, UsuarioPerfil, Perfil

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/api/usuarios")


def validar_email_institucional(email: str) -> bool:
    dominio = current_app.config.get("DOMINIO_CORREO_INSTITUCIONAL", "@coolbox.com")
    return bool(email) and email.lower().strip().endswith(dominio.lower())


def perfiles_de(id_usuario):
    asignaciones = (
        UsuarioPerfil.query.filter_by(IdUsuario=id_usuario, EstadoRegistro=True).all()
    )
    return [
        {"idPerfil": a.IdPerfil, "nombre": a.perfil.Nombre if a.perfil else None}
        for a in asignaciones
    ]


def _extraer_ids_perfiles(data) -> list:
    """Acepta tanto 'idsPerfiles': [1,2] (varios roles) como el antiguo
    'idPerfil': 1 (un solo rol), para no romper compatibilidad."""
    if "idsPerfiles" in data and isinstance(data.get("idsPerfiles"), list):
        return [int(i) for i in data["idsPerfiles"] if i]
    if data.get("idPerfil"):
        return [int(data["idPerfil"])]
    return []


def _asignar_perfiles(id_usuario, ids_perfiles):
    UsuarioPerfil.query.filter_by(IdUsuario=id_usuario).delete()
    for id_perfil in ids_perfiles:
        db.session.add(UsuarioPerfil(IdUsuario=id_usuario, IdPerfil=id_perfil))


@usuarios_bp.get("")
def listar_usuarios():
    query = Usuario.query
    if request.args.get("estado") == "activos":
        query = query.filter_by(EstadoRegistro=True)
    usuarios = query.order_by(Usuario.IdUsuario.asc()).all()
    return jsonify(
        [u.to_dict(incluir_perfiles=perfiles_de(u.IdUsuario)) for u in usuarios]
    ), 200


@usuarios_bp.get("/<int:id_usuario>")
def obtener_usuario(id_usuario):
    usuario = Usuario.query.get(id_usuario)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(usuario.to_dict(incluir_perfiles=perfiles_de(id_usuario))), 200


@usuarios_bp.post("")
def crear_usuario():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    nombres = (data.get("nombres") or "").strip()
    apellido_paterno = (data.get("apellidoPaterno") or "").strip()
    password = data.get("password") or ""
    ids_perfiles = _extraer_ids_perfiles(data)

    if not nombres or not apellido_paterno:
        return jsonify({"error": "Nombres y apellido paterno son obligatorios"}), 400
    if not email:
        return jsonify({"error": "El correo es obligatorio"}), 400
    if not validar_email_institucional(email):
        dominio = current_app.config.get("DOMINIO_CORREO_INSTITUCIONAL")
        return jsonify({"error": f"El correo debe pertenecer al dominio {dominio}"}), 400
    if Usuario.query.filter_by(Email=email).first():
        return jsonify({"error": "Ya existe un usuario con ese correo"}), 409
    if not password or len(password) < 6:
        return jsonify({"error": "La clave debe tener al menos 6 caracteres"}), 400
    for id_perfil in ids_perfiles:
        if not Perfil.query.get(id_perfil):
            return jsonify({"error": "Uno de los perfiles seleccionados no existe"}), 400

    usuario = Usuario(
        DNI=(data.get("dni") or "").strip() or None,
        Nombres=nombres,
        ApellidoPaterno=apellido_paterno,
        ApellidoMaterno=(data.get("apellidoMaterno") or "").strip() or None,
        Celular=(data.get("celular") or "").strip() or None,
        Email=email,
        Password=generate_password_hash(password),
        EstadoRegistro=data.get("estadoRegistro", True),
    )
    db.session.add(usuario)
    db.session.flush()  # obtiene IdUsuario antes del commit

    if ids_perfiles:
        _asignar_perfiles(usuario.IdUsuario, ids_perfiles)

    db.session.commit()
    return jsonify(usuario.to_dict(incluir_perfiles=perfiles_de(usuario.IdUsuario))), 201


@usuarios_bp.put("/<int:id_usuario>")
def actualizar_usuario(id_usuario):
    usuario = Usuario.query.get(id_usuario)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    data = request.get_json(silent=True) or {}

    if "email" in data:
        email = (data.get("email") or "").strip().lower()
        if not validar_email_institucional(email):
            dominio = current_app.config.get("DOMINIO_CORREO_INSTITUCIONAL")
            return jsonify({"error": f"El correo debe pertenecer al dominio {dominio}"}), 400
        existente = Usuario.query.filter_by(Email=email).first()
        if existente and existente.IdUsuario != id_usuario:
            return jsonify({"error": "Ya existe otro usuario con ese correo"}), 409
        usuario.Email = email

    for campo, atributo in [
        ("dni", "DNI"),
        ("nombres", "Nombres"),
        ("apellidoPaterno", "ApellidoPaterno"),
        ("apellidoMaterno", "ApellidoMaterno"),
        ("celular", "Celular"),
    ]:
        if campo in data:
            setattr(usuario, atributo, (data.get(campo) or "").strip() or None)

    if data.get("password"):
        if len(data["password"]) < 6:
            return jsonify({"error": "La clave debe tener al menos 6 caracteres"}), 400
        usuario.Password = generate_password_hash(data["password"])

    if "estadoRegistro" in data:
        usuario.EstadoRegistro = bool(data.get("estadoRegistro"))

    if "idsPerfiles" in data or "idPerfil" in data:
        ids_perfiles = _extraer_ids_perfiles(data)
        for id_perfil in ids_perfiles:
            if not Perfil.query.get(id_perfil):
                return jsonify({"error": "Uno de los perfiles seleccionados no existe"}), 400
        _asignar_perfiles(id_usuario, ids_perfiles)

    db.session.commit()
    return jsonify(usuario.to_dict(incluir_perfiles=perfiles_de(id_usuario))), 200


@usuarios_bp.get("/pendientes")
def listar_usuarios_pendientes():
    """Usuarios activos que se autoregistraron pero todavía no tienen
    ningún perfil asignado — a la espera de que un administrador los apruebe."""
    usuarios = Usuario.query.filter_by(EstadoRegistro=True).order_by(
        Usuario.IdUsuario.asc()
    ).all()
    pendientes = [u for u in usuarios if not perfiles_de(u.IdUsuario)]
    return jsonify(
        [u.to_dict(incluir_perfiles=[]) for u in pendientes]
    ), 200


@usuarios_bp.patch("/<int:id_usuario>/desactivar")
def desactivar_usuario(id_usuario):
    usuario = Usuario.query.get(id_usuario)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    usuario.EstadoRegistro = False
    db.session.commit()
    return jsonify(usuario.to_dict(incluir_perfiles=perfiles_de(id_usuario))), 200


@usuarios_bp.patch("/<int:id_usuario>/activar")
def activar_usuario(id_usuario):
    usuario = Usuario.query.get(id_usuario)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    usuario.EstadoRegistro = True
    db.session.commit()
    return jsonify(usuario.to_dict(incluir_perfiles=perfiles_de(id_usuario))), 200
