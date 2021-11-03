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


def navigation(nav, df_crimi2, df_veilig):

    if nav == "Home":
        st.image("Afbeeldingen/Home page.gif", width=1400,)


    elif nav == "results":
        c1, c2, c3 = st.columns((1, 3, 1))


        # df_crimi = df_crimi2
        # polygonen = gpd.read_file('Gemeente_data/gemeente_2020_v2.shp')
        # polygonen[polygonen['H2O'] == 'NEE']
        # polygonen = polygonen[['GM_NAAM', 'geometry']]
        # polygonen.rename(columns={'GM_NAAM': 'RegioS'}, inplace=True)
        # df_crimi_kaart = df_crimi[
        #     (df_crimi['Perioden'] == '2020') & (df_crimi['SoortMisdrijf'] == 'Misdrijven, totaal')]
        #
        # m = folium.Map(location=[52.25, 5.4],
        #                tiles='Carto DB Positron',
        #                zoom_start=8)
        #
        # folium.Choropleth(geo_data=polygonen,
        #                   name='geometry',
        #                   data=df_crimi_kaart,
        #                   columns=['RegioS', 'GeregistreerdeMisdrijvenPer1000Inw_3'],
        #                   key_on='feature.properties.RegioS',
        #                   fill_color='YlOrRd',
        #                   fill_opacity=0.7,
        #                   line_opacity=0.2,
        #                   legend_name='Geregistreerde misdrijven per 1000 inwoners',
        #                   nan_fill_color='black').add_to(m)
        #
        #
        # with c2:
        #     folium_static(m)

    elif nav == "Tweede":
        tweede(df_crimi2, df_veilig)


    elif nav == "Dataframe":
        st.title("Het gedownloade dataframe")
        st.write("Dit dataframe word automatisch dagelijks geupdate. De data waarmee dit gecreerd word heeft een tragere interval. ")
        st.dataframe(df_crimi2)






@st.cache
def tweede(df_crimi, df_veilig):
    df_crimi_scatter = df_crimi[df_crimi['Perioden'] == '2019'][
        ['SoortMisdrijf', 'RegioS', 'GeregistreerdeMisdrijvenPer1000Inw_3']]
    df_crimi_scatter = df_crimi_scatter[df_crimi_scatter['SoortMisdrijf'] == 'Misdrijven, totaal']
    df_crimi_scatter.drop(columns='SoortMisdrijf', inplace=True)

    df_crimi_scatter['RegioS'].replace("'s-Gravenhage (gemeente)", "'s-Gravenhage", inplace=True)
    df_crimi_scatter['RegioS'].replace('Groningen (gemeente)', 'Groningen', inplace=True)
    df_crimi_scatter['RegioS'].replace('Hengelo (O.)', 'Hengelo', inplace=True)
    df_crimi_scatter['RegioS'].replace('Utrecht (gemeente)', 'Utrecht', inplace=True)

    df_crimi_scatter = df_veilig.merge(df_crimi_scatter, on='RegioS')

    df_crimi_scatter.columns = ['Gemeente', 'Cijfer veiligheid in de buurt',
                                'Geregisteerde misdrijven per 1000 inwoners']

    fig = px.scatter(data_frame=df_crimi_scatter,
                     x='Cijfer veiligheid in de buurt',
                     y='Geregisteerde misdrijven per 1000 inwoners',
                     hover_data=df_crimi_scatter.columns,
                     trendline='ols',
                     trendline_color_override='black',
                     title='Spreidingsdiagram cijfer veiligheid enquête vs. aantal misdrijven per 1000 inwoners per gemeente in 2019',
                     range_y=(0, 110))

    ams = {'x': 7,
           'y': 96.3,
           'showarrow': True,
           'arrowhead': 5,
           'text': '<b>Amsterdam</b>',
           'font': {'size': 13, 'color': 'black'}}

    rot = {'x': 6.7,
           'y': 82.4,
           'showarrow': True,
           'arrowhead': 5,
           'text': '<b>Rotterdam</b>',
           'font': {'size': 13, 'color': 'black'}}

    utr = {'x': 7.091,
           'y': 78.6,
           'showarrow': True,
           'arrowhead': 5,
           'text': '<b>Utrecht</b>',
           'font': {'size': 13, 'color': 'black'}}

    dha = {'x': 7,
           'y': 70.8,
           'showarrow': True,
           'arrowhead': 5,
           'text': '<b>Den Haag</b>',
           'font': {'size': 13, 'color': 'black'}}

    r = {'x': 7.7,
         'y': 90,
         'showarrow': False,
         'text': '<b>r = -0.69</b>',
         'font': {'size': 15, 'color': 'black'},
         'bgcolor': 'gold'}

    fig.update_layout({'annotations': [ams, rot, utr, dha, r]})

    fig.show()