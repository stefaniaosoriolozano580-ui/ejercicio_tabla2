"""Capa 1 — Conexión. Abre y cierra el pool; entrega conexiones a quien las pida."""
from typing import Annotated, AsyncGenerator

import asyncpg
from fastapi import Depends


class Conexion:
    """Abre y cierra el pool. No sabe qué es un producto."""

    def __init__(self) -> None:
        self.pool: asyncpg.Pool | None = None

    async def conectar(self, url: str) -> None:
        if self.pool is not None:
            return
        self.pool = await asyncpg.create_pool(dsn=url, min_size=1, max_size=10)

    async def cerrar(self) -> None:
        if self.pool is not None:
            await self.pool.close()
            self.pool = None


conexion = Conexion()


async def get_conexion() -> AsyncGenerator[asyncpg.Connection, None]:
    """Dependencia de FastAPI: cede una conexión del pool y la devuelve sola."""
    if conexion.pool is None:
        raise RuntimeError("El pool no está abierto.")
    async with conexion.pool.acquire() as conn:
        yield conn


ConexionDep = Annotated[asyncpg.Connection, Depends(get_conexion)]