import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

st.set_page_config(page_title="Konkan Gaur Migration Demo", layout="wide")

st.title("🦬 Indian Gaur Migration — Konkan (Demo)")
st.caption("Interactive demo app — English + Marathi (मराठी)")

# Sample data (replace with your real CSV later)
data = pd.DataFrame({
    "district": ["Raigad", "Ratnagiri", "Sindhudurg", "Thane", "Palghar"],
    "lat": [18.53, 16.99, 16.13, 19.21, 19.70],
    "lon": [73.27, 73.30, 73.60, 72.97, 72.77],
    "count": [18, 13, 11, 6, 4]
})

st.subheader("Sample Sightings Data")
st.dataframe(data)

# Map
m = folium.Map(location=[17.9, 73.2], zoom_start=7, tiles="CartoDB positron")
HeatMap(data[["lat", "lon", "count"]].values.tolist(), radius=35).add_to(m)
st_map = st_folium(m, width=700, height=500)

# Chart
st.subheader("Sample Trend Chart")
st.line_chart(pd.Series([220, 255, 352, 500, 645, 950, 1260], 
                        index=pd.Index(range(2018, 2025), name="Year"), 
                        name="Sightings"))
