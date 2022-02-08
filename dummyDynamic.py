import shapefile as shp  # Requires the pyshp package
import matplotlib.pyplot as plt

shapePath = "~/Downloads/ubicar/dynamic/polygon.shp"
plot = False

if (plot):
    sf = shp.Reader(shapePath)

    plt.figure()
    for shape in sf.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        plt.plot(x, y)
    plt.show()

if plot:
    sf = shp.Reader(shapePath)
