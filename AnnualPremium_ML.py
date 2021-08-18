#!/usr/bin/env python

import mysql.connector
import pandas as pd
import numpy as np
import datetime
import io
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import scale
from sklearn.model_selection import train_test_split

my_connect = mysql.connector.connect(
  host="34.74.58.178",
  user="root",
  passwd="DMSSUMMER2021",
  database="InsuranceData"
)

my_cursor = my_connect.cursor()

my_cursor.execute("select c.*, d.AnnualizedPremium, e.Cases, e.Deaths, e.Vaccines from (select a.*, b.ContractNumber from (select * from CustomerInfo) as a left join (select distinct ContractNumber, CustomerSSN_TIN from Contract where LineOfBusiness = 'AH') as b on a.SSN_TIN = b.CustomerSSN_TIN) as c left join (select distinct ContractNumber, AnnualizedPremium from ContractPremium) as d on c.ContractNumber = d.ContractNumber left join (select * from Covid) as e on c.CustState = e.State")
my_result = my_cursor.fetchone()
data = []
while my_result is not None:
    data.append(my_result)
    my_result = my_cursor.fetchone()
    
df = pd.DataFrame(data, columns =['SSN_TIN', 'DOB', 'State', 'VaxStatus', 'Smoke', 'ContractNumber', 'AnnualizedPremium', 'Cases', 'Deaths', 'Vaccines'])
df['DOB2'] = pd.to_datetime(df['DOB'])

def from_dob_to_age(born):
    today = datetime.date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

df['Age'] = df['DOB2'].apply(lambda x: from_dob_to_age(x))

x = df[['Age', 'VaxStatus', 'Smoke', 'Cases', 'Deaths', 'Vaccines']].fillna(0)
y = df[['AnnualizedPremium']].fillna(0)

xtrain, xtest, ytrain, ytest=train_test_split(x, y, test_size=0.15)

LR = LinearRegression().fit(xtrain, ytrain)

import pickle
pickle.dump(LR, open("lr_model.sav", "wb"))
