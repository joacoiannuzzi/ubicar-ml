import gpxpy
import numpy as np
import pandas as pd


def obtener_barrio_privado(row_propiedad, barrios):
    # Aca voy a guardar la dictancia minima encontrada para esta propiedad
    distancia_minima = np.nan

    # Aca guardo el barrio con la distancia mínima para esta propiedad
    barrio_cercano = np.nan

    # Recorremos cada barrio y obtenemos la distancia entre la propiedad y el barrio.
    # Por cada barrio
    for i, barrio in barrios.iterrows():

        # Obtengo la distancia entre el barrio y la propiedad
        # def haversine_distance(latitude_1: float, longitude_1: float, latitude_2: float, longitude_2: float) -> float:
        # """
        # Haversine distance between two points, expressed in meters.
        # Implemented from http://www.movable-type.co.uk/scripts/latlong.html
        # """

        distancia = gpxpy.geo.haversine_distance(barrio['lat'], barrio['lon'], row_propiedad['lat'], row_propiedad[
            'lon'])  # vemos la latlon del barrio y la latlon de la propiedad., nos devuelve en metros la distancia

        # Si la distancia no es un nan
        if ~np.isnan(distancia):

            # Si la distancia anterior es nan o la distancia encontrada es menor que la distancia mínima encontrada anteriormente
            if (np.isnan(distancia_minima)) | (distancia < distancia_minima):
                # Asigno el barrio a la variable barrio_cercano
                barrio_cercano = barrio

                # Asigno la nueva distancia
                distancia_minima = distancia

    if (~np.isnan(distancia_minima)):
        # Le asigno el valor de distancia y barrio a la propiedad, teniendo en cuenta que si no encontró ninguna,
        # estos valores van a ser nan
        row_propiedad['distancia_barrio_privado'] = distancia_minima
        row_propiedad['nombre_barrio_privado'] = barrio_cercano['barrio']

    return row_propiedad


def barriosPrivados(prop):
    prop['distancia_barrio_privado'] = 0
    prop['sin_cercania_a_bp'] = 1
    prop['nombre_barrio_privado'] = 'None'
    # barrioPrivadoAux(df)
    #
    # # Asignamos el valor 0 a la columna 'distancia_barrio_privado',  1 a la columna sin_cercania_a_bp
    # # y 'None' a la columna nombre_barrio_privado
    # df.loc[
    #     (df['distancia_barrio_privado'].isnull()) |  # Si la columna distancia_barrio_privado es null
    #     (df['distancia_barrio_privado'] > 1000),  # O si la columna distancia barrio privado es mayor a 7
    #     ['distancia_barrio_privado', 'sin_cercania_a_bp', 'nombre_barrio_privado']] = [0, 1, 'None']
    #
    # # Le asignamos el valor None a la columna nombre_barrio_privado donde es mayor que 7 NULL
    # df.loc[(df['sin_cercania_a_bp'] == 1), 'nombre_barrio_privado'] = 'None'


def barrioPrivadoAux(df):
    # Cargamos el dataset de barrios privados.
    BARRIOS_PRIVADOS = pd.read_csv('drive/MyDrive/Ubicar/CSV data/barrios_privados_argentina_corrected.csv',
                                   encoding='latin1')
    BARRIOS_PRIVADOS['lat'] = BARRIOS_PRIVADOS['lat'].str.replace(',', '.').astype(float)
    BARRIOS_PRIVADOS['lon'] = BARRIOS_PRIVADOS['lon'].str.replace(',', '.').astype(float)
    df['distancia_barrio_privado'] = np.nan
    df['nombre_barrio_privado'] = np.nan
    # Obtengo las ciudades de los barrios
    ciudades_barrios_privados = BARRIOS_PRIVADOS['ciudad'].str.lower().unique()
    # Obtengo solo las propiedades que estan en las ciudades de los barrios privados Y QUE NO TENGAN LA DISTANCIA
    df_busqueda = df.loc[(df['distancia_barrio_privado'].isnull()) &  # Que aun no tengan la distancia
                         (~df['place'].isnull()) &  # Que tengan nombre de ciudad
                         (df['place'].str.lower().str.contains('|'.join(ciudades_barrios_privados)))
                         ].copy()
    print(len(df_busqueda), 'estan en ciudades de barrios privados')
    totalciudades = len(ciudades_barrios_privados)
    current = 1
    # por cada ciudad de los barrios
    for ciudad in ciudades_barrios_privados:

        # Obtengo los barrios de cada ciudad
        df_barrios = BARRIOS_PRIVADOS.loc[BARRIOS_PRIVADOS['ciudad'].str.lower() == ciudad.lower()].copy()

        # Obtengo las propiedades que son de esa ciudad
        df_props_ciudad = df_busqueda.loc[(df_busqueda['distancia_barrio_privado'].isnull()) &
                                          (~df_busqueda['place'].isnull()) &
                                          (df_busqueda['place'].str.lower().str.contains(ciudad.lower()))].copy()

        # Solo proceso si hay propiedades para esa ciudad.
        if (len(df_props_ciudad) > 0):
            print('Procesando ciudad', ciudad, '-', current, 'de', totalciudades, '-', len(df_props_ciudad),
                  'propiedades')

            # Recorremos cada propiedad y tratamos de obtener el barrio privado mas cercano a esa propiedad, basados en la ubicación.
            df_props_ciudad = df_props_ciudad.apply(obtener_barrio_privado, axis=1, barrios=df_barrios)

            # Actualizo los valores
            df_busqueda.update(df_props_ciudad)

            current = current + 1

            # Actulizo los valores del dataframe original con los del dataframe con los barrios
            df.update(df_busqueda)
    # Creamos la columna que indica que no está cerca de un barrio privado (bp)
    df['sin_cercania_a_bp'] = 0
