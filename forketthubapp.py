
import streamlit as st
import pandas as pd
import pydeck as pdk
import geocoder
import math
import haversine as hs
from PIL import Image
# import images
img_titolo = Image.open("titolo.png")
img_restaurant = Image.open("restaurant_image.jpg")
img_cappella1 = Image.open("cappella1.png")
img_cappella2 = Image.open("cappella2.png")
img_cappella3 = Image.open("cappella3.png")
img_cappella4 = Image.open("cappella4.png")
img_cappella5 = Image.open("cappella5.png")
img_cplot = Image.open("cplot.png")
img_anova1 = Image.open("anova1.png")
img_anova2 = Image.open("anova2.png")
img_anova3 = Image.open("anova3.png")
img_anova4 = Image.open("anova4.png")
img_modellolineare1 = Image.open("modellolineare1.png")
img_modellolineare2 = Image.open("modellolineare2.png")
img_modellolineare3 = Image.open("modellolineare3.png")
img_modellolineare4 = Image.open("modellolineare4.png")

# define functions
def modellocompleto(distanzaduomo, capitaleiniziale, giorni, livelloprezzo, dipendenti, indipendenti, michelin):
    return distanzaduomo* -1.299e+02  + distanzaduomo*distanzaduomo * 1.439e-02  + capitaleiniziale  *  1.374e+00  + giorni* 3.126e+01  + dipendenti  *  6.745e+04   + livelloprezzo   * 8.758e+04 + indipendenti  *   5.556e+04  + dipendenti*michelin * 1.794e+04


def modelloridotto(distanzaduomo, capitaleiniziale, giorni, livelloprezzo, kerneldistanceconst):
    return  distanzaduomo * -3.023e+01+ distanzaduomo*distanzaduomo*1.410e-02+ capitaleiniziale* 3.180e+00 + giorni* 8.038e+01  + livelloprezzo *3.003e+05+ kerneldistanceconst * 9.499e+03  + distanzaduomo*livelloprezzo * -5.319e+01  

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
elif sidebar_menu == "Forketthub project":
    st.sidebar.text("The goal of the project is to find \na model capable of predicting the \nrevenue of a restaurant in Milan \nbased on the data of a thousand \nother businesses running in the city.")

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
r_mezzo = pd.read_csv('coordinatemezzo.csv')
r_mezzo.columns = ['lat', 'lng']




# set default location
df = pd.DataFrame()
df.at[1, 'lat'] = 45.4641
df.at[1, 'lng'] = 9.1919

### MAIN MENU
###---------------------------
### model
###---------------------------
main_menu = st.selectbox("", ["Place your restaurant", "Curiosities", "Competition index"])
if main_menu == "Place your restaurant":

    # submit and geocode location
    location = st.text_input('Insert your location here (default position: "Milan Cathedral, Milan")')
    livelloprezzo = st.slider("Price level (1=Not expensive, 2 , 3 , 4=Very Expensive)", 1, 4)
    livelloprezzo = int(livelloprezzo)
    capitaleiniziale = st.text_input('Share capital (starting capital of the restaurant in €)', value = 0.)
    capitaleiniziale = float(capitaleiniziale)
    giorni = st.text_input('Days from the start (only for the complete model)', value = 0)
    giorni = int(giorni)
    dipendenti = st.text_input('Number of employees: (only for the complete model)', value = 0)
    dipendenti = int(dipendenti)
    indipendenti = st.text_input('Number of founders: (only for the complete model)', value = 0)
    indipendenti = int(indipendenti)
    michelin = st.checkbox('Any michelin star? (only for the complete model)')

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
            fatturatocompleto= modellocompleto(distanzadalduomo, capitaleiniziale, giorni, livelloprezzo, dipendenti, indipendenti, michelin)
            alpha = 0.15
            if distanzadalduomo < 10000:
                st.success('Complete model: revenue ∈ [' + str(int(fatturatocompleto*(1 - alpha))) + ', ' + str(int(fatturatocompleto*(1+alpha))) + ']')
                alpha = 0.45
                st.success('Reduced model: revenue ∈ [' + str(int(fatturatoridotto*(1 - alpha))) + ', ' + str(int(fatturatoridotto*(1+alpha))) + ']')
            else:
                st.error("Location must not be more than 10 km away from the city center")
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

    st.header('Our models')
    st.write('Here you can find and play with two different models to predict the revenue of a restaurant')
    st.write(
        'The first is a very accurate and interpretable model for the prediction of the income of a restaurant. The best use of this is to predict the revenue of an already existing restaurant since most of the variables are unknown at the opening of the business. It’s very robust with only few outliers in the predictors.')
    st.image(img_modellolineare1)
    st.write('The prediction interval will be in the form:')
    st.image(img_modellolineare2)
    st.write(
        'We estimated (through LOO Cross Validation) an interval of this form with  α=0.143 would contain the real value 93% of the times and the parameters are estimated through OLS. R^2=0.86')
    st.write(
        'The second model (Reduced model for the revenue) is intended to be used to predict the revenue of a restaurant someone wants to open. Only variables that are supposed to be know when starting the business are used.')
    st.image(img_modellolineare3)
    st.write('The prediction interval will be in the form:')
    st.image(img_modellolineare4)
    st.write(
        'We estimated (through LOO Cross Validation) an interval of this form with  α=0.431 would contain the real value 89% of the times. R^2=0.56')
    st.write('Here you can fit the models with your data and find the best position to open your own restaurant')

###---------------------------
### curiosities
###---------------------------
elif main_menu == "Curiosities":
    st.header('ANOVA tests')
    # show map with michelin restaurant in blue and normal restaurants in red
    st.pydeck_chart(
        pdk.Deck(map_style="mapbox://styles/mapbox/streets-v9", 
        initial_view_state={"latitude": df.at[1, 'lat'], "longitude": df.at[1, 'lng'], "zoom": 12.5, "pitch": 0}, layers=[
            pdk.Layer('ScatterplotLayer', data = r_data_nonmichelin, get_position='[lng, lat]', get_color='[30, 0, 200, 160]', get_radius=20,),
            pdk.Layer('ScatterplotLayer', data = r_data_michelin, get_position='[lng, lat]', get_radius=40, get_color='[200, 30, 0, 160]'),
        ]
        ))
    st.text('Blue dot = no Michelin stars\nRed dot = at least one Michelin star')
    st.write('The ANOVA test Ricavi  ~ Michelin aims at investigating differences of revenues between the Michelin-starred restaurants in Milan and the others. There is statistical evidence of a difference in the mean of the two groups, and the starred restaurants turn out to have higher mean revenue. This can be explained with the fact that such types of restaurants usually make bigger investments, have more workers and have a high level of price of the menu, so there is a large turnover.')
    st.write('A confidence interval for the difference of the mean of non Michelin and Michelin restaurants is (-894160, -79374.8) at level 95%.')
    st.image(img_anova1)
    st.write('Things change when we inspect the variable “Utile o perdite” which represents the profit. The ANOVA test shows that there isn’t a significant difference in the mean of the profit of the two categories of restaurants (starred and not). Like we said, starred restaurants may be big or with a large turnover but in the end, they also have a lot of expenses (skilled chefs, quality of the food…) and the gain is not different from the other structures.')
    st.image(img_anova2)
    st.write('A confidence interval for the difference of the mean of Michelin and non-Michelin restaurants is (-21675.94, 86102.08) at level 95%.')
    
    # show map with different colors for restaurants depending on their distance from the center of the city
    st.pydeck_chart(
        pdk.Deck(map_style="mapbox://styles/mapbox/streets-v9", 
        initial_view_state={"latitude": df.at[1, 'lat'], "longitude": df.at[1, 'lng'], "zoom": 12.5, "pitch": 0}, layers=[
            pdk.Layer('ScatterplotLayer', data = r_centro, get_position='[lng, lat]', get_color='[30, 0, 200, 160]', get_radius=20,),
            pdk.Layer('ScatterplotLayer', data = r_periferia, get_position='[lng, lat]', get_radius=20, get_color='[200, 30, 0, 160]'),
            pdk.Layer('ScatterplotLayer', data = r_mezzo, get_position='[lng, lat]', get_radius=20, get_color='[0, 200, 30, 160]'),
        ]
        ))
    st.text('Blue dot = centre\nRed dot = suburbs\nGreen dot = middle')
    st.write('We may want to highlight the role of the position over the revenues from a categorical point of view. We have created a variable which values are “suburbs” for the places more than three kilometres distant from the centre, which we identify with the Milan Cathedral, “middle” for restaurants with intermediate distance (between one and three kilometres from the Cathedral) and “centre” for the others. Three kilometres from the cathedral is approximately the radius of the ring road of Milan.  The places situated near the centre have higher mean revenues, since they are the most visited from tourists and office workers and they are usually more expensive, so they have large incomings. The difference in the mean revenues is not very significant when we analyse the groups “suburbs” and “middle”.')
    st.image(img_anova3)
    st.write('Confidence intervals at level 95% for the difference of the mean revenues are: (122136.03, 572802.7) for the difference between the restaurants in the centre and the restaurants in the middle; (248470.76, 742855.0) for the difference between the restaurants in the centre and the restaurants in the suburbs; (-22120.37, 318507.4) for the difference between the restaurants in the middle and the restaurants in the suburbs')

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
    st.write('Another interesting ANOVA test is ratings ~ iscenter. It shows us that the mean of the ratings for the restaurants in one zone is not different from the one of restaurants in the others, even though there is a difference in the mean revenues. The rating is not a measure of the size of the business but is related with quality and subjective factors which are similar for the suburbs, for the middle and for the centre and that we cannot inspect with our database.')
    st.image(img_anova4)
    st.write('Confidence intervals at level 95% for the difference of the mean ratings are: (-0.09716711, 0.04990659) for the difference between the restaurants in the centre and the restaurants in the middle; ( -0.10449932, 0.05684150) for the difference between the restaurants in the centre and the restaurants in the suburbs; (-0.05578008, 0.05538278) for the difference between the restaurants in the middle and the restaurants in the suburbs')

###---------------------------
### Gaussian kernel competition index
###---------------------------
elif main_menu == "Competition index":
    st.header('Gaussian kernel competition index')
    st.write('We need an index that works in a simple way: fixing a location, the value of the index is low if there are few restaurants in its neighborhood and vice versa.')
    st.write('The idea is to just put on every restaurant a “bell” which represents the influence each one has on all the others.')
    st.image(img_cappella1)
    st.write('We can vary a parameter (sigma) to decide how far the influence of each restaurant goes, thus varying the shape of our bell. If we increase sigma we get a larger bell and the influence of each restaurant expands:')
    st.image(img_cappella2)
    st.write('If we reduce sigma, we obviously get a smaller bell:')
    st.image(img_cappella3)
    st.write('We decided to set sigma in two different ways creating different features for our analysis:')
    st.write('1) We set a constant sigma such that being 500m away from a restaurant would mean having only 10% of the influence of it.')
    st.write('2) We set a sigma parameter that linearly varies with reference to the distance from the Duomo di Milano such that when we are close to the Cathedral, 10% of the influence is achieved at just 200m of distance.')
    st.write('Here is an example with two restaurants:')
    st.image(img_cappella4)
    st.write('And with three:')
    st.image(img_cappella5)
    st.write('Contour plot with all the restaurants:')
    st.image(img_cplot)
