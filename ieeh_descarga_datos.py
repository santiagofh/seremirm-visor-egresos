#%%
# Importar librerías necesarias
import pandas as pd
from bs4 import BeautifulSoup
import requests
from io import StringIO
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
import json

# Definir URLs del reporte
url_ieeh_2023 = 'https://reportesdeis.minsal.cl/ieeh/2023/Reporte/EstadoRegistroEgresoSeremiResumen.aspx'
url_ieeh_2024 = 'https://reportesdeis.minsal.cl/ieeh/2024/Reporte/EstadoRegistroEgresoSeremiResumen.aspx'
ieeh_reporte_0 = r"C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\GIE\IEEH-REM20\IEEH - Reporte 0\ieeh_reporte_0.json"
# Definir función para extraer la tabla de la URL
def extraeTable(url):
    response = requests.get(url, timeout=360)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find(id='ctl00_CPH_Cuerpo_GridView1')
        string_io_table = StringIO(str(table))
        df = pd.read_html(string_io_table)[0]
        return df
    else:
        st.error(f'Error al realizar la solicitud: {response.status_code}')
        return None

# Definir función para seleccionar la RM y ajustar el DataFrame
def seleccionar_y_ajustar_df(df, year):
    new_header = df.iloc[0]
    df = df[1:]

    df.columns = new_header
    df['SEREMI de Salud'] = df['SEREMI de Salud'].fillna(method='ffill')
    df_metropolitana = df[df['SEREMI de Salud'] == "SEREMI Metropolitana de Santiago"]
    df_metropolitana = df_metropolitana[1:]

    # Diccionario para renombrar columnas de meses
    dict_mont_num = {
        'Ene': 1,
        'Feb': 2,
        'Mar': 3,
        'Abr': 4,
        'May': 5,
        'Jun': 6,
        'Jul': 7,
        'Ago': 8,
        'Sep': 9,
        'Oct': 10,
        'Nov': 11,
        'Dic': 12,
    }

    df_metropolitana.rename(columns=dict_mont_num, inplace=True)
    df_metropolitana['Año'] = year  # Agregar columna de año
    return df_metropolitana

def calculate_business_days(date, business_days):
    current_date = date
    count = 0
    while count < business_days:
        if current_date.weekday() < 5:  # Monday to Friday are considered business days
            count += 1
        current_date += timedelta(days=1)
    return current_date

def es_despues_de_los_primeros_10_dias_habiles():
    now = datetime.now()
    first_day_of_month = now.replace(day=1)
    first_10_business_days_end = calculate_business_days(first_day_of_month, 10)

    # Verifica si la fecha actual está después del final de los primeros 10 días hábiles
    if now >= first_10_business_days_end:
        return True  # Estamos después de los primeros 10 días hábiles
    else:
        return False  # Estamos dentro de los primeros 10 días hábiles
def pendientes(df,control_mes):
    now = datetime.now()
    current_month = now.month
    if control_mes == True:
        n=1
    else:
        n=2
    df['Estado'] = 'Al día'
    months_to_check = list(range(1, current_month-n))
    condition = pd.concat([df[month].isna() for month in months_to_check], axis=1).any(axis=1)
    establecimientos_pendientes = df[condition]
    df.loc[establecimientos_pendientes.index, 'Estado'] = 'Pendiente'
    estado_counts = df['Estado'].value_counts().reset_index()
    estado_counts.columns = ['Estado', 'Número de Establecimientos']
    return df, estado_counts    
    
def rellenar_con_reporte_0(df, reporte_0):
    for codigo, data in reporte_0.items():
        for mes, valor in data.items():
            if mes.isdigit():
                mes = int(mes)
                print(mes)
                if mes in df.columns:
                    df.loc[df['Codigo Establecimiento'] == (codigo), mes] = valor
                    print((codigo))
                    print(valor)
                else:
                    df[mes] = 0
                    df.loc[df['Codigo Establecimiento'] == (codigo), mes] = valor
    return df    
#%%
with open(ieeh_reporte_0, 'r', encoding='utf-8') as f:
    reporte_0 = json.load(f)

df_2023=extraeTable(url_ieeh_2023)
df_2024=extraeTable(url_ieeh_2024)
#%%
df_2024_ajustado=seleccionar_y_ajustar_df(df_2024, 2024)
df_2024_ajustado_reporte0=rellenar_con_reporte_0(df_2024_ajustado,reporte_0)
#%%
control_mes=es_despues_de_los_primeros_10_dias_habiles()
df_2024_pendientes, tabla_pendientes=pendientes(df_2024_ajustado_reporte0,control_mes)

#%%

df_2024_pendientes.to_csv('establecimientos_pendientes.csv')

tabla_pendientes.to_csv('tabla_pendientes.csv')
# %%
