import streamlit as st
import csv
import requests
from math import *
import folium

déplacement = ['driving', 'cycling', 'walking','driving-traffic']
def createjson(moyendeD, lon1,lat1,lon2,lat2):
    tempUrl = requests.get( 'https://api.mapbox.com/directions/v5/mapbox/' + moyendeD +'/' + lon1 +','+ lat1+';' +lon2+',' + lat2  +'?geometries=geojson&access_token=pk.eyJ1Ijoic2ViYXN0aWVuLWRhdmlkIiwiYSI6ImNsaWxpbXM4MzBla2MzZXBrdnhscHN1MTkifQ.eOUH0fMJt-QlEqhTq0EAQQ')
    return tempUrl.json()

bikeStationInfo = {}
fileLocation = "BikeStations.csv"
#needed to ask for the curl command
headers = {
    'accept': 'application/json',
}

colorLine = ('red','blue','green','purple')

def calculateClosePosition(longitudeA,latitudeA, longitudeB, latitudeB):
    return 6371 * acos(sin(longitudeA)*sin(longitudeB)+ cos(longitudeA)*cos(longitudeB)*cos(latitudeB-latitudeA))


coordinatesBikeClosest = []
with st.form("Bike station finder"):
    st.write("inside the form")
    #The coordinates to input in the form
    number1 = st.number_input("insert longitude",value=3.8, format='%f', step=0.000001 )
    number2 = st.number_input("insert latitude",value=43.6, format='%f', step=0.000001 )
    checkbox_walking = st.checkbox('Walking')
    checkbox_driving = st.checkbox('Driving')
    checkbox_cycling = st.checkbox('Cycling')
    checkbox_buses = st.checkbox('Buses')
    submitted = st.form_submit_button("Submit")
    if submitted:
        printRouteOrNotBoolean = (checkbox_driving,checkbox_cycling, checkbox_walking, checkbox_buses)
        m = folium.Map(location=[number2,number1])
        if m != None:
            del m
        m = folium.Map(location=[number2,number1], zoom_start= 12)
        
        #To know which bike station are we studying
        counter = 0
        #The value to store the distance of the closest bike station
        tempValue = 100000
        with open(fileLocation,'r') as f:    
            csvreader =  csv.reader(f)
            #Iterate through every bike station to know which one is closer
            for line in csvreader:
                counter+=1
                #If it is the first line, skip
                if(line[0] == 'ID'):
                    continue
                #Calculating the distance tou our coordinates
                tempCloseValue = calculateClosePosition(number1,
                                                        number2,
                                                        float(line[4]),
                                                        float(line[5]))
                #Check if value is closer than the actual closest position
                if (tempCloseValue) < tempValue:
                    params = {
                    'id': 'urn:ngsi-ld:station:'  +"{:03d}".format(counter),
                    'limit': '1000',
                    }
                    

                    
                    response = requests.get('https://portail-api-data.montpellier3m.fr/bikestation', params=params, headers=headers)
                    test = response.json()
                    if (test[0]['availableBikeNumber']['value']) != 0:
                        tempValue = tempCloseValue
                        coordinatesBikeClosest = [line[4], line[5]]
                        bikeStationInfo['Locality'] = test[0]['address']['value']['addressLocality']
                        bikeStationInfo['streetAdress'] = test[0]['address']['value']['streetAddress']
                        bikeStationInfo['numberBikeAvailable'] = test[0]['availableBikeNumber']['value']
        if tempValue != 100000:
            counterForColorInDeplacement = 0
            for j in déplacement:
                if printRouteOrNotBoolean[counterForColorInDeplacement]:
               
                    itineraire = createjson(j,
                                            str(number1),
                                            str(number2),
                                            str(coordinatesBikeClosest[0]),
                                            str(coordinatesBikeClosest[1]))
                    newCoordinates = []
                    for i in range(len(itineraire['routes'][0]['geometry']['coordinates'])):
                        newCoordinates.append([])
                        newCoordinates[i] = []
                        newCoordinates[i].append(float(itineraire['routes'][0]['geometry']['coordinates'][i][1]))
                        newCoordinates[i].append(float(itineraire['routes'][0]['geometry']['coordinates'][i][0]))


                    my_PolyLine = folium.PolyLine(locations = [newCoordinates], color= colorLine[counterForColorInDeplacement])
                    
                    my_PolyLine.add_to(m)
                    counterForColorInDeplacement += 1
            legend_html = """
    <div style="position: fixed;
                bottom: 50px; left: 50px; width: 150px; height: 130px;
                background-color: white;
                z-index:9999; font-size:14px;
                border:1px solid grey; padding: 10px;">
        <b>Legend</b><br>
        <i style="background: blue; color: blue;"> Bike = ;></i> bike <br>
        <i style="background: red; color: red;"> Bike = ;></i> driving <br>
        <i style="background: purple; color: purple;"> Bike = ;></i> Bus <br>
        <i style="background: green; color: green;"> Bike = ;></i> walking <br>
    </div>
"""
            legend2_html =f"""
        <div style="position: fixed;
                        bottom: 50px; right: 50px; width: 150px; height: 100px;
                        background-color: white;
                        z-index:9999; font-size:14px;
                        border:1px solid grey; padding: 10px;">
                <b>Bike Station</b><br>
                <i style="background: blue; color: white;">{bikeStationInfo.get('Locality')}</i><br>
                <i style="background: blue; color: white;">{bikeStationInfo.get('streetAdress')}</i><br>
                <i style="background: blue; color: white;"> Bikes : {str(bikeStationInfo.get('numberBikeAvailable'))}</i><br>
            </div>
        """
            
            st.components.v1.html(m.get_root().render() + legend_html + legend2_html, width= 700, height = 700)
            #st.components.v1.html(m._repr_html_(), width= 700, height = 700)
            




