import streamlit as st
import requests
import pandas as pd
from datetime import date, datetime
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout='wide')

###########
# FILTER #
###########
fecha1 = st.sidebar.date_input("Fecha inicial",
                               date(2021, 3, 1)
                               )
fecha2 = st.sidebar.date_input("Fecha final",
                               date(2021, 3, 21)
                               )
components.html("<center> <h1>COVID 19 en el mundo</h1></center><br><center><h3>Casos acumulados entre el "+ str(fecha1)  +" y el "+ str(fecha2) +"</h3></center>")


def get_covid_values(skip = 0, limit = 100):
    response = requests.get(url = f"http://fastapi:8585/covid/values?skip={skip}&limit={limit}")
    return response.json()

def get_covid_filter(skip = 0, limit = 100, status = 'Deaths'):
    response = requests.get(url = f"http://fastapi:8585/covid/values/filter?skip={skip}&limit={limit}&status={status}")
    return response.json()

def get_covid_filter2(date_from: date,date_to: date, status: str = 'Deaths'):
    response = requests.get(url = f"http://fastapi:8585/covid/values/test2?date_from={date_from}&date_to={date_to}&status={status}")
    return response.json()

countries = df_confirmed = pd.DataFrame.from_records(get_covid_filter2(fecha1, fecha2, 'Confirmed')).reset_index()['country_region'].to_list()
countries = set(countries)
countries = list(countries)

default_countries = ['US','Canada','India','China','South Africa','United Kingdom','El Salvador', 'Guatemala', 'Peru', 'Brazil']

country = st.sidebar.multiselect("Selecciona un país",countries, default=default_countries)


########################
### Capturando datos ###
########################

#### Muertes
df_muertes = pd.DataFrame.from_records(get_covid_filter2(fecha1, fecha2, 'Deaths')).reset_index()
df_muertes = df_muertes[df_muertes.country_region.isin(country)]

#### Confirmados
df_confirmed = pd.DataFrame.from_records(get_covid_filter2(fecha1, fecha2, 'Confirmed')).reset_index()
df_confirmed = df_confirmed[df_confirmed.country_region.isin(country)]

#### Recuperados
df_recovered = pd.DataFrame.from_records(get_covid_filter2(fecha1, fecha2, 'Recovered')).reset_index()
df_recovered = df_recovered[df_recovered.country_region.isin(country)]

###################################
### Preparando datos para mapas ###
###################################

#### Muertes
df_muertes_acum =df_muertes.groupby(by=['country_region','province_state','lat','lon']).sum().reset_index()
df_muertes_acum['Text'] =  "Pais: " + df_muertes_acum['country_region'] + \
                            "<br>Estado: " + df_muertes_acum['province_state'] + \
                           '<br>Fallecidos:' + (df_muertes_acum['value']).astype(str)

#### Confirmados
df_confirmed_acum =df_confirmed.groupby(by=['country_region','province_state','lat','lon']).sum().reset_index()
df_confirmed_acum['Text'] =  "Pais: " + df_confirmed_acum['country_region'] + \
                            "<br>Estado: " + df_confirmed_acum['province_state'] + \
                           '<br>Casos confirmados:' + (df_confirmed_acum['value']).astype(str)

#### Recuperados
df_recovered_acum =df_recovered.groupby(by=['country_region','province_state','lat','lon']).sum().reset_index()

df_recovered_acum

df_recovered_acum['Text'] =  "<b>Pais</b>: " + df_recovered_acum['country_region'] + \
                            "<br><b>Estado</b>: " + df_recovered_acum['province_state'] + \
                           '<br><b>Casos recuperados</b>:' + (df_recovered_acum['value']).astype(str)

### Mapa acumuladas del filtro
def mapa_acumulado_filtro(df, scale=100, color='#ff0000'):
    fig = go.Figure(go.Scattergeo())
    fig.add_trace(go.Scattergeo(
        lon=df['lon'],
        lat=df['lat'],
        text=df['Text'],
        marker=dict(
            size=df['value']/scale,
            color=color,
            line_width=0.5,
            sizemode='area'
        )))

    fig.update_layout(
        geo = dict(
            landcolor='#DBDDEF',
            showframe=True,
            showocean=True, oceancolor="#0E1136",
        ),
        showlegend=False,
        height=300,
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    fig.update_geos(projection_type="orthographic",
                    showcountries=True,
                    countrycolor="white")

    return  fig

map_acum_confirmed = mapa_acumulado_filtro(df_confirmed_acum, scale = 1000, color = '#FF7D33')
map_acum_recovered = mapa_acumulado_filtro(df_recovered_acum, scale = 1000, color = '#338BFF')
map_acum_deaths = mapa_acumulado_filtro(df_muertes_acum, scale = 10, color = '#FF3333')

###########
#DASHBOARD#
###########

##### MAPAS #####

map1, map2, map3 = st.columns(3)

with map1:
    st.subheader("Confirmados")
    st.plotly_chart(map_acum_confirmed, use_container_width=True)

with map2:
    st.subheader("Recuperados")
    st.plotly_chart(map_acum_recovered, use_container_width=True)

with map3:
    st.subheader("Muertes")
    st.plotly_chart(map_acum_deaths, use_container_width=True, color_bg='#0E1136')

##### DE LINEAS #####

fig2 = px.line(
    x=df_muertes.date,
    y=df_muertes.value,
    color = df_muertes.country_region,
    markers=True
    )

st.plotly_chart(fig2, use_container_width=True)