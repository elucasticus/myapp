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
def modellocompleto(distanzaduomo, capitaleiniziale, giorni, livelloprezzo, dipendenti, indipendenti, michelin):
    return distanzaduomo*(-1.298e+02)  + distanzaduomo * distanzaduomo * 1.439e-02 + capitaleiniziale  *  1.374e+00 + giorni * 3.126e+01 + dipendenti  *  6.744e+04 + livelloprezzo *  8.768e+04 + indipendenti  *   5.547e+04 + dipendenti*michelin * 1.794e+04

def modelloridotto(distanzaduomo, capitaleiniziale, giorni, livelloprezzo, kerneldistanceconst):
    return distanzaduomo*(-7.766e+01) + distanzaduomo*distanzaduomo*1.030e-02 + capitaleiniziale* 3.214e+00  + giorni* 8.478e+01  + livelloprezzo *2.105e+05 + kerneldistanceconst * 1.568e+04

def modelloutile(nreviews, giorni):
    return  -40446.012 + 20.533*nreviews + 7.709*giorni


def kernelconst(lat, lng, data):
    kerneldistace = 0
    loc1 = (lat, lng)
    for i in range(1,data.shape[0]):
        loc2 = (data.at[i, 'lat'], data.at[i, 'lng']) 
        kerneldistace +=  math.exp(-(hs.haversine(loc1, loc2)*1000/330)*(hs.haversine(loc1, loc2)*1000/330))
    return kerneldistace

def kernelvar(lat, lng, data):
    kerneldistace = 0
    loc1 = (lat, lng)
    duomo = (45.4641, 9.1919)
    k = 0.02828571*hs.haversine(loc1, duomo)*1000+132
    for i in range(1,data.shape[0]):
        loc2 = (data.at[i, 'lat'], data.at[i, 'lng']) 
        kerneldistace +=  math.exp(-(hs.haversine(loc1, loc2)*1000/k)*(hs.haversine(loc1, loc2)*1000/k))
    return kerneldistace


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
    st.sidebar.text("Giacomo De Carlo \nLuca Crippa\nMargherita Basilico\nRajaa Bakir")

###---------------------------
### main page
###---------------------------

st.image(img_titolo)

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
    livelloprezzo = st.slider("Price level", 1, 4)
    livelloprezzo = int(livelloprezzo)
    capitaleiniziale = st.text_input('Share capital', value = 0.)
    capitaleiniziale = float(capitaleiniziale)

    if st.button("Submit"):
        g = geocoder.osm(location)
        if g.ok:
            df.at[1, 'lat'] = g.json['lat']
            df.at[1, 'lng'] = g.json['lng']
            kerneldistanceconst = kernelconst(df.at[1, 'lat'], df.at[1, 'lng'], r_data)
            kerneldistancevar = kernelvar(df.at[1, 'lat'], df.at[1, 'lng'], r_data)
            currentlocation = (df.at[1, 'lat'], df.at[1, 'lng'])
            duomo = (45.4641, 9.1919)
            distanzadalduomo = hs.haversine(currentlocation, duomo)*1000
            fatturatoridotto = modelloridotto(distanzadalduomo, capitaleiniziale, 0., livelloprezzo, kerneldistanceconst)
            alpha = 0.1
            st.success(str(fatturatoridotto*(1 - alpha)) + ', ' + str(fatturatoridotto*(1+alpha)))
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
    st.text('Blue dot = submitted position\nRed dot = "there is a restaurant here"')
elif main_menu == "Curiosities":
    # show map with michelin restaurant in blue and normal restaurants in red
    st.pydeck_chart(
        pdk.Deck(map_style="mapbox://styles/mapbox/streets-v9", 
        initial_view_state={"latitude": df.at[1, 'lat'], "longitude": df.at[1, 'lng'], "zoom": 12.5, "pitch": 0}, layers=[
            pdk.Layer('ScatterplotLayer', data = r_data_nonmichelin, get_position='[lng, lat]', get_color='[30, 0, 200, 160]', get_radius=20,),
            pdk.Layer('ScatterplotLayer', data = r_data_michelin, get_position='[lng, lat]', get_radius=40, get_color='[200, 30, 0, 160]'),
        ]
        ))
    st.text('Blue dot = no michelin stars\nRed dot = at least one michelin star')
    st.write('The ANOVA test Ricavi  ~ Michelin aims at investigating differences of revenues between the Michelin-starred restaurants in Milan and the others. There is statistical evidence of a difference in the mean of the two groups, and the starred restaurants turn out to have higher mean revenue. This can be explained with the fact that such types of restaurants usually make bigger investments, have more workers and have a high level of price of the menu, so there is a large turnover.')
    st.write('Things change when we inspect the variable “Utile o perdite” which represents the profit. The ANOVA tests shows that there isn’t a significant difference in the mean of the profit of the two categories of restaurants (starred and not). Like we said, starred restaurants may be big or with a large turnover but in the end, they also have a lot of expenses (expert cooks, quality of the food…) and so the gain is not different from the other structures.')
    
    # show map with different colors for restaurants depending on their distance from the center of the city
    st.pydeck_chart(
        pdk.Deck(map_style="mapbox://styles/mapbox/streets-v9", 
        initial_view_state={"latitude": df.at[1, 'lat'], "longitude": df.at[1, 'lng'], "zoom": 12.5, "pitch": 0}, layers=[
            pdk.Layer('ScatterplotLayer', data = r_centro, get_position='[lng, lat]', get_color='[30, 0, 200, 160]', get_radius=20,),
            pdk.Layer('ScatterplotLayer', data = r_periferia, get_position='[lng, lat]', get_radius=20, get_color='[200, 30, 0, 160]'),
        ]
        ))
    st.text('Blue dot = periferic\nRed dot = central')
    st.write('We may want to highlight the role of the position over the revenues from a categorical point of view. We have created a variable iscenter which values are “periferia” (suburbs) for the places which are more than 1km distant from the centre, which we identify with the Milan Cathedral, and “centro” (centre) for the others. The place situated near the centre have higher mean revenues, in fact they are the most visited from tourists and office workers and they are usually more expensive, so they have large incomings.')

    # show map with different colors for restaurants depending on their rating
    st.pydeck_chart(
        pdk.Deck(map_style="mapbox://styles/mapbox/streets-v9", 
        initial_view_state={"latitude": df.at[1, 'lat'], "longitude": df.at[1, 'lng'], "zoom": 12.5, "pitch": 0}, layers=[
            pdk.Layer('ScatterplotLayer', data = r_data3, get_position='[lng, lat]', get_color='[30, 0, 200, 160]', get_radius=20,),
            pdk.Layer('ScatterplotLayer', data = r_data4, get_position='[lng, lat]', get_radius=20, get_color='[200, 30, 0, 160]'),
            pdk.Layer('ScatterplotLayer', data = r_data5, get_position='[lng, lat]', get_radius=20, get_color='[0, 200, 30, 160]'),
        ]
        ))
    st.text('Blue dot = 3 stars\nRed dot = 4 stars\nGreen dot = 5 stars')
    st.write('Another interesting ANOVA test is ratings ~ iscenter. It shows us that the mean of the ratings for the restaurants in the suburbs is not different from the one of restaurants in the center, even though like we have showed above there is a difference in the mean revenues. The rating is not a measure of the size of the business but is related with quality and subjective factors which are similar for the suburbs and the centre and that we cannot inspect with our database.')

elif main_menu == "Data":
    st.text("")