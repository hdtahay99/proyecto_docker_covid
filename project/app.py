import streamlit as st
import requests
import pandas as pd
from datetime import date
import plotly.express as px


"""
## Ejemplo de lectura de base de datos con FastApi
"""

fecha1 = st.sidebar.date_input("Fecha inicial", date.today())
fecha2 = st.sidebar.date_input("Fecha final", date.today())



def get_covid_values(skip = 0, limit = 100):
    response = requests.get(url = f"http://fastapi:8585/covid/values?skip={skip}&limit={limit}")
    return response.json()

def get_covid_filter(skip = 0, limit = 100, status = 'Deaths'):
    response = requests.get(url = f"http://fastapi:8585/covid/values/filter?skip={skip}&limit={limit}&status={status}")
    return response.json()

def get_covid_filter2(date_from: date,date_to: date, status: str = 'Deaths'):
    response = requests.get(url = f"http://fastapi:8585/covid/values/test2?date_from={date_from}&date_to={date_to}&status={status}")
    return response.json()

### Capturando datos
df_muertes = pd.DataFrame.from_records(get_covid_filter2(fecha1, fecha2, 'Deaths'))


col_map_confirmed, col_map_deaths, col_map_recovered = st.columns(3)

with col_map_confirmed:
    st.header('Casos Confirmados')

    fig_mapa_death = px.scatter_geo(
        df_muertes,
        lati='lat',
        long='lon',
        size='value',
        hover_name='country_region',
        projection='natural earth'
    )

    st.plotly_chart(fig_mapa_death, use_container_width=True)


### Generando esquema de dashboard






