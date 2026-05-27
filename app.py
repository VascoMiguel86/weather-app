import streamlit as st
import folium
from streamlit_folium import st_folium

from database import init_db

# Initialise the database on every startup (safe to run multiple times)
init_db()

st.title("🌤️ Netherlands Weather Map")

# Build the map centred on the Netherlands
m = folium.Map(location=[52.1, 5.3], zoom_start=7)

# Render the map and capture click events
# width/height in pixels — adjust if needed
map_data = st_folium(m, width=700, height=500)
