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
import cbsodata
import datetime


import navigation



@st.cache
def download_data(date):
    df_crimi = pd.DataFrame(cbsodata.get_data('83648NED'))
    df_veilig = pd.DataFrame(cbsodata.get_data('81877NED'))

    df_crimi = df_crimi[df_crimi['GeregistreerdeMisdrijvenPer1000Inw_3'] >= 0]
    df_crimi.drop(columns='ID', inplace=True)
    groepen = ['Misdrijven, totaal',
               '1 Vermogensmisdrijven',
               '2 Vernielingen,misdropenborde/gezag',
               '3 Gewelds- en seksuele misdrijven',
               '4 Misdrijven WvSr (overig)',
               '5 Verkeersmisdrijven',
               '6 Drugsmisdrijven',
               '7 Vuurwapenmisdrijven',
               '9 Misdrijven overige wetten']

    df_crimi = df_crimi[df_crimi['SoortMisdrijf'].isin(groepen)]

    gemeenten = pd.DataFrame(
        cbsodata.get_data('70072NED', select=['Perioden', 'RegioS', 'KoppelvariabeleRegioCode_306']))

    jaren = [*range(2010, 2021)]
    jaren = [str(jaar) for jaar in jaren]
    gemeenten = gemeenten[gemeenten['Perioden'].isin(jaren)]

    gemeenten.dropna(inplace=True)

    gemeenten = gemeenten[gemeenten['KoppelvariabeleRegioCode_306'].str.contains('GM')]

    gemeenten_2010 = gemeenten[gemeenten['Perioden'] == '2010']['RegioS']
    gemeenten_2011 = gemeenten[gemeenten['Perioden'] == '2011']['RegioS']
    gemeenten_2012 = gemeenten[gemeenten['Perioden'] == '2012']['RegioS']
    gemeenten_2013 = gemeenten[gemeenten['Perioden'] == '2013']['RegioS']
    gemeenten_2014 = gemeenten[gemeenten['Perioden'] == '2014']['RegioS']
    gemeenten_2015 = gemeenten[gemeenten['Perioden'] == '2015']['RegioS']
    gemeenten_2016 = gemeenten[gemeenten['Perioden'] == '2016']['RegioS']
    gemeenten_2017 = gemeenten[gemeenten['Perioden'] == '2017']['RegioS']
    gemeenten_2018 = gemeenten[gemeenten['Perioden'] == '2018']['RegioS']
    gemeenten_2019 = gemeenten[gemeenten['Perioden'] == '2019']['RegioS']
    gemeenten_2020 = gemeenten[gemeenten['Perioden'] == '2020']['RegioS']

    df_1 = df_crimi[(df_crimi['Perioden'] == '2010') & (df_crimi['RegioS'].isin(gemeenten_2010))]
    df_2 = df_crimi[(df_crimi['Perioden'] == '2011') & (df_crimi['RegioS'].isin(gemeenten_2011))]
    df_3 = df_crimi[(df_crimi['Perioden'] == '2012') & (df_crimi['RegioS'].isin(gemeenten_2012))]
    df_4 = df_crimi[(df_crimi['Perioden'] == '2013') & (df_crimi['RegioS'].isin(gemeenten_2013))]
    df_5 = df_crimi[(df_crimi['Perioden'] == '2014') & (df_crimi['RegioS'].isin(gemeenten_2014))]
    df_6 = df_crimi[(df_crimi['Perioden'] == '2015') & (df_crimi['RegioS'].isin(gemeenten_2015))]
    df_7 = df_crimi[(df_crimi['Perioden'] == '2016') & (df_crimi['RegioS'].isin(gemeenten_2016))]
    df_8 = df_crimi[(df_crimi['Perioden'] == '2017') & (df_crimi['RegioS'].isin(gemeenten_2017))]
    df_9 = df_crimi[(df_crimi['Perioden'] == '2018') & (df_crimi['RegioS'].isin(gemeenten_2018))]
    df_10 = df_crimi[(df_crimi['Perioden'] == '2019') & (df_crimi['RegioS'].isin(gemeenten_2019))]
    df_11 = df_crimi[(df_crimi['Perioden'] == '2020') & (df_crimi['RegioS'].isin(gemeenten_2020))]

    df_crimi2 = pd.concat([df_1, df_2, df_3, df_4, df_5, df_6, df_7, df_8, df_9, df_10, df_11])

    del (df_1, df_2, df_3, df_4, df_5, df_6, df_7, df_8, df_9, df_10, df_11)

    df_veilig = df_veilig[['RegioS', 'Perioden', 'RapportcijferVeiligheidInBuurt_18']]

    df_veilig = df_veilig[df_veilig['Perioden'] == '2019']
    df_veilig.drop(columns='Perioden', inplace=True)

    df_veilig = df_veilig[~(df_veilig['RegioS'].str.contains('RE'))]
    df_veilig = df_veilig[~(df_veilig['RegioS'].str.contains('PD'))]
    df_veilig = df_veilig[~(df_veilig['RegioS'].str.contains('PV'))]
    df_veilig = df_veilig[~(df_veilig['RegioS'].str.contains('LD'))]
    df_veilig = df_veilig[~(df_veilig['RegioS'].str.contains('BT'))]

    df_veilig['RegioS'].replace("'s-Gravenhage (gemeente)", "'s-Gravenhage", inplace=True)
    df_veilig['RegioS'].replace('Hengelo (O.)', 'Hengelo', inplace=True)
    df_veilig['RegioS'].replace('Utrecht (gemeente)', 'Utrecht', inplace=True)
    df_veilig['RegioS'].replace('Groningen (gemeente)', 'Groningen', inplace=True)

    df_veilig = df_veilig[df_veilig['RapportcijferVeiligheidInBuurt_18'] >= 6.6]

    df_veilig.index = range(0, len(df_veilig))
    df_veilig = df_veilig[~(df_veilig.index.isin([0, 53, 54, 55, 56, 57]))]

    df_crimi2['RegioS'] = df_crimi2['RegioS'].str.replace("(", "").str.replace(")", "").str.replace(" gemeente", "")
    return df_crimi2, df_veilig


# Enkele standaard opties
st.set_page_config(layout="wide") # Zorgt voor default wide op streamlit
pd.set_option('display.max_columns', None) # Print alles van de DataFrame pandas



st_autorefresh(interval=120 * 60 * 1000, key="dataframerefresh")

with st.spinner("Please wait while we are downloading everything ..."):
    df_crimi2, df_veilig = download_data(datetime.datetime.now().month)

# df_crimi2['RegioS'] = df_crimi2['RegioS'].replace("'s-Gravenhage (gemeente)", "'s-Gravenhage", inplace=True)


st.sidebar.title("Navigation")
nav = st.sidebar.radio("Go to:", ['Home', 'Cijfers criminaliteit',  "Locaties criminaliteit"])



navigation.navigation(nav, df_crimi2, df_veilig)





st.sidebar.title("About")
st.sidebar.info('This app is made by Mirko Bosch en Sjoerd Fijnje.')



link1 = '[Criminaliteit](https://opendata.cbs.nl/portal.html?_la=nl&_catalog=CBS&tableId=83648NED&_theme=407)'
link2 = '[Polygonen](https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data/wijk-en-buurtkaart-2020)'
link3 = '[Veiligheidsgevoel](https://opendata.cbs.nl/portal.html?_la=nl&_catalog=CBS&tableId=81877NED&_theme=413)'
link4 = '[Regionale kerncijfers](https://opendata.cbs.nl/portal.html?_la=nl&_catalog=CBS&tableId=70072ned&_theme=239)'
# st.markdown(link, unsafe_allow_html=True)

st.sidebar.title("Bronnen")
st.sidebar.info(link1 + ' , ' + link2 + ' , ' + link3 + ' , ' + link4)