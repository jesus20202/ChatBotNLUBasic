from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProductoOut(BaseModel):
    id: int
    nombre: str
    categoria_id: int
    precio: float
    descripcion: Optional[str]
    marca: Optional[str]
    stock: int
    activo: bool
    fecha_creacion: Optional[datetime]

    class Config:
        orm_mode = True
