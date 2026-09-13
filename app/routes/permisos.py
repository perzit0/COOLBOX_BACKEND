from flask import Blueprint, request, jsonify
from app import db
from app.models import OpcionMenuPerfil, OpcionMenu, Perfil

permisos_bp = Blueprint("permisos", __name__, url_prefix="/api/permisos")


@permisos_bp.get("/perfil/<int:id_perfil>")
def listar_permisos_por_perfil(id_perfil):
    """Devuelve TODAS las opciones de menú activas, marcando cuáles
    tiene habilitadas el perfil (para pintar los checkboxes en el front)."""
    if not Perfil.query.get(id_perfil):
        return jsonify({"error": "Perfil no encontrado"}), 404

    menus = OpcionMenu.query.filter_by(EstadoRegistro=True).order_by(
        OpcionMenu.Orden.asc()
    ).all()
    asignados = {
        p.IdOpcionMenu
        for p in OpcionMenuPerfil.query.filter_by(
            IdPerfil=id_perfil, EstadoRegistro=True
        ).all()
    }

    return jsonify(
        [
            {
                "idOpcionMenu": m.IdOpcionMenu,
                "nombre": m.Nombre,
                "idPadre": m.IdPadre,
                "asignado": m.IdOpcionMenu in asignados,
            }
            for m in menus
        ]
    ), 200


@permisos_bp.put("/perfil/<int:id_perfil>")
def guardar_permisos_por_perfil(id_perfil):
    """Reemplaza los permisos de un perfil con la lista de idOpcionMenu recibida."""
    if not Perfil.query.get(id_perfil):
        return jsonify({"error": "Perfil no encontrado"}), 404

    data = request.get_json(silent=True) or {}
    ids_menu = data.get("idsOpcionMenu", [])
    if not isinstance(ids_menu, list):
        return jsonify({"error": "idsOpcionMenu debe ser una lista de IDs"}), 400

    OpcionMenuPerfil.query.filter_by(IdPerfil=id_perfil).delete()
    for id_menu in ids_menu:
        if OpcionMenu.query.get(id_menu):
            db.session.add(OpcionMenuPerfil(IdPerfil=id_perfil, IdOpcionMenu=id_menu))

    db.session.commit()
    return jsonify({"mensaje": "Permisos actualizados", "total": len(ids_menu)}), 200
