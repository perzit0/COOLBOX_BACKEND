from flask import Blueprint, request, jsonify
from app import db
from app.models import OpcionMenu

menus_bp = Blueprint("menus", __name__, url_prefix="/api/menus")


@menus_bp.get("")
def listar_menus():
    query = OpcionMenu.query
    if request.args.get("estado") == "activos":
        query = query.filter_by(EstadoRegistro=True)
    menus = query.order_by(OpcionMenu.Orden.asc(), OpcionMenu.IdOpcionMenu.asc()).all()
    return jsonify([m.to_dict() for m in menus]), 200


@menus_bp.post("")
def crear_menu():
    data = request.get_json(silent=True) or {}
    nombre = (data.get("nombre") or "").strip()
    if not nombre:
        return jsonify({"error": "El nombre de la opción de menú es obligatorio"}), 400

    id_padre = data.get("idPadre") or None
    if id_padre and not OpcionMenu.query.get(id_padre):
        return jsonify({"error": "El menú padre seleccionado no existe"}), 400

    menu = OpcionMenu(
        Nombre=nombre,
        Icono=(data.get("icono") or "").strip() or None,
        Ruta=(data.get("ruta") or "").strip() or None,
        IdPadre=id_padre,
        Orden=data.get("orden", 0),
        EstadoRegistro=data.get("estadoRegistro", True),
    )
    db.session.add(menu)
    db.session.commit()
    return jsonify(menu.to_dict()), 201


@menus_bp.put("/<int:id_menu>")
def actualizar_menu(id_menu):
    menu = OpcionMenu.query.get(id_menu)
    if not menu:
        return jsonify({"error": "Opción de menú no encontrada"}), 404

    data = request.get_json(silent=True) or {}

    if "nombre" in data:
        nombre = (data.get("nombre") or "").strip()
        if not nombre:
            return jsonify({"error": "El nombre no puede estar vacío"}), 400
        menu.Nombre = nombre

    if "icono" in data:
        menu.Icono = (data.get("icono") or "").strip() or None
    if "ruta" in data:
        menu.Ruta = (data.get("ruta") or "").strip() or None
    if "orden" in data:
        menu.Orden = data.get("orden", 0)
    if "idPadre" in data:
        id_padre = data.get("idPadre") or None
        if id_padre == id_menu:
            return jsonify({"error": "Un menú no puede ser padre de sí mismo"}), 400
        menu.IdPadre = id_padre
    if "estadoRegistro" in data:
        menu.EstadoRegistro = bool(data.get("estadoRegistro"))

    db.session.commit()
    return jsonify(menu.to_dict()), 200


@menus_bp.patch("/<int:id_menu>/desactivar")
def desactivar_menu(id_menu):
    menu = OpcionMenu.query.get(id_menu)
    if not menu:
        return jsonify({"error": "Opción de menú no encontrada"}), 404
    menu.EstadoRegistro = False
    db.session.commit()
    return jsonify(menu.to_dict()), 200


@menus_bp.patch("/<int:id_menu>/activar")
def activar_menu(id_menu):
    menu = OpcionMenu.query.get(id_menu)
    if not menu:
        return jsonify({"error": "Opción de menú no encontrada"}), 404
    menu.EstadoRegistro = True
    db.session.commit()
    return jsonify(menu.to_dict()), 200
