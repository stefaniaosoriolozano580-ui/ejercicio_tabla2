"""Capa 3 — Rutas de productos: recibe, delega y elige plantilla."""
from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from dominio import servicios
from nucleo.conexion import ConexionDep

router = APIRouter(tags=["productos"])

templates = Jinja2Templates(directory="presentacion/templates")


def no_encontrado(request: Request, producto_id: int):
    return templates.TemplateResponse(
        request=request,
        name="componentes/producto_no_encontrado.html",
        context={"producto_id": producto_id},
    )


@router.get("/productos")
async def listar_productos(request: Request, conn: ConexionDep):
    productos = await servicios.listar_productos(conn)
    return templates.TemplateResponse(
        request=request,
        name="productos.html",
        context={"productos": productos},
    )


@router.get("/productos/{producto_id}/editar")
async def editar_producto_vista(request: Request, conn: ConexionDep, producto_id: int):
    producto = await servicios.buscar_producto(conn, producto_id)
    if producto is None:
        return no_encontrado(request, producto_id)
    return templates.TemplateResponse(
        request=request,
        name="componentes/fila_editar.html",
        context={
            "producto": producto,
            "nombre": producto["nombre"],
            "precio": producto["precio"],
            "cantidad": producto["cantidad"],
            "descripcion": producto["descripcion"] or "",
            "errores": {},
        },
    )


@router.get("/productos/{producto_id}/cancelar")
async def cancelar_edicion_vista(request: Request, conn: ConexionDep, producto_id: int):
    producto = await servicios.buscar_producto(conn, producto_id)
    if producto is None:
        return no_encontrado(request, producto_id)
    return templates.TemplateResponse(
        request=request,
        name="componentes/fila_producto.html",
        context={"producto": producto},
    )


@router.post("/productos/{producto_id}")
async def guardar_producto_vista(
    request: Request,
    conn: ConexionDep,
    producto_id: int,
    nombre: Annotated[str | None, Form()] = None,
    precio: Annotated[str | None, Form()] = None,
    cantidad: Annotated[str | None, Form()] = None,
    descripcion: Annotated[str | None, Form()] = None,
):
    producto = await servicios.buscar_producto(conn, producto_id)
    if producto is None:
        return no_encontrado(request, producto_id)

    validado, errores = servicios.validar_producto(nombre, precio, cantidad, descripcion)
    if validado is None:
        return templates.TemplateResponse(
            request=request,
            name="componentes/fila_editar.html",
            status_code=422,
            context={
                "producto": producto,
                "nombre": nombre or "",
                "precio": precio or "",
                "cantidad": cantidad or "",
                "descripcion": descripcion or "",
                "errores": errores,
            },
        )

    actualizado = await servicios.actualizar_producto(conn, producto_id, validado)
    if actualizado is None:
        return no_encontrado(request, producto_id)
    return templates.TemplateResponse(
        request=request,
        name="componentes/fila_actualizada.html",
        context={"producto": actualizado},
    )


@router.delete("/productos/{producto_id}")
async def eliminar_producto_vista(request: Request, conn: ConexionDep, producto_id: int):
    if not await servicios.eliminar_producto(conn, producto_id):
        return no_encontrado(request, producto_id)
    return HTMLResponse("")