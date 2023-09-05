from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from config.db import client

from datetime import datetime, timedelta
from dateutil import relativedelta

from models.responses import CobrosDiaResponse, CobrosResumenMesResponse

cobros = APIRouter()

# Seleccionamos la base de datos:
db = client.challenge_set

def obtener_datos_cobros_mes_negocio(mes_anio, negocio):
    month, year = map(int, mes_anio.split('-'))
    
    # Obtener el _id del negocio desde la colección "merchants"
    merchant = db.merchants.find_one({"name": negocio})
    if not merchant:
        return None  # El negocio no fue encontrado
    
    merchant_id = merchant["_id"]
    
    # Construir fechas de inicio y fin del mes
    fecha_inicio_mes = datetime(year, month, 1)
    fecha_fin_mes = fecha_inicio_mes + relativedelta.relativedelta(months=1)
    
    # Consulta para cobros de Altas
    query_altas = {
        "merchant_id": merchant_id,
        "source": {"$in": ["checkout", "checkout3", "checkout_miclub"]},
        "date_created": {"$gte": fecha_inicio_mes, "$lt": fecha_fin_mes},
        "status": "approved"
    }
    
    # Consulta para cobros de Recurrencia
    query_recurrencia = {
        "merchant_id": merchant_id,
        "source": {"$in": ["recurring_charges", "recurring_miclub"]},
        "original_payment_date": {"$gte": fecha_inicio_mes, "$lt": fecha_fin_mes},
        "status": "approved"
    }
    
    # Realizar las consultas y procesar los resultados
    cobros_altas = db.boletas.find(query_altas)
    cobros_recurrencia = db.boletas.find(query_recurrencia)
    
    # Agrupar los cobros por día y sumarlos
    cobros_por_dia = {}
    
    for c in cobros_altas:
        fecha = c["date_created"].date()
        cobros_por_dia.setdefault(fecha, {"altas": 0, "recurrencias": 0})
        cobros_por_dia[fecha]["altas"] += c["charges_detail"]["final_price"]
    
    for c in cobros_recurrencia:
        fecha = c["original_payment_date"].date()
        cobros_por_dia.setdefault(fecha, {"altas": 0, "recurrencias": 0})
        cobros_por_dia[fecha]["recurrencias"] += c["charges_detail"]["final_price"]
    
    # Estructurar los datos en una lista de diccionarios
    datos_cobros = [
        {
            "fecha": fecha.strftime("%Y-%m-%d"),
            "altas": cobros["altas"],
            "recurrencias": cobros["recurrencias"]
        }
        for fecha, cobros in sorted(cobros_por_dia.items())
    ]
    
    return datos_cobros

def obtener_total_cobrado_mes_negocio(mes_anio, negocio):
    month, year = map(int, mes_anio.split('-'))
    
    # Obtener el _id del negocio desde la colección "merchants"
    merchant = db.merchants.find_one({"name": negocio})
    if not merchant:
        return None  # El negocio no fue encontrado
    
    merchant_id = merchant["_id"]
    
    # Construir fechas de inicio y fin del mes
    fecha_inicio_mes = datetime(year, month, 1)
    fecha_fin_mes = fecha_inicio_mes + relativedelta.relativedelta(months=1)
    
    # Consulta para cobros de Altas y Recurrencia
    query = {
        "merchant_id": merchant_id,
        "$or": [
            {
                "source": {"$in": ["checkout", "checkout3", "checkout_miclub"]},
                "date_created": {"$gte": fecha_inicio_mes, "$lt": fecha_fin_mes},
                "status": "approved"
            },
            {
                "source": {"$in": ["recurring_charges", "recurring_miclub"]},
                "original_payment_date": {"$gte": fecha_inicio_mes, "$lt": fecha_fin_mes},
                "status": "approved"
            }
        ]
    }
    
    # Realizar la consulta y calcular el valor total cobrado
    cobros = db.boletas.find(query)
    total_cobrado = sum(c["charges_detail"]["final_price"] for c in cobros)
    
    return total_cobrado

def calcular_variacion_total_cobrado(mes_anio, negocio):
    month, year = map(int, mes_anio.split('-'))
    
    # Obtener el _id del negocio desde la colección "merchants"
    merchant = db.merchants.find_one({"name": negocio})
    if not merchant:
        return None  # El negocio no fue encontrado
    
    merchant_id = merchant["_id"]
    
    # Construir fechas de inicio y fin del mes actual
    fecha_inicio_mes_actual = datetime(year, month, 1)
    fecha_fin_mes_actual = fecha_inicio_mes_actual + relativedelta.relativedelta(months=1)
    
    # Construir fechas de inicio y fin del mes anterior
    fecha_inicio_mes_anterior = fecha_inicio_mes_actual - relativedelta.relativedelta(months=1)
    fecha_fin_mes_anterior = fecha_inicio_mes_actual
    
    # Calcular la cantidad de días equivalentes al mes anterior
    dias_mes_anterior = fecha_inicio_mes_actual.day
    
    # Consultar el monto total de altas para el mes actual y el mes anterior
    total_altas_mes_actual = obtener_total_cobrado_mes_negocio(mes_anio, negocio)
    total_altas_mes_anterior = obtener_total_cobrado_mes_negocio(fecha_inicio_mes_anterior.strftime("%m-%Y"), negocio)
    
    # Calcular la variación del monto de altas
    if total_altas_mes_anterior > 0:
        variacion_porcentaje = ((total_altas_mes_actual - total_altas_mes_anterior) / total_altas_mes_anterior) * 100
    else:
        variacion_porcentaje = 0
    
    return variacion_porcentaje

def obtener_total_recurrencias_mes_negocio(mes_anio, negocio):
    month, year = map(int, mes_anio.split('-'))
    
    # Obtener el _id del negocio desde la colección "merchants"
    merchant = db.merchants.find_one({"name": negocio})
    if not merchant:
        return None  # El negocio no fue encontrado
    
    merchant_id = merchant["_id"]
    
    # Construir fechas de inicio y fin del mes
    fecha_inicio_mes = datetime(year, month, 1)
    fecha_fin_mes = fecha_inicio_mes + relativedelta.relativedelta(months=1)
    
    # Consulta para cobros de Recurrencia
    query_recurrencia = {
        "merchant_id": merchant_id,
        "source": {"$in": ["recurring_charges", "recurring_miclub"]},
        "original_payment_date": {"$gte": fecha_inicio_mes, "$lt": fecha_fin_mes},
        "status": "approved"
    }
    
    # Realizar la consulta y calcular el valor total cobrado por recurrencias
    cobros_recurrencia = db.boletas.find(query_recurrencia)
    total_recurrencias = sum(c["charges_detail"]["final_price"] for c in cobros_recurrencia)
    
    return total_recurrencias

def calcular_variacion_monto_recurrencias(mes_anio, negocio):
    month, year = map(int, mes_anio.split('-'))
    
    # Obtener el _id del negocio desde la colección "merchants"
    merchant = db.merchants.find_one({"name": negocio})
    if not merchant:
        return None  # El negocio no fue encontrado
    
    merchant_id = merchant["_id"]
    
    # Construir fechas de inicio y fin del mes actual
    fecha_inicio_mes_actual = datetime(year, month, 1)
    fecha_fin_mes_actual = fecha_inicio_mes_actual + relativedelta.relativedelta(months=1)
    
    # Construir fechas de inicio y fin del mes anterior
    fecha_inicio_mes_anterior = fecha_inicio_mes_actual - relativedelta.relativedelta(months=1)
    fecha_fin_mes_anterior = fecha_inicio_mes_actual
    
    # Calcular la cantidad de días equivalentes al mes anterior
    dias_mes_anterior = fecha_inicio_mes_actual.day
    
    # Consultar el monto total de altas para el mes actual y el mes anterior
    total_altas_mes_actual = obtener_total_recurrencias_mes_negocio(mes_anio, negocio)
    total_altas_mes_anterior = obtener_total_recurrencias_mes_negocio(fecha_inicio_mes_anterior.strftime("%m-%Y"), negocio)
    
    # Calcular la variación del monto de altas
    if total_altas_mes_anterior > 0:
        variacion_porcentaje = ((total_altas_mes_actual - total_altas_mes_anterior) / total_altas_mes_anterior) * 100
    else:
        variacion_porcentaje = 0
    
    return variacion_porcentaje

def obtener_total_altas_mes_negocio(mes_anio, negocio):
    month, year = map(int, mes_anio.split('-'))
    
    # Obtener el _id del negocio desde la colección "merchants"
    merchant = db.merchants.find_one({"name": negocio})
    if not merchant:
        return None  # El negocio no fue encontrado
    
    merchant_id = merchant["_id"]
    
    # Construir fechas de inicio y fin del mes
    fecha_inicio_mes = datetime(year, month, 1)
    fecha_fin_mes = fecha_inicio_mes + relativedelta.relativedelta(months=1)
    
    # Consulta para cobros de Altas
    query_altas = {
        "merchant_id": merchant_id,
        "source": {"$in": ["checkout", "checkout3", "checkout_miclub"]},
        "date_created": {"$gte": fecha_inicio_mes, "$lt": fecha_fin_mes},
        "status": "approved"
    }
    
    # Realizar la consulta y calcular el valor total cobrado por altas
    cobros_altas = db.boletas.find(query_altas)
    total_altas = sum(c["charges_detail"]["final_price"] for c in cobros_altas)
    
    return total_altas

def calcular_variacion_monto_altas(mes_anio, negocio):
    month, year = map(int, mes_anio.split('-'))
    
    # Obtener el _id del negocio desde la colección "merchants"
    merchant = db.merchants.find_one({"name": negocio})
    if not merchant:
        return None  # El negocio no fue encontrado
    
    merchant_id = merchant["_id"]
    
    # Construir fechas de inicio y fin del mes actual
    fecha_inicio_mes_actual = datetime(year, month, 1)
    fecha_fin_mes_actual = fecha_inicio_mes_actual + relativedelta.relativedelta(months=1)
    
    # Construir fechas de inicio y fin del mes anterior
    fecha_inicio_mes_anterior = fecha_inicio_mes_actual - relativedelta.relativedelta(months=1)
    fecha_fin_mes_anterior = fecha_inicio_mes_actual
    
    # Calcular la cantidad de días equivalentes al mes anterior
    dias_mes_anterior = fecha_inicio_mes_actual.day
    
    # Consultar el monto total de altas para el mes actual y el mes anterior
    total_altas_mes_actual = obtener_total_altas_mes_negocio(mes_anio, negocio)
    total_altas_mes_anterior = obtener_total_altas_mes_negocio(fecha_inicio_mes_anterior.strftime("%m-%Y"), negocio)
    
    # Calcular la variación del monto de altas
    if total_altas_mes_anterior > 0:
        variacion_porcentaje = ((total_altas_mes_actual - total_altas_mes_anterior) / total_altas_mes_anterior) * 100
    else:
        variacion_porcentaje = 0
    
    return variacion_porcentaje

# Ruta para el Objetivo 2
@cobros.get("/cobros/{negocio}/{mes_anio}", response_model=CobrosDiaResponse, tags=["Cobros del mes"])
def cobros_por_dia(negocio: str, mes_anio: str):
    # Llamamos a la función para obtener los datos de cobros por día
    datos_cobros = obtener_datos_cobros_mes_negocio(mes_anio, negocio)
    
    if not datos_cobros:
        return JSONResponse(content={"message": "No se encontraron datos para el negocio y mes especificados"}, status_code=404)
    
    # Devolver los datos como respuesta JSON
    return JSONResponse(content=datos_cobros)

# Ruta para el Objetivo 3
@cobros.get("/cobros_resumen/{negocio}/{mes_anio}", response_model=CobrosResumenMesResponse, tags=["Cobros del mes"])
def resumen_cobros_mes(negocio: str, mes_anio: str):
    
    # Construir el objeto de respuesta
    resumen_cobros = {
        "Total Cobrado": obtener_total_cobrado_mes_negocio(mes_anio, negocio),
        "Variación Total Cobrado respecto al mes anterior (%)": calcular_variacion_total_cobrado(mes_anio, negocio),
        "Total Cobrado por Recurrencias": obtener_total_recurrencias_mes_negocio(mes_anio, negocio),
        "Variación Total Cobrado por Recurrencias respecto al mes anterior (%)": calcular_variacion_monto_recurrencias(mes_anio, negocio),
        "Total Cobrado por Altas": obtener_total_altas_mes_negocio(mes_anio, negocio),
        "Variación Total Cobrado por Altas respecto al mes anterior (%)": calcular_variacion_monto_altas(mes_anio, negocio),
    }
    
    if all(value == None for value in resumen_cobros.values()):
            # Manejo de error si los datos no se encuentran
            raise HTTPException(status_code=404, detail="No se encontraron datos para el negocio y mes especificados")

    # Devolvemos los datos como una respuesta JSON
    return JSONResponse(content=resumen_cobros)