from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

ADMIN_EMAIL = "admin@coolbox.com"
ADMIN_PASSWORD = "Admin123"


def _asegurar_admin_inicial(app):
    """Crea el perfil Administrador y el usuario admin@coolbox.com
    si todavía no existen. Se ejecuta cada vez que arranca run.py,
    así nunca te quedas sin forma de entrar al sistema."""
    from werkzeug.security import generate_password_hash
    from app.models import Usuario, Perfil, UsuarioPerfil

    with app.app_context():
        try:
            perfil_admin = Perfil.query.filter_by(Nombre="Administrador").first()
            if not perfil_admin:
                perfil_admin = Perfil(
                    Nombre="Administrador", Descripcion="Acceso total al sistema COLBOX"
                )
                db.session.add(perfil_admin)
                db.session.flush()

            admin = Usuario.query.filter_by(Email=ADMIN_EMAIL).first()
            if not admin:
                admin = Usuario(
                    Nombres="Admin",
                    ApellidoPaterno="COLBOX",
                    Email=ADMIN_EMAIL,
                    Password=generate_password_hash(ADMIN_PASSWORD),
                    EstadoRegistro=True,
                )
                db.session.add(admin)
                db.session.flush()

            ya_tiene_rol = UsuarioPerfil.query.filter_by(
                IdUsuario=admin.IdUsuario, IdPerfil=perfil_admin.IdPerfil
            ).first()
            if not ya_tiene_rol:
                db.session.add(
                    UsuarioPerfil(IdUsuario=admin.IdUsuario, IdPerfil=perfil_admin.IdPerfil)
                )

            db.session.commit()
        except Exception as e:
            # Si las tablas todavía no existen (no corriste el script SQL
            # todavía), no tumbamos el arranque del servidor por esto.
            db.session.rollback()
            print(f"[COLBOX] Aviso: no se pudo verificar/crear el admin inicial: {e}")


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    CORS(app, origins=app.config.get("ALLOWED_ORIGIN", "*"))

    from app.routes.perfiles import perfiles_bp
    from app.routes.usuarios import usuarios_bp
    from app.routes.menus import menus_bp
    from app.routes.permisos import permisos_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(perfiles_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(menus_bp)
    app.register_blueprint(permisos_bp)
    app.register_blueprint(auth_bp)

    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "colbox-backend"}, 200

    _asegurar_admin_inicial(app)

    return app
