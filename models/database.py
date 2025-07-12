from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL, ForeignKey, TIMESTAMP, JSON
from sqlalchemy.orm import relationship
from database.connection import Base

class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text)
    categoria_padre_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    activo = Column(Boolean, default=True)

    categoria_padre = relationship("Categoria", remote_side=[id])
    productos = relationship("Producto", back_populates="categoria")

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    precio = Column(DECIMAL(10,2), nullable=False)
    descripcion = Column(Text)
    marca = Column(String(100))
    stock = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(TIMESTAMP)

    categoria = relationship("Categoria", back_populates="productos")

class UsuarioSesion(Base):
    __tablename__ = "usuarios_sesiones"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String(50))
    user_agent = Column(Text)
    fecha_inicio = Column(TIMESTAMP)
    fecha_ultimo_acceso = Column(TIMESTAMP)
    activo = Column(Boolean, default=True)

    conversaciones = relationship("Conversacion", back_populates="usuario_sesion")
    intenciones = relationship("IntencionDetectada", back_populates="usuario_sesion")

class Conversacion(Base):
    __tablename__ = "conversaciones"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), ForeignKey("usuarios_sesiones.session_id"))
    mensaje_usuario = Column(Text, nullable=False)
    respuesta_bot = Column(Text, nullable=False)
    intencion_detectada = Column(String(100))
    entidades_extraidas = Column(JSON)
    contexto_bd = Column(JSON)
    tiempo_respuesta_ms = Column(Integer)
    fecha_creacion = Column(TIMESTAMP)

    usuario_sesion = relationship("UsuarioSesion", back_populates="conversaciones")

class IntencionDetectada(Base):
    __tablename__ = "intenciones_detectadas"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), ForeignKey("usuarios_sesiones.session_id"))
    intencion = Column(String(100), nullable=False)
    confianza = Column(DECIMAL(3,2))
    entidades = Column(JSON)
    mensaje_original = Column(Text)
    productos_consultados = Column(JSON)
    resultado_exitoso = Column(Boolean)
    fecha_deteccion = Column(TIMESTAMP)

    usuario_sesion = relationship("UsuarioSesion", back_populates="intenciones")