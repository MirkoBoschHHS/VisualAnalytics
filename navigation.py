import streamlit as st
import base64
# import geopandas as gpd
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

def navigation(nav, df_crimi2, df_veilig):

    if nav == "Home":
        st.image("Afbeelding/Home_page.gif", width=1400,)


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

    elif nav == "Derde":
        derde(df_crimi2, df_veilig)

    elif nav == "Dataframe":
        st.title("Het gedownloade dataframe")
        st.write("Dit dataframe word automatisch dagelijks geupdate. De data waarmee dit gecreerd word heeft een tragere interval. ")
        st.dataframe(df_crimi2)

    elif nav == "Statestieken":
        statestiek(df_crimi2)

@st.cache
def download(date):
    return pd.DataFrame(cbsodata.get_data('83648NED', \
                                          select=['SoortMisdrijf', 'RegioS', 'Perioden',
                                                  'GeregistreerdeMisdrijvenRelatief_2']))


def statestiek(df_crimi):
    # df_crimi_soort = pd.DataFrame(cbsodata.get_data('83648NED', \
    #                                                 select=['SoortMisdrijf', 'RegioS', 'Perioden',
    #                                                         'GeregistreerdeMisdrijvenRelatief_2']))

    df_crimi_soort = download(datetime.datetime.now().date())


    groepen = ['Misdrijven, totaal',
               '1 Vermogensmisdrijven',
               '2 Vernielingen,misdropenborde/gezag',
               '3 Gewelds- en seksuele misdrijven',
               '4 Misdrijven WvSr (overig)',
               '5 Verkeersmisdrijven',
               '6 Drugsmisdrijven',
               '7 Vuurwapenmisdrijven',
               '9 Misdrijven overige wetten']

    df_crimi_soort = df_crimi_soort[(df_crimi_soort['RegioS'] == 'Nederland') & (df_crimi_soort['Perioden'] == '2020')]
    df_crimi_soort = df_crimi_soort[df_crimi_soort['SoortMisdrijf'].isin(groepen)]
    df_crimi_soort.drop(columns=['RegioS', 'Perioden'], inplace=True)

    df_crimi_soort = df_crimi_soort[df_crimi_soort['GeregistreerdeMisdrijvenRelatief_2'] >= 1]
    df_crimi_soort = df_crimi_soort[df_crimi_soort['GeregistreerdeMisdrijvenRelatief_2'] != 100]
    df_crimi_soort.columns = ['Soort misdrijf', 'Percentage geregistreerde misdrijven']

    df_crimi_soort.set_index('Soort misdrijf', inplace=True)
    df_crimi_soort = df_crimi_soort.sort_values('Percentage geregistreerde misdrijven', ascending=False)
    df_crimi_soort['Soort misdrijf'] = ['1', '5', '2', '3', '4', '6', '7']

    fig = px.bar(data_frame=df_crimi_soort,
                 x=df_crimi_soort.index,
                 y='Percentage geregistreerde misdrijven',
                 color='Soort misdrijf',
                 color_discrete_sequence=px.colors.qualitative.G10,
                 title='Staafdiagram percentages soorten misdrijven in Nederland in 2020',
                 labels={'index': 'Soort misdrijf'})

    # fig.show()
    st.plotly_chart(fig)

    df_crimi_box = df_crimi[['SoortMisdrijf', 'RegioS', 'Perioden', 'GeregistreerdeMisdrijvenPer1000Inw_3']]
    df_crimi_box = df_crimi_box[df_crimi_box['SoortMisdrijf'] == 'Misdrijven, totaal']
    df_crimi_box.drop(columns='SoortMisdrijf', inplace=True)
    df_crimi_box.columns = ['Gemeente', 'Jaartal', 'Geregisteerde misdrijven per 1000 inwoners']

    fig = px.box(data_frame=df_crimi_box,
                 x='Jaartal',
                 y='Geregisteerde misdrijven per 1000 inwoners',
                 hover_data=['Jaartal', 'Gemeente', 'Geregisteerde misdrijven per 1000 inwoners'],
                 title='Boxplot aantal geregisteerde misdrijven / 1000 inw. per gemeente in Nederland per jaar met mediaan')

    _10 = {'x': 0,
           'y': 53.5,
           'showarrow': False,
           'text': '<b>50.5</b>',
           'font': {'size': 13, 'color': 'black'}}
    _11 = {'x': 1,
           'y': 52.8,
           'showarrow': False,
           'text': '<b>49.8</b>',
           'font': {'size': 13, 'color': 'black'}}
    _12 = {'x': 2,
           'y': 50.5,
           'showarrow': False,
           'text': '<b>47.5</b>',
           'font': {'size': 13, 'color': 'black'}}
    _13 = {'x': 3,
           'y': 48.5,
           'showarrow': False,
           'text': '<b>45.5</b>',
           'font': {'size': 13, 'color': 'black'}}
    _14 = {'x': 4,
           'y': 44.3,
           'showarrow': False,
           'text': '<b>41.3</b>',
           'font': {'size': 13, 'color': 'black'}}
    _15 = {'x': 5,
           'y': 42.8,
           'showarrow': False,
           'text': '<b>39.8</b>',
           'font': {'size': 13, 'color': 'black'}}
    _16 = {'x': 6,
           'y': 40.2,
           'showarrow': False,
           'text': '<b>37.2</b>',
           'font': {'size': 13, 'color': 'black'}}
    _17 = {'x': 7,
           'y': 35.7,
           'showarrow': False,
           'text': '<b>32.7</b>',
           'font': {'size': 13, 'color': 'black'}}
    _18 = {'x': 8,
           'y': 33.9,
           'showarrow': False,
           'text': '<b>30.9</b>',
           'font': {'size': 13, 'color': 'black'}}
    _19 = {'x': 9,
           'y': 36.4,
           'showarrow': False,
           'text': '<b>33.4</b>',
           'font': {'size': 13, 'color': 'black'}}
    _20 = {'x': 10,
           'y': 37.1,
           'showarrow': False,
           'text': '<b>34.1</b>',
           'font': {'size': 13, 'color': 'black'}}

    fig.update_layout({'annotations': [_10, _11, _12, _13, _14, _15, _16, _17, _18, _19, _20]})

    st.plotly_chart(fig)


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


def derde(df_crimi, df_veilig):
    df_crimi_scatter = df_crimi[df_crimi['Perioden'] == '2019'][
        ['SoortMisdrijf', 'RegioS', 'GeregistreerdeMisdrijvenPer1000Inw_3']]
    df_crimi_scatter = df_crimi_scatter[df_crimi_scatter['SoortMisdrijf'] == 'Misdrijven, totaal']
    df_crimi_scatter.drop(columns='SoortMisdrijf', inplace=True)

    df_crimi_scatter['RegioS'].replace("'s-Gravenhage (gemeente)", "'s-Gravenhage", inplace=True)
    df_crimi_scatter['RegioS'].replace('Groningen (gemeente)', 'Groningen', inplace=True)
    df_crimi_scatter['RegioS'].replace('Hengelo (O.)', 'Hengelo', inplace=True)
    df_crimi_scatter['RegioS'].replace('Utrecht (gemeente)', 'Utrecht', inplace=True)

    df_crimi_scatter = df_veilig.merge(df_crimi_scatter, on='RegioS')

    df_crimi_scatter.columns=['Gemeente', 'Cijfer veiligheid in de buurt', 'Geregisteerde misdrijven per 1000 inwoners']

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
