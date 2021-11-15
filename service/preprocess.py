import gpxpy.geo
import numpy as np
import pandas as pd


# Funcion que nos permite definir si una propiedad está ubicada dentro de un barrio privado
def obtener_m2(propiedadSeleccionada, propiedades):
    # print(propiedadSeleccionada)
    # print("-----------------------")
    nearPropsPrice = []
    propsIndex = []
    count = 0

    # todas las props con distancia menor a 1000
    # sacar promedio
    # devolver nearestM2

    # Aca voy a guardar la dictancia minima encontrada para esta propiedad
    distancia_minima = np.nan

    # Recorremos cada propiedad en la zona y obtenemos la distancia entre la propiedad seleccionada
    # y las propiedades de la zona.
    for i, propiedad in propiedades.iterrows():
        # print("--------------")
        # print(propiedad)
        # print(propiedad['lat'], propiedad['lon'])
        # print("--------------")
        # print(propiedadSeleccionada)
        # print(propiedadSeleccionada['lat'], propiedadSeleccionada['lon'])
        # Obtengo la distancia entre la seleccionada y la propiedades
        distancia = gpxpy.geo.haversine_distance(propiedad['lat'], propiedad['lon'], propiedadSeleccionada['lat'],
                                                 propiedadSeleccionada['lon'])
        # vemos la latlon del barrio y la latlon de la propiedad, nos devuelve en metros la distancia
        # Si la distancia no es un nan
        if ~np.isnan(distancia):
            # Si la distancia ES MENOR A 1000, agregamos al array el precio.
            if (distancia < 1000):
                print(propiedad['lat'], propiedad['lon'])
                print("DISTANCIA MENOR A 1000")
                propsIndex.append(i)
                nearPropsPrice.append(
                    propiedad['price'] / propiedad['surface_total'])  # precio / sup_total => precio * m^2
                count = count + 1

    if count <= 0:
        m2 = propiedadSeleccionada['price'] / propiedadSeleccionada['surface_total']
        print("No hay casas cercas")
    else:
        m2 = sum(nearPropsPrice) / count  # sacamos el total del precio / total de propiedades

    if (len(propsIndex) > 1):
        for idx in propsIndex:
            propiedades.loc[idx, 'nearestM2'] = m2
    return m2


def preprocess(dataframe, propDataFrame):
    # for i, propiedad in dataframe.iterrows():  # we'll have to check all properties.
    #     if (np.isnan(propiedad['nearestM2'])):
    #         df_busqueda = dataframe.loc[(~dataframe['departamento_nombre'].isnull()) &  # Que tengan nombre de ciudad
    #                                     (dataframe['departamento_nombre'].str.lower().str.fullmatch(
    #                                         propiedad['departamento_nombre'], case=False))]
    #         dataframe.loc[i, 'nearestM2'] = obtener_m2(propiedad, df_busqueda)

    propDataFrame.loc['nearestM2'] = obtener_m2(propDataFrame, dataframe)

    cols_to_remove = ['Unnamed: 0', 'id', 'lat', 'lon', 'departamento_id', 'departamento_nombre', 'municipio_id',
                      'municipio_nombre', 'provincia_id', 'provincia_nombre', 'dAirport', 'dPort', 'dTrainStation',
                      'dHealthBuilding', 'dPenitentiary', 'l1', 'l2', 'l3', 'id', 'start_date', 'end_date',
                      'created_on', 'lat_x', 'lon_x', 'title', 'description', 'operation_type']

    for c in cols_to_remove:
        if c in propDataFrame:
            del propDataFrame[c]

    # Barrio privado default
    propDataFrame['distancia_barrio_privado'] = 0
    propDataFrame['sin_cercania_a_bp'] = 1
    propDataFrame['nombre_barrio_privado'] = 'None'
    # finish

    col_ohe_pTypes = pd.get_dummies(propDataFrame['property_type'], prefix='prop_type_')
    col_ohe_places = pd.get_dummies(propDataFrame['place'], prefix='place_')
    col_ohe_barrioPriv = pd.get_dummies(propDataFrame['nombre_barrio_privado'], prefix='barrio_')

    del propDataFrame['property_type']
    del propDataFrame['place']
    del propDataFrame['nombre_barrio_privado']

    cols = ['dEducation', 'dFireStation', 'dSecureBuilding', 'dUniversity', 'dRailway', 'dIndustrialArea']
    for geo in cols:
        arr_geo = propDataFrame[geo]
        arr_geo = arr_geo[:, None]
        df_mul_geo = pd.DataFrame(arr_geo * col_ohe_places)
        propDataFrame.drop(geo, axis=1, inplace=True)
        for c in df_mul_geo.columns:
            df_mul_geo.rename(columns={c: c + "_" + geo}, inplace=True)
        propDataFrame = pd.concat([propDataFrame, df_mul_geo], axis=1)

    # Obtengo el array de numpy de Superficies
    arr_superficie = propDataFrame['surface_covered'].values

    # La paso de 1 dimension a 2.
    arr_superficie = arr_superficie[:, None]

    # Obtengo el array de numpy de Superficies
    # arr_rooms = propDataFrame['rooms'].values

    # La paso de 1 dimension a 2.
    # arr_rooms = arr_rooms[:, None]

    # df_mul_rooms_pType= pd.DataFrame(col_ohe_pTypes * arr_rooms)

    # Calculo el producto de cada columna de lugar x la superficie para obtener una columna de superficie para cada lugar.
    df_mul_places = pd.DataFrame(col_ohe_places * arr_superficie)

    df_mul_barrio = pd.DataFrame(col_ohe_barrioPriv * arr_superficie)  # superficie de barrio privado

    # Calculo el producto de cada tipo de propiedad x la superficie para obtener una columna de superficie para cada lugar.
    df_mul_pTypes = pd.DataFrame(col_ohe_pTypes * arr_superficie)

    # Calculo el producto de cada columna de lugar x la superficie para obtener una columna de superficie para cada lugar.
    # Le agrego las nuevas columnas al dataFrame
    # df_mul_barrio
    propDataFrame = pd.concat([propDataFrame, df_mul_places, df_mul_pTypes, df_mul_barrio], axis=1)

    # Agrego las columnas que estan en el dataframe de todas las propiedades pero no en el de la propiedad que busco la info
    propDataFrame[dataframe.columns.difference(propDataFrame.columns)] = 0
    propDataFrame.drop(propDataFrame.columns.difference(dataframe.columns), axis=1, inplace=True)
    propDataFrame = propDataFrame[dataframe.columns]

    return propDataFrame
