import os
import pandas as pd
import streamlit as st
from pyproj import Proj

DATA_PATH = os.path.join("data","all_data_csvs", "religis_sites.csv")

utm2GeoProj = Proj("+proj=utm +zone=36K, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")

X_LABEL, Y_LABEL = "E_ORD", "N_ORD"


def utm2geo(lat,lon):
    return utm2GeoProj(lon,lat, inverse=True)


st.title(DATA_PATH)
df = pd.read_csv(DATA_PATH, index_col=0)
df["geo_ord"] = df.apply(lambda x: utm2geo(x.E_ORD, x.N_ORD), axis=1)
print(df["geo_ord"].values)
df["lon"], df["lat"] = df["geo_ord"][0], df["geo_ord"][1]
print(df[["lon","lat"]])

st.map(df)

