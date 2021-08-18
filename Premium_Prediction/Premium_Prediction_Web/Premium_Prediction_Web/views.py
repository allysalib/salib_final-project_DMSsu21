from django.shortcuts import render
import pickle
import mysql.connector
import pandas as pd
import numpy as np
import datetime
import io

# our home page view
def home(request):    
    return render(request, 'index.html')


# custom method for generating predictions
def getPredictions(VaxStatus, Age, Smoke, Cases, Deaths, Vaccines):
    model = pickle.load(open('lr_model.sav', 'rb'))
    x_pred = [[VaxStatus, Age, Smoke, Cases, Deaths, Vaccines]]
    prediction = model.predict(x_pred)
    
    x = prediction[0][0]
    y = "${:.2f}".format(x)

    return y

# our result page view
def result(request):
    VaxStatus = int(request.GET['VaxStatus'])
    Age = int(request.GET['Age'])
    Smoke = int(request.GET['Smoke'])
    State = str(request.GET['State'])

    my_connect = mysql.connector.connect(
    host="34.74.58.178",
    user="root",
    passwd="DMSSUMMER2021",
    database="InsuranceData"
    )

    my_cursor = my_connect.cursor()

    my_cursor.execute("select distinct * from Covid")
    my_result = my_cursor.fetchone()
    covid_map = []
    while my_result is not None:
        covid_map.append(my_result)
        my_result = my_cursor.fetchone()

    covid_map_df = pd.DataFrame(covid_map, columns =['State', 'Cases', 'Deaths', 'Vaccines'])
    
    Cases = covid_map_df['Cases'].loc[covid_map_df['State'] == State].item()
    Deaths = covid_map_df['Deaths'].loc[covid_map_df['State'] == State].item()
    Vaccines = covid_map_df['Vaccines'].loc[covid_map_df['State'] == State].item()

    result = getPredictions(VaxStatus, Age, Smoke, Cases, Deaths, Vaccines)

    return render(request, 'result.html', {'result':result})