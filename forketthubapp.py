import streamlit as st
import pandas as pd
import pydeck as pdk
import geocoder
import math
import haversine as hs
from PIL import Image

# import images
img_restaurant = Image.open("restaurant_image.jpg")
img_titolo = Image.open("titolo.png")

# define functions
def f(feature1, feature2, feature3, latitude, longitude):
    return feature1 + feature2 + feature3 + latitude + longitude

def kernelconst(lat, lng, data):
    kerneldistace = 0
    loc1 = (lat, lng)
    for i in range(1,data.shape[0]):
        loc2 = (data.at[i, 'lat'], data.at[i, 'lng']) 
        kerneldistace +=  math.exp(-(hs.haversine(loc1, loc2)/330)*(hs.haversine(loc1, loc2)/330))

def kernelvar(lat, lng, data):
    kerneldistace = 0
    loc1 = (lat, lng)
    duomo = (45.4641, 9.1919)
    k = 0.02828571*hs.haversine(loc1, duomo)+132
    for i in range(1,data.shape[0]):
        loc2 = (data.at[i, 'lat'], data.at[i, 'lng']) 
        kerneldistace +=  math.exp(-(hs.haversine(loc1, loc2)/k)*(hs.haversine(loc1, loc2)/k))


###---------------------------
### sidebar
###---------------------------

st.sidebar.image(img_restaurant, use_column_width = True, caption = "Photo by Eleonora Verdelli, edited by Luca Crippa")

#sidebar menu
sidebar_menu = st.sidebar.selectbox("", ["Who we are", "Forketthub project", "Contact us"])
if sidebar_menu == "Contact us":
    st.sidebar.text("Do you have a question about \nour project?\n\n")
    st.sidebar.text("You can contact us at:\nforkhubofficial@gmail.com\ngiacomodecarlo@mail.polimi.it")
elif sidebar_menu == "Who we are":
    st.sidebar.text("Giacomo\nLuca\nMargherita\nRajaa")

###---------------------------
### main page
###---------------------------

st.image(img_titolo, width = 300)

# import restaurant coordinates
r_data = pd.read_csv('coordinateristoranti.csv')
r_data.columns = ['lat', 'lng']

# import michelin restaurant coordinates
r_data_michelin = pd.read_csv('coordinatemichelin.csv')
r_data_michelin.columns = ['lat', 'lng']

# import non-michelin restaurant coordinates
r_data_nonmichelin = pd.read_csv('coordinatenonmichelin.csv')
r_data_nonmichelin.columns = ['lat', 'lng']

# import ratings data
r_data3 = pd.read_csv('coordinate3s.csv')
r_data3.columns = ['lat', 'lng']
r_data4 = pd.read_csv('coordinate4s.csv')
r_data4.columns = ['lat', 'lng']
r_data5 = pd.read_csv('coordinate5s.csv')
r_data5.columns = ['lat', 'lng']


# import center and periferic data
r_centro = pd.read_csv('coordinatecentro.csv')
r_centro.columns = ['lat', 'lng']
r_periferia = pd.read_csv('coordinateperiferia.csv')
r_periferia.columns = ['lat', 'lng']



# set default location
df = pd.DataFrame()
df.at[1, 'lat'] = 45.4641
df.at[1, 'lng'] = 9.1919

# main menu
main_menu = st.selectbox("", ["Place your restaurant", "Curiosities", "Data"])
if main_menu == "Place your restaurant":

    # submit and geocode location
    location = st.text_input('Insert your location here (default position: "Milan Cathedral, Milan")')

    if st.button("Submit"):
        g = geocoder.osm(location)
        if g.ok:
            df.at[1, 'lat'] = g.json['lat']
            df.at[1, 'lng'] = g.json['lng']
            kerneldistaceconst = kernelconst(df.at[1, 'lat'], df.at[1, 'lng'], r_data)
            kerneldistancevar = kernelvar(df.at[1, 'lat'], df.at[1, 'lng'], r_data)
            location = (df.at[1, 'lat'], df.at[1, 'lng'])
            duomo = (45.4641, 9.1919)
            distanzadalduomo = hs.haversine(location, duomo)
            st.success("Location correctly found")
        else:
            st.error("Location not found")

    # show map with submitted location in blue and all real restaurants in red
    st.pydeck_chart(
        pdk.Deck(map_style="mapbox://styles/mapbox/streets-v9", 
        initial_view_state={"latitude": df.at[1, 'lat'], "longitude": df.at[1, 'lng'], "zoom": 15, "pitch": 0}, layers=[
            pdk.Layer('ScatterplotLayer', data = df, get_position='[lng, lat]', get_color='[30, 0, 200, 160]', get_radius=12.5,),
            pdk.Layer('ScatterplotLayer', data = r_data, get_position='[lng, lat]', get_radius=12.5, get_color='[200, 30, 0, 160]'),
        ]
        ))
    st.text('Legend:\nBlue dot = submitted position\nRed dot = "there is a restaurant here"')
elif main_menu == "Curiosities":
    # show map with michelin restaurant in blue and normal restaurants in red
    st.pydeck_chart(
        pdk.Deck(map_style="mapbox://styles/mapbox/streets-v9", 
        initial_view_state={"latitude": df.at[1, 'lat'], "longitude": df.at[1, 'lng'], "zoom": 12.5, "pitch": 0}, layers=[
            pdk.Layer('ScatterplotLayer', data = r_data_nonmichelin, get_position='[lng, lat]', get_color='[30, 0, 200, 160]', get_radius=20,),
            pdk.Layer('ScatterplotLayer', data = r_data_michelin, get_position='[lng, lat]', get_radius=40, get_color='[200, 30, 0, 160]'),
        ]
        ))
    st.text('Legend:\nBlue dot = no michelin stars\nRed dot = at least one michelin star')
    # show map with different colors for restaurants depending on their rating
    st.pydeck_chart(
        pdk.Deck(map_style="mapbox://styles/mapbox/streets-v9", 
        initial_view_state={"latitude": df.at[1, 'lat'], "longitude": df.at[1, 'lng'], "zoom": 12.5, "pitch": 0}, layers=[
            pdk.Layer('ScatterplotLayer', data = r_data3, get_position='[lng, lat]', get_color='[30, 0, 200, 160]', get_radius=20,),
            pdk.Layer('ScatterplotLayer', data = r_data4, get_position='[lng, lat]', get_radius=20, get_color='[200, 30, 0, 160]'),
            pdk.Layer('ScatterplotLayer', data = r_data5, get_position='[lng, lat]', get_radius=20, get_color='[0, 200, 30, 160]'),
        ]
        ))
    st.text('Legend:\nBlue dot = 3 stars\nRed dot = 4 stars\nGreen dot = 5 stars')
    # show map with different colors for restaurants depending on their distance from the center of the city
    st.pydeck_chart(
        pdk.Deck(map_style="mapbox://styles/mapbox/streets-v9", 
        initial_view_state={"latitude": df.at[1, 'lat'], "longitude": df.at[1, 'lng'], "zoom": 12.5, "pitch": 0}, layers=[
            pdk.Layer('ScatterplotLayer', data = r_centro, get_position='[lng, lat]', get_color='[30, 0, 200, 160]', get_radius=20,),
            pdk.Layer('ScatterplotLayer', data = r_periferia, get_position='[lng, lat]', get_radius=20, get_color='[200, 30, 0, 160]'),
        ]
        ))
    st.text('Legend:\nBlue dot = periferic\nRed dot = central')    
elif main_menu == "Data":
    st.text("")