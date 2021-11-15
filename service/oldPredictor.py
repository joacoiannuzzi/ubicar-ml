# def place_filter_f(dataframe):
#     # dataframe = dataframe.drop(dataframe[(~dataframe.place.str.contains('Capital Federal', regex=True))].index)
#     # Obtenemos solo las zonas que tienen mas de 50 propiedades publicadas
#     # El uso de la columna property_type es indiferente. Solo necesito contar la cantidad de registros agrupados por lugar
#     df_zonas_count = dataframe.groupby(by='place').agg({'property_type': 'count'})
#
#     # Obtengo los nombres de las zonas
#     zonas_mayores_50 = df_zonas_count.loc[df_zonas_count['property_type'] > 50].index
#
#     # Obtengo solo las zonas con mas de 50 propiedades
#     dataframe = dataframe.loc[dataframe['place'].isin(zonas_mayores_50)]
#
#     return dataframe


# def preprocess(dataframe, place_filter=False):
#     if place_filter:
#         dataframe = place_filter_f(dataframe)
#
#     cols_to_remove = ['Unnamed: 0', 'id', 'surface_total', 'dAirport', 'dPort', 'dTrainStation', 'dHealthBuilding',
#                       'dPenitentiary', 'dRailway', 'dIndustrialArea', 'l1', 'l2', 'l3', 'id', 'start_date', 'end_date',
#                       'created_on', 'lat_x', 'lon_x', 'title', 'description', 'operation_type']
#
#     for c in cols_to_remove:
#         if c in dataframe:
#             del dataframe[c]
#
#     col_ohe_pTypes = pd.get_dummies(dataframe['property_type'], prefix='prop_type_')
#     col_ohe_places = pd.get_dummies(dataframe['place'], prefix='place_')
#
#     del dataframe['property_type']
#     del dataframe['place']
#
#     cols = ['dEducation', 'dFireStation', 'dSecureBuilding', 'dUniversity', ]
#
#     for geo in cols:
#         arr_geo = dataframe[geo]
#         arr_geo = arr_geo[:, None]
#         df_mul_geo = pd.DataFrame(arr_geo * col_ohe_places)
#         dataframe.drop(geo, axis=1, inplace=True)
#         for c in df_mul_geo.columns:
#             df_mul_geo.rename(columns={c: c + "_" + geo}, inplace=True)
#         dataframe = pd.concat([dataframe, df_mul_geo], axis=1)
#
#     # Obtengo el array de numpy de Superficies
#     arr_superficie = dataframe['surface_covered'].values
#
#     # La paso de 1 dimension a 2.
#     arr_superficie = arr_superficie[:, None]
#
#     # Obtengo el array de numpy de Superficies
#     # arr_rooms = dataframe['rooms'].values
#
#     # La paso de 1 dimension a 2.
#     # arr_rooms = arr_rooms[:, None]
#
#     # Calculo el producto de cada columna de lugar x la superficie para obtener una columna de superficie para cada lugar.
#     df_mul_places = pd.DataFrame(col_ohe_places * arr_superficie)
#
#     # Calculo el producto de cada tipo de propiedad x la superficie para obtener una columna de superficie para cada lugar.
#     df_mul_pTypes = pd.DataFrame(col_ohe_pTypes * arr_superficie)
#
#     # Calculo el producto de cada columna de lugar x la superficie para obtener una columna de superficie para cada lugar.
#     # Le agrego las nuevas columnas al datafra,e
#     dataframe = pd.concat([dataframe, df_mul_places, df_mul_pTypes], axis=1)
#
#     del dataframe['rooms']  # Lasso lo tira
#
#     return dataframe
