#%%
# Importar librerías necesarias
import pandas as pd
from bs4 import BeautifulSoup
import requests
from io import StringIO
from datetime import datetime, timedelta
import json

# Definir URLs del reporte
url_ieeh_2023 = 'https://reportesdeis.minsal.cl/ieeh/2023/Reporte/EstadoRegistroEgresoSeremiResumen.aspx'
url_ieeh_2024 = 'https://reportesdeis.minsal.cl/ieeh/2024/Reporte/EstadoRegistroEgresoSeremiResumen.aspx'

ieeh_reporte_0 = r"C:\\Users\\fariass\\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\\Escritorio\\GIE\\IEEH-REM20\\IEEH - Reporte 0\\ieeh_reporte_0.json"

#%%
# Funciones auxiliares

def extraeTable(url):
    """
    Extrae una tabla de una URL dada.
    """
    response = requests.get(url, timeout=360)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find(id='ctl00_CPH_Cuerpo_GridView1')
        string_io_table = StringIO(str(table))
        df = pd.read_html(string_io_table)[0]
        return df
    else:
        raise Exception(f'Error al realizar la solicitud: {response.status_code}')

def seleccionar_y_ajustar_df(df, year):
    """
    Ajusta el DataFrame extrayendo los datos de la SEREMI Metropolitana y agregando columnas necesarias.
    """
    new_header = df.iloc[0]
    df = df[1:]
    df.columns = new_header
    df['SEREMI de Salud'] = df['SEREMI de Salud'].fillna(method='ffill')
    df_metropolitana = df[df['SEREMI de Salud'] == "SEREMI Metropolitana de Santiago"]
    df_metropolitana = df_metropolitana[1:]

    dict_mont_num = {
        'Ene': 1, 'Feb': 2, 'Mar': 3, 'Abr': 4, 'May': 5,
        'Jun': 6, 'Jul': 7, 'Ago': 8, 'Sep': 9, 'Oct': 10,
        'Nov': 11, 'Dic': 12
    }

    df_metropolitana.rename(columns=dict_mont_num, inplace=True)
    df_metropolitana['Año'] = year

    # Convertir columnas de meses en formato YYYY-MM
    columnas_meses = [col for col in df_metropolitana.columns if isinstance(col, int)]
    for mes in columnas_meses:
        nuevo_nombre = f"{year}-{str(mes).zfill(2)}"
        df_metropolitana.rename(columns={mes: nuevo_nombre}, inplace=True)

    # Procesar columnas
    for col in df_metropolitana.columns:
        if col.startswith(f"{year}-"):
            df_metropolitana[col] = pd.to_numeric(df_metropolitana[col].str.replace('.', '', regex=False), errors='coerce')

    df_metropolitana['Total'] = pd.to_numeric(df_metropolitana['Total'].str.replace('.', '', regex=False), errors='coerce')
    return df_metropolitana

def calculate_business_days(date, business_days):
    """
    Calcula la fecha sumando días hábiles a una fecha inicial.
    """
    current_date = date
    count = 0
    while count < business_days:
        if current_date.weekday() < 5:  # Lunes a Viernes son días hábiles
            count += 1
        current_date += timedelta(days=1)
    return current_date

def diez_dias_habiles_mes_subsiguiente():
    """
    Calcula si hoy es después de los primeros 10 días hábiles del mes subsiguiente.
    """
    now = datetime.now()
    if now.month == 12:
        first_day_of_subsequent_month = datetime(year=now.year + 1, month=1, day=1)
    else:
        first_day_of_subsequent_month = datetime(year=now.year, month=now.month + 1, day=1)

    return now >= calculate_business_days(first_day_of_subsequent_month, 10)

def pendientes(df, control_mes):
    """
    Marca los establecimientos como "Pendiente" o "Al día" según los meses con datos ausentes y rellena los pendientes.
    """
    now = datetime.now()
    current_month = now.month
    month_threshold = current_month - (1 if control_mes else 2)

    df['Estado'] = 'Al día'
    months_to_check = [col for col in df.columns if col.startswith(f"{now.year}-") and int(col.split('-')[1]) <= month_threshold]
    
    # Rellenar "Pendiente" en las columnas de meses pendientes
    for month in months_to_check:
        df[month] = df[month].fillna('Pendiente')

    # Determinar los establecimientos pendientes
    condition = pd.concat([df[month] == 'Pendiente' for month in months_to_check], axis=1).any(axis=1)
    establecimientos_pendientes = df[condition]

    df.loc[establecimientos_pendientes.index, 'Estado'] = 'Pendiente'
    estado_counts = df['Estado'].value_counts().reset_index()
    estado_counts.columns = ['Estado', 'Número de Establecimientos']

    return df, estado_counts

def rellenar_con_reporte_0(df, reporte_0):
    """
    Rellena datos faltantes en el DataFrame usando un reporte inicial.
    """
    for codigo, data in reporte_0.items():
        for mes, valor in data.items():
            if mes.isdigit():
                mes = int(mes)
                mes_col = f"{datetime.now().year}-{str(mes).zfill(2)}"
                if mes_col in df.columns:
                    df.loc[df['Codigo Establecimiento'] == codigo, mes_col] = valor
    return df

#%%
# Cargar y procesar datos
with open(ieeh_reporte_0, 'r', encoding='utf-8') as f:
    reporte_0 = json.load(f)

df_2023 = extraeTable(url_ieeh_2023)
df_2024 = extraeTable(url_ieeh_2024)

# Ajustar DataFrames
df_2024_ajustado = seleccionar_y_ajustar_df(df_2024, 2024)
df_2024_ajustado_reporte0 = rellenar_con_reporte_0(df_2024_ajustado, reporte_0)

# Determinar si estamos después de los primeros 10 días hábiles del mes subsiguiente
control_mes = diez_dias_habiles_mes_subsiguiente()

# Calcular pendientes
df_2024_pendientes, tabla_pendientes = pendientes(df_2024_ajustado_reporte0, control_mes)

#%%
# Exportar resultados
tabla_pendientes.to_csv('tabla_pendientes.csv', index=False)
df_2024_pendientes.to_csv('establecimientos_pendientes.csv', index=False)
df_2024_pendientes.to_excel('establecimientos_pendientes.xlsx', index=False)
# %%
