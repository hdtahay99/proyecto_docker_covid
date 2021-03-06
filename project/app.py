import streamlit as st
import requests
import pandas as pd
from datetime import date, datetime
import streamlit.components.v1 as components
import plotly.graph_objects as go

st.set_page_config(layout='wide')

###########
# FILTER #
###########
fecha1 = st.sidebar.date_input("Fecha inicial",
                               date(2021, 3, 1),
                               min_value=date(2019, 12, 1),
                               max_value=date.today()
                               )
fecha2 = st.sidebar.date_input("Fecha final",
                               date(2021, 6, 30),
                               min_value=date(2019, 12, 1),
                               max_value=date.today()
                               )

st.markdown("# COVID 19 en el mundo")
st.markdown("## Casos acumulados entre el "+ str(fecha1)  +" y el "+ str(fecha2))


def get_covid_values(skip = 0, limit = 100):
    response = requests.get(url = f"http://fastapi:8585/covid/values?skip={skip}&limit={limit}")
    return response.json()

def get_covid_filter2(date_from: date, date_to: date):
    response = requests.get(url = f"http://fastapi:8585/covid/values/test2?date_from={date_from}&date_to={date_to}")
    return response.json()

countries = df_confirmed = pd.DataFrame.from_records(get_covid_filter2(fecha1, fecha2)).reset_index()['country_region'].to_list()
countries = set(countries)
countries = list(countries)

default_countries = ['US','Canada','India','China','South Africa','United Kingdom','El Salvador', 'Guatemala', 'Peru', 'Brazil']

country = st.sidebar.multiselect("Selecciona un país",countries, default=default_countries)


########################
### Capturando datos ###
########################

full_data = pd.DataFrame.from_records(get_covid_filter2(fecha1, fecha2)).reset_index()

#### Muertes
df_muertes = full_data[full_data.country_region.isin(country)]

#### Confirmados
df_confirmed = full_data[full_data.country_region.isin(country)]

#### Recuperados
df_recovered = full_data[full_data.country_region.isin(country)]



###################################
### Preparando datos para mapas ###
###################################

#### Muertes
df_muertes_acum =df_muertes.groupby(by=['country_region','province_state','lat','lon']).sum().reset_index()
df_muertes_acum['Text'] =  "Pais: " + df_muertes_acum['country_region'] + \
                            "<br>Estado: " + df_muertes_acum['province_state'] + \
                           '<br>Fallecidos:' + (df_muertes_acum['deaths']).astype(str)

#### Confirmados
df_confirmed_acum =df_confirmed.groupby(by=['country_region','province_state','lat','lon']).sum().reset_index()
df_confirmed_acum['Text'] =  "Pais: " + df_confirmed_acum['country_region'] + \
                            "<br>Estado: " + df_confirmed_acum['province_state'] + \
                           '<br>Casos confirmados:' + (df_confirmed_acum['confirmed']).astype(str)

#### Recuperados
df_recovered_acum =df_recovered.groupby(by=['country_region','province_state','lat','lon']).sum().reset_index()



df_recovered_acum['Text'] =  "<b>Pais</b>: " + df_recovered_acum['country_region'] + \
                            "<br><b>Estado</b>: " + df_recovered_acum['province_state'] + \
                           '<br><b>Casos recuperados</b>:' + (df_recovered_acum['recovered']).astype(str)


#########################################################
### Preparando datos para metricas y grafico acumulado###
#########################################################

cumsum_confirmed = df_confirmed.groupby(['country_region', 'date']).sum().groupby(level=0).cumsum().reset_index()
cumsum_recovered = df_recovered.groupby(['country_region', 'date']).sum().groupby(level=0).cumsum().reset_index()
cumsum_death = df_muertes.groupby(['country_region', 'date']).sum().groupby(level=0).cumsum().reset_index()

### Mapa acumuladas del filtro ###

def mapa_acumulado_filtro(df, scale=100, color='#ff0000', val='confirmed'):
    fig = go.Figure(go.Scattergeo())
    fig.add_trace(go.Scattergeo(
        lon=df['lon'],
        lat=df['lat'],
        text=df['Text'],
        marker=dict(
            size=df[val]/scale,
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

map_acum_confirmed = mapa_acumulado_filtro(df_confirmed_acum, scale = 1000, color = '#FF7D33', val='confirmed')
map_acum_recovered = mapa_acumulado_filtro(df_recovered_acum, scale = 1000, color = '#338BFF', val='recovered')
map_acum_deaths = mapa_acumulado_filtro(df_muertes_acum, scale = 100, color = '#FF3333', val='deaths')


def line_cases(df,title="Nuevos", status ='Casos', val='confirmed'):
    fig = go.Figure()

    for country_region, group in df.groupby("country_region"):
        fig.add_trace(go.Scatter(
            x = group['date'],
            y = group[val],
            mode = 'lines',
            name = country_region,
            hovertemplate ="<b>%s</b><br><b>%s:</b>%%{y}"%(country_region, status)
        ))

    fig.update_layout(
        paper_bgcolor = '#F3F5F9',
        plot_bgcolor='rgba(0,0,0,0)',
        title_text=title, title_x=0.5, title_font_size=24,
        xaxis_title="Fecha",
        yaxis_title="Casos",
        xaxis_tickformat = '%d-%m-%y',
        xaxis_showgrid=False,
        yaxis_showgrid=False
    )

    return fig

## Data diaria
line_confirmed = line_cases(df_confirmed,"Nuevos" ,'Casos confirmados', 'confirmed')
line_recovered = line_cases(df_recovered, "Nuevos",'Pacientes recuperados', 'recovered')
line_deaths = line_cases(df_muertes, "Nuevos" ,"Fallecidos", 'deaths')

## Data acumulada
cumsum_line_confirmed = line_cases(cumsum_confirmed,"Acumulados" , 'Casos confirmados', 'confirmed')
cumsum_line_recovered = line_cases(cumsum_confirmed, "Acumulados" ,'Casos recuperados', 'recovered')
cumsum_line_deaths = line_cases(cumsum_death, "Acumulados",'Fallecidos', 'deaths')

#### Procesamiento de datos para tablas acumuladas
t1 = df_confirmed_acum[[ 'country_region', 'confirmed']].groupby('country_region').sum().sort_values(by='confirmed', ascending=False).reset_index()
t1.columns = ['País', 'Confirmados']
t1.Confirmados = t1.Confirmados .map('{:,}'.format)

t2 = df_recovered_acum[[ 'country_region', 'recovered']].groupby('country_region').sum().sort_values(by='recovered', ascending=False).reset_index()
t2.columns = ['País', 'Recuperados']
t2.Recuperados = t2.Recuperados .map('{:,}'.format)

t3 = df_muertes_acum[[ 'country_region', 'deaths']].groupby('country_region').sum().sort_values(by='deaths', ascending=False).reset_index()
t3.columns = ['País', 'Fallecidos']
t3.Fallecidos = t3.Fallecidos .map('{:,}'.format)

full_data_ld = pd.DataFrame.from_records(get_covid_filter2(fecha2, fecha2)).reset_index()
full_data_ld = full_data_ld[full_data_ld.country_region.isin(country)]

#### Data del último día

tn1 = full_data_ld.groupby('country_region').sum().reset_index()[['country_region', 'confirmed']].sort_values(by='confirmed', ascending=False)
tn1.columns = ['País', 'Confirmados']
tn1.Confirmados = tn1.Confirmados.map('{:,}'.format)

tn2 = full_data_ld.groupby('country_region').sum().reset_index()[['country_region', 'recovered']].sort_values(by='recovered', ascending=False)
tn2.columns = ['País', 'Recuperados']
tn2.Recuperados = tn2.Recuperados.map('{:,}'.format)

tn3 = full_data_ld.groupby('country_region').sum().reset_index()[['country_region', 'deaths']].sort_values(by='deaths', ascending=False)
tn3.columns = ['País', 'Fallecidos']
tn3.Fallecidos = tn3.Fallecidos.map('{:,}'.format)

###########
#DASHBOARD#
###########

##### METRICS #####


metrics = st.container()

m1, m2, m3, m4 = metrics.columns(4)

with m1:
    st.metric(
        label='Paises seleccionados',
        value=len(country)
    )


with m2:
    st.metric(
        label='Casos confirmados en el periodo',
        value= "{:,}".format(sum(df_confirmed_acum['confirmed']))
    )

with m3:
    st.metric(
        label='Casos confirmados en el periodo',
        value= "{:,}".format(sum(df_recovered_acum['recovered']))
    )

with m4:
    st.metric(
        label='Fallecidos en el periodo',
        value="{:,}".format(sum(df_muertes_acum['deaths']))
        #delta= sum(mtc_deaths_ld['value']),
        #delta_color= 'inverse'
    )

##### MAPAS #####

map1, map2, map3 = st.columns(3)

with map1:
    st.markdown("#### Confirmados")
    st.plotly_chart(map_acum_confirmed, use_container_width=True)

with map2:
    st.markdown("#### Recuperados")
    st.plotly_chart(map_acum_recovered, use_container_width=True)

with map3:
    st.markdown("#### Muertes")
    st.plotly_chart(map_acum_deaths, use_container_width=True)

##### DE LINEAS #####
###### Confirmados

st.markdown("#### Casos confirmados en el periodo")
conf1, conf2 = st.columns(2)
with conf1:
    st.plotly_chart(line_confirmed, use_container_width=True)

with conf2:
    st.plotly_chart(cumsum_line_confirmed, use_container_width=True)

###### Recuperados

st.markdown("#### Casos recuperados en el periodo")
rec1, rec2 = st.columns(2)
with rec1:
    st.plotly_chart(line_recovered, use_container_width=True)

with rec2:
    st.plotly_chart(cumsum_line_recovered, use_container_width=True)

###### Fallecidos

st.markdown("#### Fallecidos en el periodo")
dead1, dead2 = st.columns(2)
with dead1:
    st.plotly_chart(line_deaths, use_container_width=True)

with dead2:
    st.plotly_chart(cumsum_line_deaths, use_container_width=True)

##### Tablas

st.markdown("### Comparativo entre países seleccionados")
st.markdown("#### Ranking de países -  Acumulados entre el "+ str(fecha1)  +" y el "+ str(fecha2))

tab1, tab2, tab3 = st.columns(3)
with tab1:
    st.markdown("###### Confirmados")
    st.dataframe(t1)

with tab2:
    st.markdown("###### Recuperados")
    st.dataframe(t2)

with tab3:
    st.markdown("###### Fallecidos")
    st.dataframe(t3)


st.markdown("#### Ranking de países - Nuevos casos para la fecha " + str(fecha2))

tabn1, tabn2, tabn3 = st.columns(3)
with tabn1:
    st.markdown("###### Confirmados")
    st.dataframe(tn1)

with tabn2:
    st.markdown("###### Recuperados")
    st.dataframe(tn2)

with tabn3:
    st.markdown("###### Fallecidos")
    st.dataframe(tn3)