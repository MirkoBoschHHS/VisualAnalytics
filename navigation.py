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
from plotly.figure_factory import create_distplot

def navigation(nav, df_crimi2, df_veilig):

    if nav == "Home":
        st.image("Afbeelding/Home_page.gif", width=1400,)


    elif nav == "Locaties criminaliteit":
        m = locaties(df_crimi2)
        # col1, col2 = st.columns([1, 5])
        folium_static(m, width=1400,height=900)



    elif nav == "Dataframe":
        st.title("Het gedownloade dataframe")
        st.write("Dit dataframe word automatisch dagelijks geupdate. De data waarmee dit gecreerd word heeft een tragere interval. ")
        st.dataframe(df_crimi2)

    elif nav == "Cijfers criminaliteit":
        jaar = st.sidebar.select_slider("Kies een jaar om weer te geven:", [*range(2010,2021)])


        fig1 = Spreidingsdiagram(df_crimi2, df_veilig, jaar)
        fig2 = distplot(df_crimi2, jaar)
        fig3 = staafdiagram(df_crimi2, jaar)
        fig4 = boxplot(df_crimi2)

        col1, col2 = st.columns(2)

        col1.plotly_chart(fig1)
        col1.plotly_chart(fig3)
        col2.plotly_chart(fig2)
        col2.plotly_chart(fig4)



def locaties(df_crimi2):
    polygonen_2 = load_polygonen()


    df_crimi_kaart = df_crimi2[
        (df_crimi2['Perioden'] == '2020') & (df_crimi2['SoortMisdrijf'] == 'Misdrijven, totaal')]

    m = folium.Map(location=[52.25, 5.4],
                   tiles='Carto DB Positron',
                   zoom_start=8)

    folium.Choropleth(geo_data=polygonen_2,
                      name='geometry',
                      data=df_crimi_kaart,
                      columns=['RegioS', 'GeregistreerdeMisdrijvenPer1000Inw_3'],
                      key_on='feature.properties.RegioS',
                      fill_color='YlOrRd',
                      fill_opacity=0.7,
                      line_opacity=0.2,
                      legend_name='Geregistreerde misdrijven per 1000 inwoners',
                      nan_fill_color='black').add_to(m)

    return m

@st.cache
def load_polygonen():
    polygonen_2 = pd.read_pickle('Gemeente_data/polygonen.pkl')
    polygonen_2['geometry'] = polygonen_2['geometry'].simplify(500)
    return polygonen_2


@st.cache
def download(date):
    return pd.DataFrame(cbsodata.get_data('83648NED',
                                          select=['SoortMisdrijf', 'RegioS', 'Perioden',
                                                  'GeregistreerdeMisdrijvenRelatief_2']))

@st.cache
def staafdiagram(df_crimi, jaar):
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

    df_crimi_soort = df_crimi_soort[(df_crimi_soort['RegioS'] == 'Nederland') & (df_crimi_soort['Perioden'] == str(jaar))]
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
                 title='Staafdiagram percentages soorten misdrijven in Nederland in '+ str(jaar),
                 labels={'index': 'Soort misdrijf'})

    # fig.show()
    # st.plotly_chart(fig)
    return fig

@st.cache
def boxplot(df_crimi):
    df_crimi_box = df_crimi[['SoortMisdrijf', 'RegioS', 'Perioden', 'GeregistreerdeMisdrijvenPer1000Inw_3']]
    df_crimi_box = df_crimi_box[df_crimi_box['SoortMisdrijf'] == 'Misdrijven, totaal']
    df_crimi_box.drop(columns='SoortMisdrijf', inplace=True)
    df_crimi_box.columns = ['Gemeente', 'Jaartal', 'Geregisteerde misdrijven per 1000 inwoners']

    fig = px.box(data_frame=df_crimi_box,
                 x='Jaartal',
                 y='Geregisteerde misdrijven per 1000 inwoners',
                 hover_data=['Jaartal', 'Gemeente', 'Geregisteerde misdrijven per 1000 inwoners'],
                 title='Boxplot aantal geregisteerde misdrijven / 1000 inw. per gemeente in Nederland per jaar met mediaan',
                 color_discrete_sequence=px.colors.qualitative.Set2)

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

    # st.plotly_chart(fig)
    return fig

#@st.cache
def Spreidingsdiagram(df_crimi, df_veilig, jaar):
    df_crimi_scatter = df_crimi[df_crimi['Perioden'] == str(jaar)][
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
                     title='Spreidingsdiagram cijfer veiligheid vs. misdrijven / 1000 inw. per gemeente in ' + str(jaar),
                     range_y=(0, 140))

    def x_cor(stad):
        return df_crimi_scatter.loc[df_crimi_scatter['Gemeente'] == str(stad)].iat[0, 1]

    def y_cor(stad):
        return df_crimi_scatter.loc[df_crimi_scatter['Gemeente'] == str(stad)].iat[0, 2]


    # st.write(df_crimi_scatter)
    # st.write(df_crimi_scatter.loc[df_crimi_scatter['Gemeente'] == "Amsterdam"].iat[0,2])
    # st.write(df_crimi_scatter['Gemeente'] == "Amsterdam")
    # st.write(df_crimi_scatter.iat[0,1])

    ams = {'x': x_cor("Amsterdam"),
           'y': y_cor("Amsterdam"),
           'showarrow': True,
           'arrowhead': 5,
           'text': '<b>Amsterdam</b>',
           'font': {'size': 13, 'color': 'black'}}

    rot = {'x': x_cor("Rotterdam"),
           'y': y_cor("Rotterdam"),
           'showarrow': True,
           'arrowhead': 5,
           'text': '<b>Rotterdam</b>',
           'font': {'size': 13, 'color': 'black'}}

    utr = {'x': x_cor("Utrecht"),
           'y': y_cor("Utrecht"),
           'showarrow': True,
           'arrowhead': 5,
           'text': '<b>Utrecht</b>',
           'font': {'size': 13, 'color': 'black'}}

    dha = {'x': x_cor("'s-Gravenhage"),
           'y': y_cor("'s-Gravenhage"),
           'showarrow': True,
           'arrowhead': 5,
           'text': '<b>Den Haag</b>',
           'font': {'size': 13, 'color': 'black'}}

    results = px.get_trendline_results(fig)
    # st.write(results.iloc[0]["px_fit_results"].summary())
    results = results.iloc[0]["px_fit_results"].rsquared

    r = {'x': 7.7,
         'y': 120,
         'showarrow': False,
         'text': '<b>R² = '+ str(results) + '</b>',
         'font': {'size': 15, 'color': 'black'},
         'bgcolor': 'gold'}

    fig.update_layout({'annotations': [ams, rot, utr, dha, r]})

    # st.plotly_chart(fig)






    return fig


@st.cache
def distplot(df_crimi, jaar):
    df_crimi_dist = df_crimi[df_crimi['SoortMisdrijf'] == 'Misdrijven, totaal']
    df_crimi_dist = df_crimi_dist[df_crimi_dist['Perioden'] == str(jaar)]
    df_crimi_dist = df_crimi_dist[['RegioS', 'Perioden', 'OpgehelderdeMisdrijvenRelatief_5']]
    df_crimi_dist.columns = ['Gemeente', 'Jaartal', 'Percentage opgehelderde misdrijven']
    df_crimi_dist.drop(columns='Jaartal', inplace=True)

    fig = create_distplot([df_crimi_dist['Percentage opgehelderde misdrijven']],
                          group_labels=['% opgehelderde misdrijven'],
                          bin_size=2,
                          show_rug=False)

    fig.update_xaxes(title_text='Percentage opgehelderde misdrijven', range=[8, 42])
    fig.update_yaxes(title_text='Dichtheid')
    fig.update_layout(title_text='Distplot percentage opgehelderde misdrijven per gemeente in Nederland in '+ str(jaar))

    # fig.show()
    return fig
