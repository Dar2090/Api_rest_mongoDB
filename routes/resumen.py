from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from config.db import client

from datetime import datetime, timedelta
from dateutil import relativedelta

from models.responses import ResumenMesResponse

resumen = APIRouter()

# Seleccionamos la base de datos:
db = client.challenge_set

def clientes_activos(mes, negocio):
    
    month, year = map(int, mes.split('-'))

    # Obtenemos el _id del negocio desde la colección merchants
    merchant = db.merchants.find_one({"name": negocio})
    if not merchant:
        return 0  # El negocio no fue encontrado

    merchant_id = merchant["_id"]

    # Obtenemos los _id de planes asociados a ese negocio desde la colección planes
    planes_ids = [plan["_id"] for plan in db.planes.find({"merchant_id": merchant_id}, {"_id": 1})]

    fecha_inicio_mes = datetime(year, month, 1)
    fecha_fin_mes = min(fecha_inicio_mes + relativedelta.relativedelta(months=1), datetime(2023, 6, 11))

    query = {
        "$and": [
            {
                "$or": [
                    {
                        "history": {
                            "$elemMatch": {
                                "event": "alta",
                                "date_created": {"$lt": fecha_fin_mes}
                            }
                        }
                    },
                    {
                        "history": {
                            "$elemMatch": {
                                "event": "inactivacion",
                                "date_created": {"$gte": fecha_inicio_mes, "$lt": fecha_fin_mes}
                            }
                        }
                    }
                ]
            },
            {
                "history": {
                    "$not": {
                        "$elemMatch": {
                            "event": {"$in": ["baja", "inactivacion"]},
                            "date_created": {"$lt": fecha_inicio_mes}
                        }
                    }
                }
            },
            {
                "history.plan": {"$in": planes_ids}  # Filtramos por los planes del negocio
            }
        ]
    }

    clientes_count = db.clientes.count_documents(query)  # Obtenemos la cantidad de clientes activos
    return clientes_count

def porcentaje_variacion_socios_activos_mes_negocio(mes, negocio):
    month, year = map(int, mes.split('-'))
    
    fecha_inicio_mes = datetime(year, month, 1)
    fecha_inicio_mes_anterior = fecha_inicio_mes - relativedelta.relativedelta(months=1)
    
    clientes_activos_mes_actual = clientes_activos(mes, negocio)
    clientes_activos_mes_anterior = clientes_activos(fecha_inicio_mes_anterior.strftime("%m-%Y"), negocio)
    
    if clientes_activos_mes_anterior > 0:
        variacion_porcentaje = ((clientes_activos_mes_actual - clientes_activos_mes_anterior) / clientes_activos_mes_anterior) * 100
    else:
        variacion_porcentaje = 0
    
    return variacion_porcentaje

def cantidad_altas_mes(mes, negocio):
    month, year = map(int, mes.split('-'))

    # Obtenemos el _id del negocio desde la colección merchants
    merchant = db.merchants.find_one({"name": negocio})
    if not merchant:
        return 0  # El negocio no fue encontrado

    merchant_id = merchant["_id"]

    # Obtenemos los _id de planes asociados a ese negocio desde la colección planes
    planes_ids = [plan["_id"] for plan in db.planes.find({"merchant_id": merchant_id}, {"_id": 1})]

    fecha_inicio_mes = datetime(year, month, 1)
    fecha_fin_mes = min(fecha_inicio_mes + relativedelta.relativedelta(months=1), datetime(2023, 6, 11))

    query = {
        "$and": [
            {
                "history": {
                    "$elemMatch": {
                        "event": "alta",
                        "date_created": {"$gte": fecha_inicio_mes, "$lt": fecha_fin_mes}
                    }
                }
            },
            {
                "history": {
                    "$not": {
                        "$elemMatch": {
                            "event": {"$in": ["baja", "inactivacion"]},
                            "date_created": {"$lt": fecha_inicio_mes}
                        }
                    }
                }
            },
            {
                "history.plan": {"$in": planes_ids}  # Filtramos por los planes del negocio
            }
        ]
    }

    altas_count = db.clientes.count_documents(query)  # Obtenemos la cantidad de altas de clientes activos
    return altas_count

def porcentaje_variacion_altas(mes, negocio):
    month, year = map(int, mes.split('-'))
    
    fecha_inicio_mes = datetime(year, month, 1)
    fecha_inicio_mes_anterior = fecha_inicio_mes - relativedelta.relativedelta(months=1)
    
    altas_mes_actual = cantidad_altas_mes(mes, negocio)  # Cambio de nombre de la variable
    altas_mes_anterior = cantidad_altas_mes(fecha_inicio_mes_anterior.strftime("%m-%Y"), negocio)  # Cambio de nombre de la variable
    
    if altas_mes_anterior > 0:
        variacion_porcentaje = ((altas_mes_actual - altas_mes_anterior) / altas_mes_anterior) * 100
    else:
        variacion_porcentaje = 0
    
    return variacion_porcentaje

def cantidad_bajas_mes(mes, negocio):
    month, year = map(int, mes.split('-'))

    # Obtenemos el _id del negocio desde la colección merchants
    merchant = db.merchants.find_one({"name": negocio})
    if not merchant:
        return 0  # El negocio no fue encontrado

    merchant_id = merchant["_id"]

    # Obtenemos los _id de planes asociados a ese negocio desde la colección planes
    planes_ids = [plan["_id"] for plan in db.planes.find({"merchant_id": merchant_id}, {"_id": 1})]

    fecha_inicio_mes = datetime(year, month, 1)
    fecha_fin_mes = min(fecha_inicio_mes + relativedelta.relativedelta(months=1), datetime(2023, 6, 11))

    query = {
        "$and": [
            {
                "history": {
                    "$elemMatch": {
                        "event": "baja",
                        "date_created": {"$lt": fecha_fin_mes}
                    }
                }
            },
            {
                "history": {
                    "$not": {
                        "$elemMatch": {
                            "event": {"$in": ["inactivacion"]},
                            "date_created": {"$lt": fecha_inicio_mes}
                        }
                    }
                }
            },
            {
                "history.plan": {"$in": planes_ids}  # Filtramos por los planes del negocio
            }
        ]
    }

    bajas_count = db.clientes.count_documents(query)  # Obtenemos la cantidad de bajas de clientes activos
    return bajas_count

def porcentaje_variacion_bajas(mes, negocio):
    month, year = map(int, mes.split('-'))
    
    fecha_inicio_mes = datetime(year, month, 1)
    fecha_inicio_mes_anterior = fecha_inicio_mes - relativedelta.relativedelta(months=1)
    
    bajas_mes_actual = cantidad_bajas_mes(mes, negocio)  # Cambio de nombre de la variable
    bajas_mes_anterior = cantidad_bajas_mes(fecha_inicio_mes_anterior.strftime("%m-%Y"), negocio)  # Cambio de nombre de la variable
    
    if bajas_mes_anterior > 0:
        variacion_porcentaje = ((bajas_mes_actual - bajas_mes_anterior) / bajas_mes_anterior) * 100
    else:
        variacion_porcentaje = 0
    
    return variacion_porcentaje

def cantidad_inactivaciones_sin_baja_mes(mes, negocio):
    month, year = map(int, mes.split('-'))

    # Obtenemos el _id del negocio desde la colección merchants
    merchant = db.merchants.find_one({"name": negocio})
    if not merchant:
        return 0  # El negocio no fue encontrado

    merchant_id = merchant["_id"]

    # Obtenemos los _id de planes asociados a ese negocio desde la colección planes
    planes_ids = [plan["_id"] for plan in db.planes.find({"merchant_id": merchant_id}, {"_id": 1})]

    fecha_inicio_mes = datetime(year, month, 1)
    fecha_fin_mes = min(fecha_inicio_mes + relativedelta.relativedelta(months=1), datetime(2023, 6, 11))

    query = {
        "$and": [
            {
                "history": {
                    "$elemMatch": {
                        "event": "inactivacion",
                        "date_created": {"$lt": fecha_fin_mes}
                    }
                }
            },
            {
                "history": {
                    "$not": {
                        "$elemMatch": {
                            "event": {"$in": ["baja"]},
                            "date_created": {"$lt": fecha_inicio_mes}
                        }
                    }
                }
            },
            {
                "history.plan": {"$in": planes_ids}  # Filtramos por los planes del negocio
            }
        ]
    }

    inactivaciones_sin_baja_count = db.clientes.count_documents(query)  # Obtenemos la cantidad de inactivaciones sin baja
    return inactivaciones_sin_baja_count

def porcentaje_variacion_inactivaciones_sin_bajas(mes, negocio):
    month, year = map(int, mes.split('-'))
    
    fecha_inicio_mes = datetime(year, month, 1)
    fecha_inicio_mes_anterior = fecha_inicio_mes - relativedelta.relativedelta(months=1)
    
    inactivaciones_sin_bajas_mes_actual = cantidad_inactivaciones_sin_baja_mes(mes, negocio)  # Cambio de nombre de la variable
    inactivaciones_sin_bajas_mes_anterior = cantidad_inactivaciones_sin_baja_mes(fecha_inicio_mes_anterior.strftime("%m-%Y"), negocio)  # Cambio de nombre de la variable
    
    if inactivaciones_sin_bajas_mes_anterior > 0:
        variacion_porcentaje = ((inactivaciones_sin_bajas_mes_actual - inactivaciones_sin_bajas_mes_anterior) / inactivaciones_sin_bajas_mes_anterior) * 100
    else:
        variacion_porcentaje = 0
    
    return variacion_porcentaje

# Ruta para el objetivo 1 Resumen del mes
@resumen.get("/resumen_mes/{negocio}/{mes_anio}", response_model=ResumenMesResponse, tags=["Resumen del mes"])
def movimiento_socios(negocio: str, mes_anio: str):
    datos = {
        "Cantidad de socios activos del mes": clientes_activos(mes_anio, negocio),
        "% variación de socios activos respecto al mes anterior": porcentaje_variacion_socios_activos_mes_negocio(mes_anio, negocio),
        "Cantidad de altas del mes": cantidad_altas_mes(mes_anio, negocio),
        "% variación de altas respecto al mes anterior": porcentaje_variacion_altas(mes_anio, negocio),
        "Cantidad de bajas del mes": cantidad_bajas_mes(mes_anio, negocio),
        "% variación de bajas respecto al mes anterior": porcentaje_variacion_bajas(mes_anio, negocio),
        "Cantidad de inactivaciones sin baja del mes": cantidad_inactivaciones_sin_baja_mes(mes_anio, negocio),
        "% variación de inactivaciones sin baja respecto al mes anterior": porcentaje_variacion_inactivaciones_sin_bajas(mes_anio, negocio),
    }

    if all(value == 0 for value in datos.values()):
        # Manejo de error si los datos no se encuentran
        raise HTTPException(status_code=404, detail="No se encontraron datos para el negocio y mes especificados")

    # Devolvemos los datos como una respuesta JSON
    return JSONResponse(content=datos)