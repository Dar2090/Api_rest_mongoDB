from fastapi import FastAPI

from routes.resumen import resumen
from routes.cobros import cobros
from routes.graficos import graficos

app = FastAPI(
        title="API Rest con Python y MongoDB",
        description="El objetivo es construir una API que sirva de backend de una plataforma web de gestión de una cadena de negocios.",
        version="0.0.1",
)

app.include_router(resumen)
app.include_router(cobros)
app.include_router(graficos)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)