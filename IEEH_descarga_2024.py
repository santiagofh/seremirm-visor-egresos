#%%
# Importar librerías necesarias
import pandas as pd
from bs4 import BeautifulSoup
import requests
from io import StringIO

# Definir URLs del reporte
url_ieeh_2024 = 'https://reportesdeis.minsal.cl/ieeh/2024/Reporte/EstadoRegistroEgresoSeremiResumen.aspx'

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


df_2024 = extraeTable(url_ieeh_2024)

# Ajustar DataFrames
df_2024_ajustado = seleccionar_y_ajustar_df(df_2024, 2024)

# Exportar resultados
df_2024_ajustado.to_csv('ieeh_2024.csv', index=False)# %%

# %%
