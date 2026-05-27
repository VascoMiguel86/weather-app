import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime

from weather import get_temperature, get_forecast
from database import (
    init_db,
    create_favorite,
    read_favorites,
    update_favorite,
    delete_favorite,
)

# ── Must be first Streamlit call ──────────────────────────────────────────────
st.set_page_config(
    page_title="Netherlands Weather",
    page_icon="🌤️",
    layout="wide",
)

init_db()

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Hide Streamlit chrome for a cleaner look */
#MainMenu, header, footer { visibility: hidden; }

/* App background — deep navy like Buienradar */
.stApp {
    background: linear-gradient(160deg, #0b1f3b 0%, #163361 55%, #0d2145 100%);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #091a38 0%, #0d2448 100%);
    border-right: 1px solid rgba(79, 195, 247, 0.18);
}

/* ── Temperature card (shown after map click) ── */
.temp-card {
    display: flex;
    align-items: center;
    gap: 20px;
    background: linear-gradient(135deg,
        rgba(79,195,247,.18) 0%,
        rgba(21,101,192,.18) 100%);
    border: 1px solid rgba(79, 195, 247, .40);
    border-radius: 18px;
    padding: 22px 30px;
    margin: 14px 0 20px;
    color: #e8f4fd;
}
.temp-card .tc-num   { font-size: 3.8rem; font-weight: 800; color: #4fc3f7; line-height: 1; }
.temp-card .tc-label { font-size: 0.95rem; color: #90caf9; margin-top: 4px; }
.temp-card .tc-emoji { font-size: 3rem; }

/* ── Forecast strip ── */
.fcast-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #90caf9;
    letter-spacing: .06em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.fcast-wrap {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}
.fcast-card {
    flex: 1;
    background: rgba(255, 255, 255, 0.07);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(79, 195, 247, 0.20);
    border-radius: 14px;
    padding: 14px 6px 12px;
    text-align: center;
    color: #e8f4fd;
    transition: border-color .2s;
}
.fcast-card:hover { border-color: rgba(79, 195, 247, 0.55); }
.fcast-card .fc-day  { font-size: .80rem; font-weight: 700; color: #90caf9;
                        letter-spacing: .05em; text-transform: uppercase; }
.fcast-card .fc-date { font-size: .68rem; color: #546e7a; margin: 2px 0 8px; }
.fcast-card .fc-icon { font-size: 1.75rem; }
.fcast-card .fc-max  { font-size: 1.20rem; font-weight: 700; color: #ff8a65; margin-top: 6px; }
.fcast-card .fc-min  { font-size: .85rem; color: #90caf9; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def _sky_icon(max_temp: float) -> str:
    """Pick a weather emoji based on expected max temperature."""
    if max_temp >= 28: return "☀️"
    if max_temp >= 21: return "🌤️"
    if max_temp >= 13: return "⛅"
    if max_temp >=  5: return "🌥️"
    return "❄️"


def _forecast_html(forecast: list[dict]) -> str:
    cards = ""
    for d in forecast:
        dt   = datetime.strptime(d["date"], "%Y-%m-%d")
        day  = dt.strftime("%a")
        date = dt.strftime("%d %b")
        icon = _sky_icon(d["max"])
        cards += f"""
        <div class="fcast-card">
            <div class="fc-day">{day}</div>
            <div class="fc-date">{date}</div>
            <div class="fc-icon">{icon}</div>
            <div class="fc-max">{d['max']}°</div>
            <div class="fc-min">↓ {d['min']}°</div>
        </div>"""
    return f'<div class="fcast-wrap">{cards}</div>'


# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(
    "<h2 style='color:#4fc3f7; margin-bottom:4px;'>🌤️ Netherlands Weather</h2>"
    "<p style='color:#607d8b; margin-top:0; font-size:.9rem;'>"
    "Click anywhere on the map to get the current temperature.</p>",
    unsafe_allow_html=True,
)

# ── Map ───────────────────────────────────────────────────────────────────────
# Version key: increment to force a fresh map when tile/settings change.
_MAP_VER = "v5-voyager"
if st.session_state.get("_map_ver") != _MAP_VER:
    st.session_state["folium_map"] = folium.Map(
        location=[52.1, 5.3],
        zoom_start=7,
        tiles="CartoDB Voyager",
    )
    st.session_state["_map_ver"] = _MAP_VER

map_data = st_folium(
    st.session_state["folium_map"],
    use_container_width=True,
    height=480,
    returned_objects=["last_clicked"],
)

# ── Map-click: current temperature ───────────────────────────────────────────
if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]

    # st_folium's last_clicked is sticky — it keeps returning the same
    # coordinates on every rerun until the user actually clicks somewhere new.
    # We track the last position we already handled in _processed_click and
    # skip the event if it hasn't changed.
    if (lat, lon) != st.session_state.get("_processed_click"):
        st.session_state["_processed_click"] = (lat, lon)
        st.session_state["clicked_lat"] = lat
        st.session_state["clicked_lon"] = lon
        st.session_state.pop("selected_fav", None)
        temperature = get_temperature(lat, lon)
        icon = "🌡️" if "Could not" not in temperature else "⚠️"
        st.markdown(f"""
    <div class="temp-card">
        <div class="tc-emoji">{icon}</div>
        <div>
            <div class="tc-num">{temperature}</div>
            <div class="tc-label">Current temperature at clicked location</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Favourite forecast ────────────────────────────────────────────────────────
if "selected_fav" in st.session_state:
    fav = st.session_state["selected_fav"]
    forecast = get_forecast(fav["lat"], fav["lon"])
    if isinstance(forecast, str):
        st.error(forecast)
    else:
        st.markdown(
            f"<div class='fcast-title'>📅 7-day forecast — {fav['name']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(_forecast_html(forecast), unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown(
    "<h3 style='color:#4fc3f7; margin-bottom:8px;'>⭐ My Favorites</h3>",
    unsafe_allow_html=True,
)

# Save form — only shown after a map click
if "clicked_lat" in st.session_state:
    with st.sidebar.form("save_form", clear_on_submit=True):
        location_name = st.text_input("📍 Location name:")
        if st.form_submit_button("💾 Save location"):
            if location_name.strip():
                create_favorite(
                    location_name.strip(),
                    st.session_state["clicked_lat"],
                    st.session_state["clicked_lon"],
                )
                del st.session_state["clicked_lat"]
                del st.session_state["clicked_lon"]
                st.rerun()
            else:
                st.warning("Please enter a name before saving.")

st.sidebar.markdown(
    "<hr style='border-color: rgba(79,195,247,.2); margin:12px 0;'>",
    unsafe_allow_html=True,
)

# Favourites list
favorites = read_favorites()
if not favorites:
    st.sidebar.markdown(
        "<p style='color:#546e7a; font-size:.85rem;'>No favourites saved yet.<br>"
        "Click the map and save a location.</p>",
        unsafe_allow_html=True,
    )
else:
    for fav in favorites:
        col1, col2, col3 = st.sidebar.columns([3, 1, 1])

        # Name is a button — click to see 7-day forecast
        if col1.button(f"📌 {fav['name']}", key=f"select_{fav['id']}"):
            st.session_state["selected_fav"] = {
                "name": fav["name"],
                "lat":  fav["lat"],
                "lon":  fav["lon"],
            }
            st.session_state.pop("clicked_lat", None)
            st.session_state.pop("clicked_lon", None)
            # Anchor _processed_click to whatever last_clicked currently is.
            # Without this, the stale last_clicked fires on the next rerun,
            # wipes selected_fav, and the 7-day forecast never appears.
            if map_data and map_data.get("last_clicked"):
                lc = map_data["last_clicked"]
                st.session_state["_processed_click"] = (lc["lat"], lc["lng"])
            st.rerun()

        if col2.button("✏️", key=f"edit_{fav['id']}", help="Rename"):
            st.session_state[f"editing_{fav['id']}"] = True

        if col3.button("🗑️", key=f"delete_{fav['id']}", help="Delete"):
            delete_favorite(fav["id"])
            st.rerun()

        if st.session_state.get(f"editing_{fav['id']}"):
            with st.sidebar.form(f"rename_{fav['id']}", clear_on_submit=True):
                new_name = st.text_input("New name:", value=fav["name"])
                if st.form_submit_button("Rename"):
                    if new_name.strip():
                        update_favorite(fav["id"], new_name.strip())
                        st.session_state[f"editing_{fav['id']}"] = False
                        st.rerun()
                    else:
                        st.warning("Please enter a name before renaming.")
