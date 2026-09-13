from flask import Blueprint, request, jsonify
from app import db
from app.models import Perfil

perfiles_bp = Blueprint("perfiles", __name__, url_prefix="/api/perfiles")


@perfiles_bp.get("")
def listar_perfiles():
    """Lista todos los perfiles. ?estado=activos para filtrar solo los activos."""
    query = Perfil.query
    estado = request.args.get("estado")
    if estado == "activos":
        query = query.filter_by(EstadoRegistro=True)
    perfiles = query.order_by(Perfil.IdPerfil.asc()).all()
    return jsonify([p.to_dict() for p in perfiles]), 200


@perfiles_bp.get("/<int:id_perfil>")
def obtener_perfil(id_perfil):
    perfil = Perfil.query.get(id_perfil)
    if not perfil:
        return jsonify({"error": "Perfil no encontrado"}), 404
    return jsonify(perfil.to_dict()), 200


@perfiles_bp.post("")
def crear_perfil():
    data = request.get_json(silent=True) or {}
    nombre = (data.get("nombre") or "").strip()

    if not nombre:
        return jsonify({"error": "El campo 'nombre' es obligatorio"}), 400
    if len(nombre) > 100:
        return jsonify({"error": "El nombre no puede superar los 100 caracteres"}), 400

    nuevo = Perfil(
        Nombre=nombre,
        Descripcion=(data.get("descripcion") or "").strip() or None,
        EstadoRegistro=data.get("estadoRegistro", True),
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(nuevo.to_dict()), 201


@perfiles_bp.put("/<int:id_perfil>")
def actualizar_perfil(id_perfil):
    perfil = Perfil.query.get(id_perfil)
    if not perfil:
        return jsonify({"error": "Perfil no encontrado"}), 404

    data = request.get_json(silent=True) or {}

    if "nombre" in data:
        nombre = (data.get("nombre") or "").strip()
        if not nombre:
            return jsonify({"error": "El campo 'nombre' no puede estar vacío"}), 400
        perfil.Nombre = nombre

    if "descripcion" in data:
        perfil.Descripcion = (data.get("descripcion") or "").strip() or None

    if "estadoRegistro" in data:
        perfil.EstadoRegistro = bool(data.get("estadoRegistro"))

    db.session.commit()
    return jsonify(perfil.to_dict()), 200


@perfiles_bp.patch("/<int:id_perfil>/desactivar")
def desactivar_perfil(id_perfil):
    """Baja lógica: no se elimina de la BD, solo se marca EstadoRegistro = 0."""
    perfil = Perfil.query.get(id_perfil)
    if not perfil:
        return jsonify({"error": "Perfil no encontrado"}), 404

    perfil.EstadoRegistro = False
    db.session.commit()
    return jsonify(perfil.to_dict()), 200


@perfiles_bp.patch("/<int:id_perfil>/activar")
def activar_perfil(id_perfil):
    perfil = Perfil.query.get(id_perfil)
    if not perfil:
        return jsonify({"error": "Perfil no encontrado"}), 404

    perfil.EstadoRegistro = True
    db.session.commit()
    return jsonify(perfil.to_dict()), 200


@perfiles_bp.delete("/<int:id_perfil>")
def eliminar_perfil_fisico(id_perfil):
    """Eliminación física — úsala solo en pruebas locales, no en el flujo normal."""
    perfil = Perfil.query.get(id_perfil)
    if not perfil:
        return jsonify({"error": "Perfil no encontrado"}), 404

    db.session.delete(perfil)
    db.session.commit()
    return jsonify({"mensaje": "Perfil eliminado"}), 200
