import os
import pandas as pd
import numpy as np
import sklearn
import sklearn.model_selection
import joblib
import sklearn.metrics
from sklearn.model_selection import train_test_split
from sklearn import metrics
import io
import pickle

from service.preprocess import preprocess
import xgboost as xgb
from xgboost import plot_importance

cwd = os.getcwd()

if __name__ == '__main__':
    cwd = '..'

model_path = f'{cwd}/model/XGB_sell_final_model.model'
columns_path = f'{cwd}/model/columns.joblib'
csvFile = f'{cwd}/csv/BsAs_withM2.csv'

model = xgb.XGBRegressor()
model.load_model(model_path)


# model = pickle.load(open(model_path, "rb"))
# model = joblib.load(model_path)
# cols = joblib.load(columns_path)


# surface_total,surface_covered,rooms,l2,l3,dRailway,dIndustrialArea,dAirport,dEducation,dFireStation,dHealthBuilding,dPenitentiary,dPort,dSecureBuilding,dTrainStation,dUniversity,property_type
# 270,220,5,Capital Federal,Palermo,68.18094605352108,17650.8529526008,3575.2659930816058,183.7490251249611,801.3807166376195,1003.3870439640796,5014.101495255802,7125.625596463275,1081.0891911105905,272.5637816612818,327.33186883943927,house

def predict(csv_string):
    # print(csv_string.encode("utf-8"))
    # print(csv_string.decode("utf-8"))

    x_valid = pd.read_csv(io.StringIO(csv_string), sep=",")

    print("x_valid")
    print(x_valid['lon'])
    print("x_valid")

    x_valid['place'] = x_valid['l2'] + x_valid['l3']

    allPropertiesDataframe = pd.read_csv(csvFile)
    print(allPropertiesDataframe.shape)
    # new_header = allPropertiesDataframe.iloc[0]  # grab the first row for the header
    # allPropertiesDataframe = allPropertiesDataframe[1:]  # take the data less the header row
    # allPropertiesDataframe.columns = new_header  # set the header row as the df header

    x_valid = preprocess(allPropertiesDataframe, x_valid)
    x_valid.drop(['lat', 'lon', 'price'], axis=1, inplace=True)
    # x_valid = x_valid.reindex(columns=cols, fill_value=0)
    # print("---- COEF ----")
    # print(get_df_coefs_values(model.coef_, cols, x_valid))
    print("--------------------")
    return model.predict(x_valid)


if __name__ == '__main__':
    # result = predict("a,lon,lat,surface_total,surface_covered,rooms,l2,l3,dRailway,dIndustrialArea,dAirport,dEducation,dFireStation,dHealthBuilding,dPenitentiary,dPort,dSecureBuilding,dTrainStation,dUniversity,dSubway,property_type\n0,-58.960,-34.60828,270,220,5,Buenos Aires,Pilar,68.18094605352108,17650.8529526008,3575.2659930816058,183.7490251249611,801.3807166376195,1003.3870439640796,5014.101495255802,7125.625596463275,1081.0891911105905,272.5637816612818,327.33186883943927,227.33186883943927,house")
    a = 'a,surface_total,surface_covered,rooms,l2,l3,lat,lon,price,dRailway,dIndustrialArea,dAirport,dEducation,dFireStation,dHealthBuilding,dPenitentiary,dPort,dSecureBuilding,dTrainStation,dUniversity,dSubway,property_type\n0,400,300,3,General Rodr\xedguez,Buenos Aires,-58.96011555213481,-34.608287657059115,100000,136.13328553881365,2710.387739005383,35069.62584015463,19.029504502812646,464.9455811473594,763.9281385286072,20902.30127024814,53664.347669430135,338.88138453648526,246.31482706072075,316.4748007067508,51931.537813973344,house'
    result = predict(a)

    print(result)
