import streamlit as st
import requests
import pandas as pd
from datetime import date, datetime
import plotly.express as px
import plotly.graph_objects as go


"""
## Ejemplo de lectura de base de datos con FastApi
"""

fecha1 = st.sidebar.date_input("Fecha inicial",
                               date(2021, 3, 1)
                               )
fecha2 = st.sidebar.date_input("Fecha final",
                               date(2021, 3, 21)
                               )



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
df_muertes = pd.DataFrame.from_records(get_covid_filter2(fecha1, fecha2, 'Deaths')).reset_index()


df_muertes =df_muertes.groupby(by=['country_region']).sum().reset_index()

fig = px.scatter_geo(df_muertes, locations="country_region", size="value",)

st.plotly_chart(fig, use_container_width=True)



