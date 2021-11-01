import streamlit as st
import base64
import geopandas as gpd
import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import numpy as np
import requests
import plotly.figure_factory as ff
import plotly.express as px
import io
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from streamlit_folium import folium_static
import folium


def navigation(nav, df_crimi2):

    if nav == "Home":
        st.image("Afbeeldingen/Home page.gif", width=1400,)


    elif nav == "results":
        df_crimi = df_crimi2
        polygonen = gpd.read_file('Gemeente_data/gemeente_2020_v2.shp')
        polygonen[polygonen['H2O'] == 'NEE']
        polygonen = polygonen[['GM_NAAM', 'geometry']]
        polygonen.rename(columns={'GM_NAAM': 'RegioS'}, inplace=True)
        df_crimi_kaart = df_crimi[
            (df_crimi['Perioden'] == '2020') & (df_crimi['SoortMisdrijf'] == 'Misdrijven, totaal')]

        m = folium.Map(location=[52.25, 5.4],
                       tiles='Carto DB Positron',
                       zoom_start=8)

        folium.Choropleth(geo_data=polygonen,
                          name='geometry',
                          data=df_crimi_kaart,
                          columns=['RegioS', 'GeregistreerdeMisdrijvenPer1000Inw_3'],
                          key_on='feature.properties.RegioS',
                          fill_color='YlOrRd',
                          fill_opacity=0.7,
                          line_opacity=0.2,
                          legend_name='Geregistreerde misdrijven per 1000 inwoners',
                          nan_fill_color='black').add_to(m)

        st.folium_static(m)

    elif nav == "Dataframe":
        st.title("Het gedownloade dataframe")
        st.write("Dit dataframe word automatisch dagelijks geupdate. De data waarmee dit gecreerd word heeft een tragere interval. ")
        st.dataframe(df_crimi2)

