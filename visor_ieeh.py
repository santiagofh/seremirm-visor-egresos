#%%
import streamlit as st
import pandas as pd
import plotly.express as px
#%%
df_metropolitana_2024=pd.read_csv('establecimientos_pendientes.csv')
tabla_pendientes=pd.read_csv('tabla_pendientes.csv')
#%%
st.title('Estado de Reporte de Egresos Hospitalarios de la SEREMI Metropolitana de Santiago')

# Crear gráfico de torta
fig_pie = px.pie(tabla_pendientes, names='Estado', values='Número de Establecimientos', title='Proporción de Establecimientos al día vs Pendientes (2024)')
st.plotly_chart(fig_pie)

# Agregar tablas de establecimientos
st.subheader('Establecimientos Al Día')
st.dataframe(df_metropolitana_2024[df_metropolitana_2024['Estado'] == 'Al día'].drop(columns=['SEREMI de Salud']))

st.subheader('Establecimientos Pendientes')
st.dataframe(df_metropolitana_2024[df_metropolitana_2024['Estado'] == 'Pendiente'].drop(columns=['SEREMI de Salud']))

# %%
