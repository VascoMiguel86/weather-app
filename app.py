import streamlit as st
import folium
from streamlit_folium import st_folium

from weather import get_temperature
from database import init_db

init_db()

st.title("🌤️ Netherlands Weather Map")

# --- Map ---
m = folium.Map(location=[52.1, 5.3], zoom_start=7)
map_data = st_folium(m, width=700, height=500)

# --- Handle click ---
if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]

    # Store clicked coordinates in session state so the sidebar can use them
    st.session_state["clicked_lat"] = lat
    st.session_state["clicked_lon"] = lon

    temperature = get_temperature(lat, lon)
    st.info(f"Temperature at this location: **{temperature}**")
