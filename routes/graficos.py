from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from config.db import client

from datetime import datetime, timedelta
from dateutil import relativedelta

from models.responses import GraficosResponse

graficos = APIRouter()

# Seleccionamos la base de datos:
db = client.challenge_set

def obtener_tipos_cobro_y_plan_ids(negocio):
    # Obtener el _id del negocio desde la colección "merchants"
    merchant = db.merchants.find_one({"name": negocio})
    if not merchant:
        return None  # El negocio no fue encontrado

    merchant_id = merchant["_id"]

    # Obtener los tipos de cobro (Mensual o Anual) y sus respectivos plan_ids
    tipos_cobro = {}

    # Obtener los planes asociados al negocio
    planes = db.planes.find({"merchant_id": merchant_id})

    for plan in planes:
        plan_id = plan["_id"]
        plan_sede_local = plan.get("sede_local", "")  # Si no existe, se guarda como cadena vacía
        tipo_cobro = plan["cobro"]

        if tipo_cobro not in tipos_cobro:
            tipos_cobro[tipo_cobro] = []

        if plan_id not in tipos_cobro[tipo_cobro]:
            tipos_cobro[tipo_cobro].append(plan_id)

        if plan_sede_local and plan_sede_local != plan_id and plan_sede_local not in tipos_cobro[tipo_cobro]:
            tipos_cobro[tipo_cobro].append(plan_sede_local)

    return tipos_cobro

def calcular_porcentaje_cobro_tipos_cobro(mes_anio, negocio):
    # Obtener el _id del negocio desde la colección "merchants"
    merchant = db.merchants.find_one({"name": negocio})
    if not merchant:
        return None  # El negocio no fue encontrado

    merchant_id = merchant["_id"]

    # Obtener los tipos de cobro y plan_ids asociados al negocio
    tipos_cobro_y_plan_ids = obtener_tipos_cobro_y_plan_ids(negocio)

    if not tipos_cobro_y_plan_ids:
        return None  # No se encontraron tipos de cobro

    # Parsear el mes-año en una fecha
    month, year = map(int, mes_anio.split('-'))
    fecha_inicio_mes = datetime(year, month, 1)
    fecha_fin_mes = fecha_inicio_mes + relativedelta.relativedelta(months=1)

    # Consultar las boletas cobradas para el mes-año y negocio especificados (Mensual)
    query_mensual = {
        "merchant_id": merchant_id,
        "status": "approved",
        "plan_id": {"$in": tipos_cobro_y_plan_ids["Mensual"]},
        "$or": [
            {"date_created": {"$gte": fecha_inicio_mes, "$lt": fecha_fin_mes}},
            {"original_payment_date": {"$gte": fecha_inicio_mes, "$lt": fecha_fin_mes}},
        ],
    }

    # Consultar las boletas cobradas para el mes-año y negocio especificados (Anual)
    query_anual = {
        "merchant_id": merchant_id,
        "status": "approved",
        "plan_id": {"$in": tipos_cobro_y_plan_ids["Anual"]},
        "$or": [
            {"date_created": {"$gte": fecha_inicio_mes, "$lt": fecha_fin_mes}},
            {"original_payment_date": {"$gte": fecha_inicio_mes, "$lt": fecha_fin_mes}},
        ],
    }

    # Obtener las boletas que coinciden con la consulta (Mensual)
    boletas_mensual = db.boletas.find(query_mensual)

    # Obtener las boletas que coinciden con la consulta (Anual)
    boletas_anual = db.boletas.find(query_anual)

    # Calcular el monto total cobrado por cada tipo de cobro (Mensual)
    total_cobrado_mensual = sum(boleta["charges_detail"]["final_price"] for boleta in boletas_mensual)

    # Calcular el monto total cobrado por cada tipo de cobro (Anual)
    total_cobrado_anual = sum(boleta["charges_detail"]["final_price"] for boleta in boletas_anual)

    # Calcular el porcentaje de dinero cobrado por cada tipo de cobro
    total_cobrado_mes_actual = total_cobrado_mensual + total_cobrado_anual
    
    if total_cobrado_mes_actual > 0:
        porcentajes = {
            "Mensual": (total_cobrado_mensual / total_cobrado_mes_actual) * 100,
            "Anual": (total_cobrado_anual / total_cobrado_mes_actual) * 100,
        }
    else:
        porcentajes = None

    return porcentajes

def obtener_niveles_acceso_y_plan_ids(negocio):
    # Obtener el _id del negocio desde la colección "merchants"
    merchant = db.merchants.find_one({"name": negocio})
    if not merchant:
        return None  # El negocio no fue encontrado

    merchant_id = merchant["_id"]

    # Obtener los niveles de acceso (Local, Plus, Total) y sus respectivos plan_ids
    niveles_acceso = {}

    # Obtener los planes asociados al negocio
    planes = db.planes.find({"merchant_id": merchant_id})

    for plan in planes:
        plan_id = plan["_id"]
        plan_sede_local = plan.get("sede_local", "")  # Si no existe, se guarda como cadena vacía
        nivel_acceso = plan.get("nivel_de_acceso", "")  # Obtener el nivel de acceso del plan

        if nivel_acceso not in niveles_acceso:
            niveles_acceso[nivel_acceso] = []

        if plan_id not in niveles_acceso[nivel_acceso]:
            niveles_acceso[nivel_acceso].append(plan_id)

        if plan_sede_local and plan_sede_local != plan_id and plan_sede_local not in niveles_acceso[nivel_acceso]:
            niveles_acceso[nivel_acceso].append(plan_sede_local)

    return niveles_acceso

def calcular_porcentaje_cobro_niveles_acceso(mes_anio, negocio):
    # Obtener el _id del negocio desde la colección "merchants"
    merchant = db.merchants.find_one({"name": negocio})
    if not merchant:
        return None  # El negocio no fue encontrado

    merchant_id = merchant["_id"]

    # Obtener los niveles de acceso y plan_ids asociados al negocio
    niveles_acceso_y_plan_ids = obtener_niveles_acceso_y_plan_ids(negocio)

    if not niveles_acceso_y_plan_ids:
        return None  # No se encontraron niveles de acceso

    # Parsear el mes-año en una fecha
    month, year = map(int, mes_anio.split('-'))
    fecha_inicio_mes = datetime(year, month, 1)
    fecha_fin_mes = fecha_inicio_mes + relativedelta.relativedelta(months=1)

    # Consultar las boletas cobradas para el mes-año y negocio especificados
    query = {
        "merchant_id": merchant_id,
        "status": "approved",
        "$or": [
            {"plan_id": {"$in": niveles_acceso_y_plan_ids["Local"]}},
            {"plan_id": {"$in": niveles_acceso_y_plan_ids["Plus"]}},
            {"plan_id": {"$in": niveles_acceso_y_plan_ids["Total"]}},
        ],
        "$or": [
            {"date_created": {"$gte": fecha_inicio_mes, "$lt": fecha_fin_mes}},
            {"original_payment_date": {"$gte": fecha_inicio_mes, "$lt": fecha_fin_mes}},
        ],
    }

    # Obtener las boletas que coinciden con la consulta
    boletas = db.boletas.find(query)

    # Calcular el monto total cobrado por cada nivel de acceso
    resultados = {
        "Local": 0,
        "Plus": 0,
        "Total": 0
    }

    for boleta in boletas:
        plan_id = boleta["plan_id"]
        
        if plan_id in niveles_acceso_y_plan_ids["Local"]:
            resultados["Local"] += boleta["charges_detail"]["final_price"]
        elif plan_id in niveles_acceso_y_plan_ids["Plus"]:
            resultados["Plus"] += boleta["charges_detail"]["final_price"]
        elif plan_id in niveles_acceso_y_plan_ids["Total"]:
            resultados["Total"] += boleta["charges_detail"]["final_price"]

    # Calcular el porcentaje de dinero cobrado por cada nivel de acceso
    total_cobrado_mes_actual = sum(resultados.values())
    
    if total_cobrado_mes_actual > 0:
        porcentajes = {nivel: (total_cobrado / total_cobrado_mes_actual) * 100 for nivel, total_cobrado in resultados.items()}
    else:
        porcentajes = None

    return porcentajes

@graficos.get("/porcentaje_cobro/{negocio}/{mes_anio}", response_model=GraficosResponse, tags=["Gráficos de torta"])
def porcentaje_cobro(negocio: str, mes_anio: str):
    datos = {
        "Porcentaje de dinero cobrado por tipo de cobro": calcular_porcentaje_cobro_tipos_cobro(mes_anio, negocio),
        "Porcentaje de dinero cobrado por niveles de acceso": calcular_porcentaje_cobro_niveles_acceso(mes_anio, negocio)
    }

    if all(value == 0 for value in datos.values()):
        # Manejo de error si los datos no se encuentran
        raise HTTPException(status_code=404, detail="No se encontraron datos para el negocio y mes especificados")

    # Devolvemos los datos como una respuesta JSON
    return JSONResponse(content=datos)