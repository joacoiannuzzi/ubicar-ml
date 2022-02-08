# !pip install geopandas
# !pip install rtree
# !pip install pygeos
# !pip install pyshp
# !pip install matplotlib

import geopandas as gpd
import numpy as np
from geopandas import GeoDataFrame
import pandas as pd
import pyproj
from shapely.ops import linemerge, unary_union, polygonize, transform
from shapely.geometry import LineString, Polygon, Point, box, shape
from functools import partial
from matplotlib import pyplot as plt
from pyproj import Geod
from shapely import wkt, affinity

shapePath = "~/Downloads/ubicar/dynamic/polygon.shp"
propsPath = "~/Downloads/ubicar/dynamic/maxi-data-final.csv"

shapeDF = gpd.read_file(shapePath)
propsDf = pd.read_csv(propsPath)

# shapeDF = gpd.read_file("drive/MyDrive/Ubicar/ShapeFiles/Simplified/polygon.shp")
# propsDf = pd.read_csv('drive/MyDrive/Ubicar/CSV data/newData/maxi-data-final.csv')

propsDf['priceM2'] = propsDf.apply(lambda row: row.price / row.surface_total, axis=1)

geometry = [Point(xy) for xy in zip(propsDf.lon, propsDf.lat)]
propsGDF = GeoDataFrame(propsDf, crs="EPSG:4326",
                        geometry=geometry)  # GeoDataframe de las properties EPSG:4326 = ej -> -34, -54

propsGDF.to_crs(epsg=3857,
                inplace=True)  # lo convertimos a 3857. (misma transformacion que nuestro shape polygon, sirve para calcular el area)

# Division algo:

# 1 - Definir minima area para los poligonos.
# 2 - Por cada poligono, es decir por cada provincia, calcular primero el precio de m ^ 2(lat - long)
# 3 - hacer un split random del poligono y comparar el m ^ 2 de los nuevos splits.

def cut_polygon_by_line(polygon, line):  # cortamos el polygono.
    merged = linemerge([polygon.boundary, line])
    borders = unary_union(merged)
    polygons = polygonize(borders)
    return list(polygons)


def plot(shapely_objects, figure_path='fig.png'):  # Para plotear las casas
    from matplotlib import pyplot as plt
    import geopandas as gpd
    boundary = gpd.GeoSeries(shapely_objects)
    boundary.plot(
        color=['red', 'green', 'blue', 'yellow', 'yellow', 'red', 'green', 'blue', 'yellow', 'yellow', 'red', 'green',
               'blue', 'yellow', 'yellow'])
    plt.show()
    # plt.savefig(figure_path)


def calculateArea(gdf):
    gdf.to_crs(epsg=3395, inplace=True)
    return gdf.area[0] / 10 ** 6


def calculateAreainRespectToParent(parentShape, shapeAfterCut):
    gdfpoly1 = GeoDataFrame(geometry=[parentShape], crs="EPSG:3857")
    gdfpoly2 = GeoDataFrame(geometry=[shapeAfterCut], crs="EPSG:3857")
    AParent = calculateArea(gdfpoly1)
    ACut = calculateArea(gdfpoly2)
    res = (ACut * 100 / AParent)
    # print("res ",res)

    if (ACut * 100 / AParent < 25):  # Si por lo menos contiene un 25% respecto al padre, va
        return True
    else:
        return False


def polyFn(shape, resultingPolys, n, df_busqueda):
    # minx, miny, maxx, maxy = list(shape.bounds)
    # line = LineString([ Point(minx, (miny+maxy)/2), Point(maxx,(miny+maxy)/2)])

    plot(shape)
    exteriorCoords = list(
        shape.exterior.coords)  # each of this is a vertex point. So, our lines will have to start from this point towards another point.
    print(f"Exterior coords amount: {len(exteriorCoords)}")
    # We assign this first.
    maxX = exteriorCoords[0][0]
    maxY = exteriorCoords[0][1]
    minX = exteriorCoords[0][0]
    minY = exteriorCoords[0][1]

    for coords in exteriorCoords:
        if (coords[0] > maxX):
            maxX = coords[0]
        if (coords[1] > maxY):
            maxY = coords[1]
        if (coords[0] < minX):
            minX = coords[0]
        if (coords[1] < minY):
            minY = coords[1]

    # we assigned the maxiumum left and right, top and bottom vertices. So our cuts will be from the left to the top right, and from the bottom to top.

    for coords in exteriorCoords:  # a partir de cada vertice tenemos que hacer n cortes
        # Tenemos que calcular hacia que lado debemos partir el poligono, si la coordenada que estamos esta a la derecha del resto de las coordenadas, tenemos que splitear hacia la izquierda.
        # La altura maxima tambien debemos calcular ya que queremos que cambie la altura del corte. Si esta arriba tiene que cortar hacia abajo, o si esta abajo hacia arriba.

        valuesX = list(np.linspace(minX, maxX, num=n, endpoint=True))  # calculamos los valores de X
        valuesY = list(np.linspace(minY, maxY, num=n, endpoint=True))  # calculamos los valores de Y

        totalHousesInPoly, totalM2, df_busqueda_update = getHousesInPoly(shape, df_busqueda)
        pointCoords = Point(coords[0], coords[1])

        if (totalHousesInPoly > 20):
            for i in range(n):  # hacemos n cortes desde cada vertice
                if (coords[1] == minY and coords[0] != minX and coords[0] != maxX):
                    # if we cut from left to right and are in the bottom.
                    line = LineString([pointCoords, Point(valuesX[i], maxY)])
                    print("Cut 1")

                elif (coords[1] == maxY and coords[0] != minX and coords[0] != maxX):
                    # if we cut from left to right and are in the top.
                    line = LineString([pointCoords, Point(valuesX[i], minY)])
                    print("Cut 2")

                elif (coords[0] == minX and coords[1] != minY and coords[1] != maxY):
                    # if we cut from top to bottom and are in the left.
                    line = LineString([pointCoords, Point(maxX, valuesY[i])])
                    print("Cut 3")

                elif (coords[0] == maxX and coords[1] != minY and coords[1] != maxY):
                    # if we cut from top to bottom and are in the right.
                    line = LineString([pointCoords, Point(minX, valuesY[i])])
                    print("Cut 4")

                else:
                    # we shouldn't reach here but just in case, we cut by the diagonal
                    minx, miny, maxx, maxy = list(shape.bounds)
                    line = LineString([Point(minx, (miny + maxy) / 2), Point(maxx, (miny + maxy) / 2)])
                    print("Cut 5")

                split = cut_polygon_by_line(shape,
                                            line)  # Here comes the remaining polygons after the split, so split=[polys] which together form 'shape'
                if (calculateAreainRespectToParent(shape, split[0])):  # If we have somewhat a good cut.
                    plot(split)
                    for poly in split:  # remaining polygons after cut.
                        totalHousesAfterSplit, totalAfterSplitM2, df_busqueda_update_2 = getHousesInPoly(poly,
                                                                                                         df_busqueda_update)  # Calculate totalhousesAfterSplit, and totalM2AfterSplit (in a splitted polygon)
                        gdfpoly = GeoDataFrame(geometry=[poly], crs="EPSG:3857")
                        area = calculateArea(gdfpoly)
                        # print('area: ', area)
                        # print(df_busqueda_update_2)
                        if (
                                totalHousesAfterSplit >= 20 or area >= 1.0):  # If we have atleast 20 houses, or the area is greater= than 1
                            totalPercentageInPoly = totalHousesAfterSplit / totalHousesInPoly * 100  # We get the percentage of houses in polygon
                            if (calculateError(df_busqueda_update_2,
                                               df_busqueda_update)):  # calculamos si el error es mejor o no, si no lo es seguimos iterando
                                resultingPolys.append([poly, totalAfterSplitM2])  # save the poly and the m2
                                break;
                            else:
                                polyFn(poly, resultingPolys, n,
                                       df_busqueda_update_2)  # we have a meh polygon, keep splitting it.
                        else:
                            resultingPolys.append([shape, totalM2])  # add the parent poly.
                else:
                    break;  # bad cut, dont add and break loop.


def calculateError(df_HousesAfterSplit, df_HousesInParentPolygon):
    # Maxi error_calculation finding?
    # meanM2AfterSplit = getTotalM2(df_HousesAfterSplit)
    # meanM2BeforeSplit = getTotalM2(df_HousesInParentPolygon)

    std_error_before = np.std(df_HousesInParentPolygon['priceM2'], ddof=1) / np.sqrt(np.size(df_HousesInParentPolygon[
                                                                                                 'priceM2']))  # stdeviation del promedio de m2 / raiz(tamano de la cantidad de casas en ese promedio)
    std_error_after = np.std(df_HousesAfterSplit['priceM2'], ddof=1) / np.sqrt(np.size(df_HousesAfterSplit[
                                                                                           'priceM2']))  # stdeviation del promedio de m2 / raiz(tamano de la cantidad de casas en ese promedio)

    # print("eB ",std_error_before)
    # print("eA ",std_error_after)

    if (std_error_before >= std_error_after):
        return True  # Error se reduce
    else:
        return False  # error no se reduce, Seguimos iterando


def getTotalM2(df):
    size = len(df)
    meanM2 = df['priceM2'].sum() / size
    return meanM2


def getHousesInPoly(poly, df_busqueda):
    polygpd = GeoDataFrame(geometry=[poly], crs="EPSG:3857")
    joined = gpd.sjoin(df_busqueda, polygpd, how='left',
                       predicate='within')  # here we join the new df_busqueda with the poly if its within.
    joined = joined[joined['index_right'].notna()]  # drop those that are not within
    joined.drop(['index_right'], axis=1, errors='ignore',
                inplace=True)  # drop the added col so we can repeat the process
    size = len(joined)

    if (size >= 1):
        print(f"size {size}")
        meanM2 = joined['priceM2'].sum() / size
        # print(meanM2)
    else:
        meanM2 = 0
    return size, meanM2, joined


def setM2ForHousesInPoly(polyArray):
    poly = polyArray[0]
    m2 = polyArray[1]
    for j, pt in propsGDF.iterrows():
        if poly.contains(pt.geometry):
            propsGDF.loc[j, 'nearestM2'] = m2  # this is to set so we have to do itterrows...


# Plot all Argentina
def plotArgentina():
    plot(shapeDF.iloc[0].geometry)


def runMain():
    polyArray = []  # we need to save all the polygons as a tuple

    # for pos, poly in shapeDF.iterrows():
    #  minx, miny, maxx, maxy = list(poly.geometry.bounds)
    # line = LineString([ Point(minx, miny), Point(maxx,maxy)]) #se splitea por una linea diagonal (este es el primer split)
    # result = cut_polygon_by_line(poly.geometry, line)

    polyFn(shapeDF.iloc[0].geometry, polyArray, 4, propsGDF)

    # npArray = np.array(polyArray)
    # with open('/Downloads/ubicar/dynamic/array.txt', 'w') as f:
    #    np.savetxt(f, npArray)

    propsGDF['nearestM2'] = np.nan
    for poly in polyArray:
        setM2ForHousesInPoly(poly)

    propsDf = pd.DataFrame(propsGDF.drop(columns=['geometry', 'priceM2']))


propsDf.to_csv('~/Downloads/ubicar/dynamic/PostAlgoCasas.csv',
               index=False)  # Despues con este se hace el entrenado del modelo.

propsDf.describe()

propsDf['nearestM2']

propsDf.to_csv('Downloads/ubicar/dynamic/PostAlgoCasas_2.csv',
               index=False)  # Despues con este se hace el entrenado del modelo.