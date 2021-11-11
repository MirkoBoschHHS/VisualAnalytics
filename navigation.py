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
from statsmodels.formula.api import ols

def navigation(nav, df_crimi2, df_veilig):

    if nav == "Home":
        st.image("Afbeelding/Home_page2.gif", width=1400,)


    elif nav == "Locaties criminaliteit":
        m = locaties(df_crimi2)
        # col1, col2 = st.columns([1, 5])
        folium_static(m, width=1400,height=900)



    elif nav == "Dataframe":
        st.title("Het gedownloade dataframe")
        st.write("Dit dataframe word automatisch dagelijks geupdate. De data waarmee dit gecreerd word heeft een tragere interval. ")
        st.dataframe(df_crimi2)
        # st.dataframe(load_polygonen())

    elif nav == "Cijfers criminaliteit":
        jaar = st.sidebar.select_slider("Kies een jaar om weer te geven:", [*range(2010,2021)])

        # st.write(list(df_crimi2['RegioS'].unique()))
        gemeente = st.sidebar.multiselect("Kies enkele gemeentes om te highlighten:", list(df_crimi2['RegioS'].unique()), 'Amsterdam')


        fig1 = Spreidingsdiagram(df_crimi2, df_veilig, jaar, gemeente)
        fig2 = distplot(df_crimi2, jaar)
        fig3 = staafdiagram(df_crimi2, jaar)
        fig4 = boxplot(df_crimi2, gemeente, jaar)
        fig5 = regessie(df_crimi2, gemeente, jaar)

        col1, col2 = st.columns(2)
        col1.plotly_chart(fig1)
        col2.plotly_chart(fig5)

        col1, col2, col3 = st.columns(3)
        col1.plotly_chart(fig3)
        col2.plotly_chart(fig2)
        col3.plotly_chart(fig4)


        st.markdown("""
        <style>
        .big-font {
            font-size:13px !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<p class="big-font">*Alleen gemeenten die meegedaan hebben/voldoende enquêtes hebben ingevuld.</p>', unsafe_allow_html=True)







def locaties(df_crimi2):
    polygonen_2 = load_polygonen()

    df_crimi2 = df_crimi2[(df_crimi2['Perioden'] == '2020') & (df_crimi2['SoortMisdrijf'] == 'Misdrijven, totaal')]
    polygonen_2 = polygonen_2.merge(df_crimi2[['RegioS', 'GeregistreerdeMisdrijvenPer1000Inw_3']], on='RegioS', how='left')

    df_crimi_kaart = df_crimi2[
        (df_crimi2['Perioden'] == '2020') & (df_crimi2['SoortMisdrijf'] == 'Misdrijven, totaal')]



    m = folium.Map(location=[52.25, 5.5],
                   tiles='Carto DB Positron',
                   zoom_start=8,
                   min_zoom=7,
                   max_zoom=10)

    bins = list(df_crimi2['GeregistreerdeMisdrijvenPer1000Inw_3'].quantile([0, 1 / 6, 2 / 6, 3 / 6, 4 / 6, 5 / 6, 1]))

    folium.Choropleth(geo_data=polygonen_2,
                      name='geometry',
                      data=df_crimi2,
                      columns=['RegioS', 'GeregistreerdeMisdrijvenPer1000Inw_3'],
                      key_on='feature.properties.RegioS',
                      fill_color='YlOrRd',
                      fill_opacity=0.6,
                      line_opacity=0.2,
                      legend_name='Geregistreerde misdrijven per 1000 inwoners',
                      nan_fill_opacity=0.8,
                      bins=bins,
                      nan_fill_color='dimgray',
                      highlight=True).add_to(m).geojson.add_child(
        folium.features.GeoJsonTooltip(fields=['RegioS', 'GeregistreerdeMisdrijvenPer1000Inw_3'], labels=False))

    # plugins.Fullscreen().add_to(m)



    return m

@st.cache
def load_polygonen():
    polygonen_2 = pd.read_pickle('Gemeente_data/polygonen.pkl')
    polygonen_2['geometry'] = polygonen_2['geometry'].simplify(500)
    return polygonen_2


@st.cache
def download(date):
    df_crimi_soort = pd.DataFrame(cbsodata.get_data('83648NED',
                                          select=['SoortMisdrijf', 'RegioS', 'Perioden',
                                                  'GeregistreerdeMisdrijvenRelatief_2']))
    df_crimi_soort['SoortMisdrijf'] = df_crimi_soort['SoortMisdrijf'].str.replace('\d+', '')
    return df_crimi_soort

@st.cache
def staafdiagram(df_crimi, jaar):
    df_crimi_soort = download(datetime.datetime.now().month)

    

    groepen = ['Misdrijven, totaal',
               ' Vermogensmisdrijven',
               ' Vernielingen,misdropenborde/gezag',
               ' Gewelds- en seksuele misdrijven',
               ' Misdrijven WvSr (overig)',
               ' Verkeersmisdrijven',
               ' Drugsmisdrijven',
               ' Vuurwapenmisdrijven',
               ' Misdrijven overige wetten']

   
    # st.write(groepen)

    df_crimi_soort = df_crimi_soort[(df_crimi_soort['RegioS'] == 'Nederland') & (df_crimi_soort['Perioden'] == str(jaar))]
    df_crimi_soort = df_crimi_soort[df_crimi_soort['SoortMisdrijf'].isin(groepen)]
    df_crimi_soort.drop(columns=['RegioS', 'Perioden'], inplace=True)

    df_crimi_soort = df_crimi_soort[df_crimi_soort['GeregistreerdeMisdrijvenRelatief_2'] > 0]
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
                 title='Percentages soorten misdrijven in '+ str(jaar),
                 labels={'index': 'Soort Misdrijf'})
    fig.update_layout(showlegend=False, width=500, xaxis_tickangle=50)
    # fig.update_traces(width=0.4)

    # fig.show()
    # st.plotly_chart(fig)
    return fig

@st.cache
def boxplot(df_crimi, gemeente, jaar):
    df_crimi_box = df_crimi[['SoortMisdrijf', 'RegioS', 'Perioden', 'GeregistreerdeMisdrijvenPer1000Inw_3']]
    df_crimi_box = df_crimi_box[df_crimi_box['SoortMisdrijf'] == 'Misdrijven, totaal']
    df_crimi_box.drop(columns='SoortMisdrijf', inplace=True)
    df_crimi_box.columns = ['Gemeente', 'Jaartal', 'Geregisteerde misdrijven per 1000 inwoners']

    fig = px.box(data_frame=df_crimi_box,
                 x='Jaartal',
                 y='Geregisteerde misdrijven per 1000 inwoners',
                 hover_data=['Jaartal', 'Gemeente', 'Geregisteerde misdrijven per 1000 inwoners'],
                 title='Aantal misdrijven / 1000 inw. per gemeente per jaar',
                 color_discrete_sequence=px.colors.qualitative.Set2)

    fig.update_layout(width=550)


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

    # st.write(df_crimi_box)


    def x_cor(stad, jaar):
        return jaar-2010 #df_crimi_box.loc[df_crimi_box['Gemeente'] == str(stad)].iat[(jaar-2010), 1]

    def y_cor(stad, jaar):
        return df_crimi_box.loc[df_crimi_box['Gemeente'] == str(stad)].iat[(jaar-2010), 2]

    # st.write(y_cor("Aalsmeer", jaar))


    def gemeente_toevoegen(gemeente, jaar):
        a = {'x': x_cor(gemeente, jaar),
               'y': y_cor(gemeente, jaar),
               'showarrow': True,
               # 'arrowhead': 5,
               'text': '<b>' + gemeente + '</b>',
               'font': {'size': 10, 'color': 'black'}}
        return a

    annotations = []
    for g in gemeente:
        try:
            annotations.append(gemeente_toevoegen(g, jaar))
        except:
            pass


    for i in [_10, _11, _12, _13, _14, _15, _16, _17, _18, _19, _20]:
        annotations.append(i)

    # annotations.append([_10, _11, _12, _13, _14, _15, _16, _17, _18, _19, _20])

    fig.update_layout({'annotations': annotations})

    # st.plotly_chart(fig)
    return fig

@st.cache
def Spreidingsdiagram(df_crimi, df_veilig, jaar, gemeente):
    df_crimi_scatter = df_crimi[df_crimi['Perioden'] == str(jaar)][
        ['SoortMisdrijf', 'RegioS', 'GeregistreerdeMisdrijvenPer1000Inw_3']]
    df_crimi_scatter = df_crimi_scatter[df_crimi_scatter['SoortMisdrijf'] == 'Misdrijven, totaal']
    df_crimi_scatter.drop(columns='SoortMisdrijf', inplace=True)

    # df_crimi_scatter['RegioS'].replace("'s-Gravenhage (gemeente)", "'s-Gravenhage", inplace=True)
    # df_crimi_scatter['RegioS'].replace('Groningen (gemeente)', 'Groningen', inplace=True)
    # df_crimi_scatter['RegioS'].replace('Hengelo (O.)', 'Hengelo', inplace=True)
    # df_crimi_scatter['RegioS'].replace('Utrecht (gemeente)', 'Utrecht', inplace=True)

    df_crimi_scatter = df_veilig.merge(df_crimi_scatter, on='RegioS')

    df_crimi_scatter.columns = ['Gemeente', 'Cijfer enquête veiligheid in de buurt',
                                'Geregisteerde misdrijven per 1000 inwoners']

    fig = px.scatter(data_frame=df_crimi_scatter,
                     x='Cijfer enquête veiligheid in de buurt',
                     y='Geregisteerde misdrijven per 1000 inwoners',
                     hover_data=df_crimi_scatter.columns,
                     trendline='ols',
                     trendline_color_override='black',
                     title='Cijfer veiligheid vs. misdrijven / 1000 inw. per gemeente* in ' + str(jaar),
                     range_y=(0, 140))

    fig.update_layout(width=700)



    def x_cor(stad):
        return df_crimi_scatter.loc[df_crimi_scatter['Gemeente'] == str(stad)].iat[0, 1]

    def y_cor(stad):
        return df_crimi_scatter.loc[df_crimi_scatter['Gemeente'] == str(stad)].iat[0, 2]



    def gemeente_toevoegen(gemeente):
        a = {'x': x_cor(gemeente),
               'y': y_cor(gemeente),
               'showarrow': True,
               'arrowhead': 5,
               'text': '<b>' + gemeente + '</b>',
               'font': {'size': 13, 'color': 'black'}}
        return a

    annotations = []
    for g in gemeente:
        try:
            annotations.append(gemeente_toevoegen(g))
        except:
            pass
    # st.write(annotations)

    # ams = {'x': x_cor("Amsterdam"),
    #        'y': y_cor("Amsterdam"),
    #        'showarrow': True,
    #        'arrowhead': 5,
    #        'text': '<b>Amsterdam</b>',
    #        'font': {'size': 13, 'color': 'black'}}
    #
    # rot = {'x': x_cor("Rotterdam"),
    #        'y': y_cor("Rotterdam"),
    #        'showarrow': True,
    #        'arrowhead': 5,
    #        'text': '<b>Rotterdam</b>',
    #        'font': {'size': 13, 'color': 'black'}}
    #
    # utr = {'x': x_cor("Utrecht"),
    #        'y': y_cor("Utrecht"),
    #        'showarrow': True,
    #        'arrowhead': 5,
    #        'text': '<b>Utrecht</b>',
    #        'font': {'size': 13, 'color': 'black'}}
    #
    # dha = {'x': x_cor("'s-Gravenhage"),
    #        'y': y_cor("'s-Gravenhage"),
    #        'showarrow': True,
    #        'arrowhead': 5,
    #        'text': '<b>Den Haag</b>',
    #        'font': {'size': 13, 'color': 'black'}}

    results = px.get_trendline_results(fig)
    # st.write(results.iloc[0]["px_fit_results"].summary())
    results = round(results.iloc[0]["px_fit_results"].rsquared, 2)

    r = {'x': 7.7,
         'y': 120,
         'showarrow': False,
         'text': '<b>R² = '+ str(results) + '</b>',
         'font': {'size': 15, 'color': 'black'},
         'bgcolor': 'gold'}

    annotations.append(r)

    fig.update_layout({'annotations': annotations})

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

    fig.update_xaxes(title_text='Percentage misdrijven dat is opgehelderd', range=[8, 42])
    fig.update_yaxes(title_text='Dichtheid')
    fig.update_layout(title_text='Percentage opgehelderde misdrijven per gemeente in ' + str(jaar))

    # fig.show()
    return fig


@st.cache
def download_reg(date):
    bevolking = pd.DataFrame(cbsodata.get_data('70072NED', select=['RegioS', 'Perioden',
                                                       'KoppelvariabeleRegioCode_306', 'Bevolkingsdichtheid_57']))
    bevolking.dropna(subset=['KoppelvariabeleRegioCode_306'], inplace=True)
    bevolking = bevolking[bevolking['KoppelvariabeleRegioCode_306'].str.contains('GM')]
    bevolking = bevolking[bevolking['Perioden'].isin(['2010', '2011', '2012', '2013', '2014', \
                                                      '2015', '2016', '2017', '2018', '2019', '2020'])]
    bevolking.drop(columns='KoppelvariabeleRegioCode_306', inplace=True)

    return bevolking

# @st.cache
def regessie(df_crimi, gemeente, jaar):
    df_regressie = df_crimi[['SoortMisdrijf', 'RegioS', 'Perioden', 'GeregistreerdeMisdrijvenPer1000Inw_3']]
    df_regressie = df_regressie[df_regressie['SoortMisdrijf'] == 'Misdrijven, totaal']
    df_regressie.drop(columns='SoortMisdrijf', inplace=True)

    bevolking = download_reg(datetime.datetime.now().month)


    df_regressie = df_regressie.merge(bevolking, on=['RegioS', 'Perioden'])
    df_regressie['Perioden'] = df_regressie['Perioden'].astype(int)
    df_regressie['ln_GeregistreerdeMisdrijvenPer1000Inw_3'] = np.log(df_regressie['GeregistreerdeMisdrijvenPer1000Inw_3'])
    df_regressie['ln_Bevolkingsdichtheid_57'] = np.log(df_regressie['Bevolkingsdichtheid_57'])
    regressie = ols('ln_GeregistreerdeMisdrijvenPer1000Inw_3 ~ Perioden + ln_Bevolkingsdichtheid_57', data=df_regressie).fit()
    df_regressie['fitted values na terugtrans.'] = np.exp(regressie.fittedvalues)
    df_regressie['residuen na terugtrans.'] = df_regressie['GeregistreerdeMisdrijvenPer1000Inw_3'] - df_regressie['fitted values na terugtrans.']
    for i in range(0, len(df_regressie)):
        df_regressie.loc[i, 'Hovertext'] = str(df_regressie.loc[i, 'Perioden']) + ', ' + df_regressie.loc[i, 'RegioS']


    fig = go.Figure()

    fig.add_trace(go.Scatter(
                x=df_regressie['fitted values na terugtrans.'],
                y=df_regressie['GeregistreerdeMisdrijvenPer1000Inw_3'],
                mode='markers',
                hovertext=df_regressie['Hovertext'],
                marker={'size':4},
                showlegend=False,
                name=''))

    fig.add_trace(go.Scatter(
                x=(10,140),
                y=(10,140),
                mode='lines',
                line={'dash':'dot'},
                showlegend=False))


    def x_cor(stad, jaar):
        return df_regressie.loc[df_regressie['RegioS'] == str(stad)].iat[(jaar-2010), 6]

    def y_cor(stad, jaar):
        return df_regressie.loc[df_regressie['RegioS'] == str(stad)].iat[(jaar-2010), 2]

    # st.write(df_regressie.loc[df_regressie['RegioS'] == "Amsterdam"])
    # st.write(y_cor("Amsterdam", 2010))


    def gemeente_toevoegen(gemeente, jaar):
        a = {'x': x_cor(gemeente, jaar),
               'y': y_cor(gemeente, jaar),
               'showarrow': True,
               'arrowhead': 5,
               'text': '<b>' + gemeente + '</b>',
               'font': {'size': 13, 'color': 'black'}}
        return a

    annotations = []
    for g in gemeente:
        try:
            annotations.append(gemeente_toevoegen(g, jaar))
        except:
            pass


    R2 = {'x': 120,
          'y': 90,
          'showarrow': False,
          'text': '<b>' + 'R' + '<sup>2</sup>' + ' = ' + str(round(regressie.rsquared, 2)) + '</b>',
          'font': {'size': 15, 'color': 'black'},
          'bgcolor': 'gold'}

    annotations.append(R2)

    fig.update_xaxes(title_text='Gefitte waarde misdrijven / 1000 inw.')
    fig.update_yaxes(title_text='Werkelijke waarde misdrijven / 1000 inw.')
    fig.update_layout(title_text='Gefitte vs. werkelijke waarden geregistreerde misdrijven / 1000 inw. 2010-2020')
    fig.update_layout({'annotations':annotations})
    return fig







