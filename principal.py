import streamlit as st

import pandas as pd
import geopandas as gpd

import plotly.express as px

import folium
from folium import Marker
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap
from streamlit_folium import folium_static

import math

# Configuración de la página
st.set_page_config(layout="wide")

#
# Entradas
#

# Carga de datos
archivo_registros_presencia = st.sidebar.file_uploader('Seleccione un archivo CSV que siga el estándar DwC')

# Se continúa con el procesamiento solo si hay un archivo de datos cargado
if archivo_registros_presencia is not None:
# Carga de registros de presencia en un dataframe
 registros_presencia = pd.read_csv(archivo_registros_presencia, delimiter='\t')
# Conversión del dataframe de registros de presencia a geodataframe
 registros_presencia = gpd.GeoDataFrame(registros_presencia, 
                                    geometry=gpd.points_from_xy(registros_presencia.decimalLongitude, 
                                                                registros_presencia.decimalLatitude),
                                    crs='EPSG:4326')

# Carga de polígonos de ASP
asp = gpd.read_file("asp.geojson")

# Limpieza de datos
# Eliminación de registros con valores nulos en la columna 'species'
registros_presencia = registros_presencia[registros_presencia['species'].notna()]
# Cambio del tipo de datos del campo de fecha
registros_presencia["eventDate"] = pd.to_datetime(registros_presencia["eventDate"])

# Especificación de filtros
# Especie
lista_especies = registros_presencia.species.unique().tolist()
lista_especies.sort()
filtro_especie = st.sidebar.selectbox('Seleccione la especie', lista_especies)

#
# PROCESAMIENTO
#

# Filtrado
registros_presencia = registros_presencia[registros_presencia['species'] == filtro_especie]

# Tabla de registros de presencia
st.header('Registros de presencia')
st.dataframe(registros_presencia[['family', 'species', 'eventDate', 'locality', 'occurrenceID']].rename(columns = {'family':'Familia', 'species':'Especie', 'eventDate':'Fecha', 'locality':'Localidad', 'occurrenceID':'Origen del dato'}))

# Filtrado
registros_presencia = registros_presencia[registros_presencia['species'] == filtro_especie]

# Cálculo de la cantidad de registros en ASP
# "Join" espacial de las capas de ASP y registros de presencia
asp_contienen_registros = asp.sjoin(registros_presencia, how="left", predicate="contains")
# Conteo de registros de presencia en cada ASP
asp_registros = asp_contienen_registros.groupby("codigo").agg(cantidad_registros_presencia = ("gbifID","count"))
asp_registros = asp_registros.reset_index() # para convertir la serie a dataframe

# Tabla de registros de presencia
st.header('Registros de presencia')
st.dataframe(registros_presencia[['family', 'species', 'eventDate', 'locality', 'occurrenceID']].rename(columns = {'family':'Familia', 'species':'Especie', 'eventDate':'Fecha', 'locality':'Localidad', 'occurrenceID':'Origen del dato'}))

#Resultado parcial
st.write(asp_registros)

# Definición de columnas
col1, col2 = st.columns(2)

with col1:
# Gráficos de historial de registros de presencia por año
    st.header('Historial de registros por año')
    registros_presencia_grp_anio = pd.DataFrame(registros_presencia.groupby(registros_presencia['eventDate'].dt.year).count().eventDate)
    registros_presencia_grp_anio.columns = ['registros_presencia']

    fig = px.bar(registros_presencia_grp_anio, 
                labels={'eventDate':'Año', 'value':'Registros de presencia'})
    st.plotly_chart(fig)

with col2:    
    # Gráficos de estacionalidad de registros de presencia por mes
    st.header('Estacionalidad de registros por mes')
    registros_presencia_grp_mes = pd.DataFrame(registros_presencia.groupby(registros_presencia['eventDate'].dt.month).count().eventDate)
    registros_presencia_grp_mes.columns = ['registros_presencia']

    fig = px.area(registros_presencia_grp_mes, 
                labels={'eventDate':'Mes', 'value':'Registros de presencia'})
    st.plotly_chart(fig)      