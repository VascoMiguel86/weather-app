import streamlit as st
import folium
from streamlit_folium import st_folium

from weather import get_temperature
from database import (
    init_db,
    create_favorite,
    read_favorites,
    update_favorite,
    delete_favorite,
)

init_db()

st.title("🌤️ Netherlands Weather Map")

# --- Map ---
m = folium.Map(location=[52.1, 5.3], zoom_start=7)
map_data = st_folium(m, width=700, height=500)

# --- Handle click ---
if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    st.session_state["clicked_lat"] = lat
    st.session_state["clicked_lon"] = lon
    temperature = get_temperature(lat, lon)
    st.info(f"Temperature at this location: **{temperature}**")

# --- Sidebar ---
st.sidebar.title("My Favorites")

# Save current clicked location as a favourite
if "clicked_lat" in st.session_state:
    with st.sidebar.form("save_form", clear_on_submit=True):
        location_name = st.text_input("Location name:")
        submitted = st.form_submit_button("Save location")
        if submitted:
            if location_name.strip():
                create_favorite(
                    location_name.strip(),
                    st.session_state["clicked_lat"],
                    st.session_state["clicked_lon"],
                )
                st.sidebar.success(f'Saved "{location_name}"')
            else:
                st.sidebar.warning("Please enter a name before saving.")

st.sidebar.markdown("---")

# List all favourites with Rename and Delete buttons
favorites = read_favorites()

if not favorites:
    st.sidebar.write("No favourites saved yet.")
else:
    for fav in favorites:
        col1, col2, col3 = st.sidebar.columns([3, 1, 1])
        col1.write(fav["name"])

        if col2.button("✏️", key=f"edit_{fav['id']}", help="Rename"):
            st.session_state[f"editing_{fav['id']}"] = True

        if col3.button("🗑️", key=f"delete_{fav['id']}", help="Delete"):
            delete_favorite(fav["id"])
            st.rerun()

        # Inline rename form — only shown when the edit button was clicked
        if st.session_state.get(f"editing_{fav['id']}"):
            with st.sidebar.form(f"rename_form_{fav['id']}", clear_on_submit=True):
                new_name = st.text_input("New name:", value=fav["name"])
                if st.form_submit_button("Rename"):
                    if new_name.strip():
                        update_favorite(fav["id"], new_name.strip())
                        st.session_state[f"editing_{fav['id']}"] = False
                        st.rerun()
