from contextlib import asynccontextmanager

from fastapi import FastAPI

from nucleo.conexion import conexion                          # capa 1
from nucleo.configuracion import CONFIGURACION                # capa 1
from presentacion.rutas.productos import router as productos  # capa 3


@asynccontextmanager
async def lifespan(app: FastAPI):
    await conexion.conectar(CONFIGURACION.base_datos)
    yield
    await conexion.cerrar()


app = FastAPI(lifespan=lifespan)

app.include_router(productos)