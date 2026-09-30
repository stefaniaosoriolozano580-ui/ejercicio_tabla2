"""Reglas de los productos.

No sabe de HTTP, no sabe de plantillas y no abre conexiones: las recibe.
"""
from pydantic import ValidationError

from dominio import repositorios
from dominio.esquemas import ProductoActualizar

MENSAJES = {
    "nombre": "El nombre es obligatorio (máximo 100 caracteres).",
    "precio": "El precio debe ser mayor que cero.",
    "cantidad": "La cantidad debe ser un entero mayor o igual que cero.",
}


def validar_producto(nombre, precio, cantidad, descripcion):
    """Devuelve (datos_validos, errores). Si hay errores, datos_validos es None."""
    errores = {}
    datos = {
        "nombre": (nombre or "").strip(),
        "descripcion": (descripcion or "").strip() or None,
    }

    try:
        datos["precio"] = float((precio or "").strip().replace(",", "."))
    except ValueError:
        errores["precio"] = "El precio debe ser un número."

    try:
        datos["cantidad"] = int((cantidad or "").strip())
    except ValueError:
        errores["cantidad"] = "La cantidad debe ser un número entero."

    validado = None
    try:
        validado = ProductoActualizar(**datos)
    except ValidationError as e:
        for err in e.errors():
            campo = err["loc"][0]
            if campo in MENSAJES:
                errores.setdefault(campo, MENSAJES[campo])

    if errores or validado is None:
        return None, errores
    return validado, {}


async def listar_productos(conn) -> list[dict]:
    return await repositorios.obtener_productos(conn)


async def buscar_producto(conn, producto_id: int) -> dict | None:
    return await repositorios.obtener_producto(conn, producto_id)


async def actualizar_producto(conn, producto_id: int, datos: ProductoActualizar) -> dict | None:
    """Actualiza y devuelve el producto guardado, o None si no existía."""
    ok = await repositorios.actualizar_producto(
        conn, producto_id, datos.nombre, datos.precio, datos.cantidad, datos.descripcion
    )
    if not ok:
        return None
    return await repositorios.obtener_producto(conn, producto_id)


async def eliminar_producto(conn, producto_id: int) -> bool:
    return await repositorios.eliminar_producto(conn, producto_id)