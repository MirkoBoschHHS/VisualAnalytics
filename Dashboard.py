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


# Primary accent for interactive elements
primaryColor = '#7792E3'

# Background color for the main content area
backgroundColor = '#273346'

# Background color for sidebar and most interactive widgets
secondaryBackgroundColor = '#B9F1C0'

# Color used for almost all text
textColor = '#FFFFFF'

# Font family for all text in the app, except code blocks
# Accepted values (serif | sans serif | monospace)
# Default: "sans serif"
font = "sans serif"


# Enkele standaard opties
st.set_page_config(layout="wide") # Zorgt voor default wide op streamlit
pd.set_option('display.max_columns', None) # Print alles van de DataFrame pandas


# Maak een titel
st.title('Dashboard')