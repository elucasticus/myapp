import streamlit as st
import pandas as pd
import pydeck as pdk
import geocoder
from PIL import Image

#import images
img_restaurant = Image.open("restaurant_image.jpg")

#define functions
def f(feature1, feature2, feature3, latitude, longitude):
    return feature1 + feature2 + feature3 + latitude + longitude


#
#sidebar
#
st.sidebar.image(img_restaurant, width = 300, caption = "Photo by Jay Wennington, edited by Luca Crippa")

#sidebar menu
sidebar_menu = st.sidebar.selectbox("", ["Who we are", "Forketthub project", "Contact us"])
if sidebar_menu == "Contact us":
    st.sidebar.text("Have you a question about our project?\n\n")
    st.sidebar.text("You can contact us at:\nforkhubofficial@gmail.com\ngiacomodecarlo@mail.polimi.it")
elif sidebar_menu == "Who we are":
    st.sidebar.text("Giacomo\nLuca\nMargherita\nRajaa")

#
#main page
#

#import restaurant coordinates
r_data = pd.read_csv('coordinateristoranti.csv')
r_data.columns = ['lat', 'lng']

#set default location
df = pd.DataFrame()
df.at[1, 'lat'] = 45.4641
df.at[1, 'lng'] = 9.1919

#main menu
main_menu = st.selectbox("", ["Place your restaurant", "Our analysis"])
if main_menu == "Place your restaurant":

    #submit and geocode location
    location = st.text_input('Insert your location here (default position: "Milan Cathedral, Milan")')

    if st.button("Submit"):
        g = geocoder.osm(location)
        if g.ok:
            df.at[1, 'lat'] = g.json['lat']
            df.at[1, 'lng'] = g.json['lng']
            st.success("Location correctly found")
        else:
            st.error("location not found")

    #show map with submitted location in blue and all real restaurants in red
    st.pydeck_chart(
        pdk.Deck(map_style="mapbox://styles/mapbox/streets-v9", 
        initial_view_state={"latitude": df.at[1, 'lat'], "longitude": df.at[1, 'lng'], "zoom": 15, "pitch": 0}, layers=[
            pdk.Layer('ScatterplotLayer', data = df, get_position='[lng, lat]', get_color='[30, 0, 200, 160]', get_radius=12.5,),
            pdk.Layer('ScatterplotLayer', data = r_data, get_position='[lng, lat]', get_radius=12.5, get_color='[200, 30, 0, 160]'),
        ]
        ))
    st.text('Legend:\nBlue dot = submitted position\nRed dot = "there is a restaurant here"')
elif main_menu == "Our analysis":
    st.text("I risultati del progetto vanno qui")
