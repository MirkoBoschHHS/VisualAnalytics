import streamlit as st
import pandas as pd
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

import navigation

# Enkele standaard opties
st.set_page_config(layout="wide") # Zorgt voor default wide op streamlit
pd.set_option('display.max_columns', None) # Print alles van de DataFrame pandas


st.sidebar.title("Navigation")
nav = st.sidebar.radio("Go to:", ['Home', 'results'])




navigation.navigation(nav)




st.sidebar.title("About")
st.sidebar.info('This app is made by Mirko Bosch en Sjoerd Fijnje.')