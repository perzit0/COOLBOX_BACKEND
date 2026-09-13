from datetime import datetime
from app import db


class Perfil(db.Model):
    __tablename__ = "Perfiles"

    IdPerfil = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(100), nullable=False)
    Descripcion = db.Column(db.String(255), nullable=True)
    EstadoRegistro = db.Column(db.Boolean, nullable=False, default=True)
    FechaCreacion = db.Column(db.DateTime, default=datetime.utcnow)
    FechaModificacion = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "idPerfil": self.IdPerfil,
            "nombre": self.Nombre,
            "descripcion": self.Descripcion,
            "estadoRegistro": bool(self.EstadoRegistro),
            "fechaCreacion": self.FechaCreacion.isoformat() if self.FechaCreacion else None,
            "fechaModificacion": self.FechaModificacion.isoformat()
            if self.FechaModificacion
            else None,
        }


class Usuario(db.Model):
    __tablename__ = "Usuario"

    IdUsuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DNI = db.Column(db.String(15), nullable=True)
    Nombres = db.Column(db.String(100), nullable=False)
    ApellidoPaterno = db.Column(db.String(100), nullable=False)
    ApellidoMaterno = db.Column(db.String(100), nullable=True)
    Celular = db.Column(db.String(20), nullable=True)
    Email = db.Column(db.String(150), nullable=False, unique=True)
    Password = db.Column(db.String(255), nullable=False)
    EstadoRegistro = db.Column(db.Boolean, nullable=False, default=True)
    FechaCreacion = db.Column(db.DateTime, default=datetime.utcnow)
    FechaModificacion = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self, incluir_perfiles=None):
        data = {
            "idUsuario": self.IdUsuario,
            "dni": self.DNI,
            "nombres": self.Nombres,
            "apellidoPaterno": self.ApellidoPaterno,
            "apellidoMaterno": self.ApellidoMaterno,
            "celular": self.Celular,
            "email": self.Email,
            "estadoRegistro": bool(self.EstadoRegistro),
        }
        if incluir_perfiles is not None:
            data["perfiles"] = incluir_perfiles
        return data


class UsuarioPerfil(db.Model):
    __tablename__ = "Usuario_Perfiles"

    IdUsuarioPerfil = db.Column(db.Integer, primary_key=True, autoincrement=True)
    IdUsuario = db.Column(db.Integer, db.ForeignKey("Usuario.IdUsuario"), nullable=False)
    IdPerfil = db.Column(db.Integer, db.ForeignKey("Perfiles.IdPerfil"), nullable=False)
    EstadoRegistro = db.Column(db.Boolean, nullable=False, default=True)
    FechaCreacion = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship("Usuario", backref="perfiles_asignados")
    perfil = db.relationship("Perfil", backref="usuarios_asignados")

    def to_dict(self):
        return {
            "idUsuarioPerfil": self.IdUsuarioPerfil,
            "idUsuario": self.IdUsuario,
            "idPerfil": self.IdPerfil,
            "estadoRegistro": bool(self.EstadoRegistro),
        }


class OpcionMenu(db.Model):
    __tablename__ = "OpcionesMenu"

    IdOpcionMenu = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(100), nullable=False)
    Icono = db.Column(db.String(100), nullable=True)
    Ruta = db.Column(db.String(150), nullable=True)
    IdPadre = db.Column(db.Integer, db.ForeignKey("OpcionesMenu.IdOpcionMenu"), nullable=True)
    Orden = db.Column(db.Integer, nullable=False, default=0)
    EstadoRegistro = db.Column(db.Boolean, nullable=False, default=True)
    FechaCreacion = db.Column(db.DateTime, default=datetime.utcnow)

    hijos = db.relationship("OpcionMenu", backref=db.backref("padre", remote_side=[IdOpcionMenu]))

    def to_dict(self):
        return {
            "idOpcionMenu": self.IdOpcionMenu,
            "nombre": self.Nombre,
            "icono": self.Icono,
            "ruta": self.Ruta,
            "idPadre": self.IdPadre,
            "orden": self.Orden,
            "estadoRegistro": bool(self.EstadoRegistro),
        }


class OpcionMenuPerfil(db.Model):
    __tablename__ = "OpcionesMenu_Perfiles"

    IdOpcionMenuPerfil = db.Column(db.Integer, primary_key=True, autoincrement=True)
    IdOpcionMenu = db.Column(
        db.Integer, db.ForeignKey("OpcionesMenu.IdOpcionMenu"), nullable=False
    )
    IdPerfil = db.Column(db.Integer, db.ForeignKey("Perfiles.IdPerfil"), nullable=False)
    EstadoRegistro = db.Column(db.Boolean, nullable=False, default=True)
    FechaCreacion = db.Column(db.DateTime, default=datetime.utcnow)

    opcion_menu = db.relationship("OpcionMenu", backref="permisos")
    perfil = db.relationship("Perfil", backref="permisos_menu")

    def to_dict(self):
        return {
            "idOpcionMenuPerfil": self.IdOpcionMenuPerfil,
            "idOpcionMenu": self.IdOpcionMenu,
            "idPerfil": self.IdPerfil,
            "estadoRegistro": bool(self.EstadoRegistro),
        }
