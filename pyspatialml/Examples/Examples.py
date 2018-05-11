from osgeo import gdal
from pyspatialml.sampling import extract
from pyspatialml.spectral import indices
from pyspatialml import predict
import geopandas as gpd
import rasterio
from rasterio import plot
import os
import matplotlib.pyplot as plt

# raster and vector input data
band1 = os.path.join('pyspatialml', 'Examples', 'lsat7_2000_10.tif')
band2 = os.path.join('pyspatialml', 'Examples', 'lsat7_2000_20.tif')
band3 = os.path.join('pyspatialml', 'Examples', 'lsat7_2000_30.tif')
band4 = os.path.join('pyspatialml', 'Examples', 'lsat7_2000_40.tif')
band5 = os.path.join('pyspatialml', 'Examples', 'lsat7_2000_50.tif')
band7 = os.path.join('pyspatialml', 'Examples', 'lsat7_2000_70.tif')

training_points = os.path.join('pyspatialml', 'Examples', 'landclass96_roi.shp')

# prepare virtual raster
predictors = [band1, band2, band3, band4, band5, band7]
vrt_file = os.path.join('pyspatialml', 'Examples', 'landsat.vrt')
outds = gdal.BuildVRT(
    destName=vrt_file, srcDSOrSrcDSTab=predictors, separate=True,
    resolution='highest', resampleAlg='bilinear')
outds.FlushCache()

# calculate spectral indices
spec_ind = indices(src=vrt_file, blue=0, green=1, red=2, nir=3, swir2=4, swir3=5)
ndvi = spec_ind.ndvi()

# read vector data
training_gpd = gpd.read_file(training_points)

# plotting
bounds = rasterio.open(vrt_file).bounds
plt.imshow(ndvi, extent=(bounds.left, bounds.right, bounds.bottom, bounds.top))
plt.scatter(x=training_gpd.bounds.iloc[:, 0], y=training_gpd.bounds.iloc[:, 1],
            s=2, color='black')
plt.show()

# extract training data
X, y, xy = extract(raster=vrt_file, response_gdf=training_gpd, field='id')

# classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_validate
clf = LogisticRegression()
clf.fit(X, y)
scores = cross_validate(clf, X, y, cv=3, scoring=['accuracy'])
scores['test_accuracy'].mean()

result = predict(estimator=clf, raster=vrt_file, file_path=os.path.join('pyspatialml', 'Examples', 'classification.tif'))
result = rasterio.open(os.path.join('pyspatialml', 'Examples', 'classification.tif'))
rasterio.plot.show(result)
result.close()

