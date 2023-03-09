import geopandas as gpd
import os
import shutil
from shutil import copyfile
import subprocess
import glob
from glob import glob
import datetime
from zipfile import ZipFile
import math
from rasterio.crs import CRS
import rasterio as rio
import geopandas
import pandas as pd


from os import getenv, walk, mkdir, remove, listdir
from os.path import join, isdir, isfile

def zip_file(path, file):
    """
    Zips a file and deletes the un-archived version
    """
    zipObj = ZipFile(f'{join(path,file)}.zip', 'w')
    zipObj.write(join(path,file))

    zipObj.close()

    os.remove(join(path, file))
    return

def round_down(val, round_val):
    """Round a value down to the nearst value as set by the round val parameter"""
    return math.floor(val / round_val) * round_val


def round_up(val, round_val):
    """Round a value up to the nearst value as set by the round val parameter"""
    return math.ceil(val / round_val) * round_val


def round_bbox_extents(extents, round_to):
    """Round extents
    extents: a list of 4 values which are the 2 corners/extents of a layer
    rount_to: an integer value in base 0 in meters to round the extents too
    """
    print('^^^^^')
    print('In round bbox extents method.')
    print('Extents to round are: %s' %extents)
    print('Rounding to extents to: %s' %round_to)
    print('^^^^^')

    xmin = round_down(extents[0], round_to)
    ymin = round_down(extents[1], round_to)
    xmax = round_up(extents[2], round_to)
    ymax = round_up(extents[3], round_to)

    return [xmin, xmax, ymin, ymax]

# Set data paths
data_path = os.getenv('DATA_PATH','/data')
print(data_path)

# Input Paths
inputs_path = os.path.join(data_path, 'inputs')
boundary_path = os.path.join(inputs_path, 'boundary')
required_path = os.path.join(inputs_path,'required')
parameters_path = os.path.join(inputs_path,'parameters')

print(inputs_path)
if not os.path.exists(inputs_path):
    os.mkdir(inputs_path)

if not os.path.exists(required_path):
    os.mkdir(required_path)

outputs_path = os.path.join(data_path, 'outputs')
if not os.path.exists(outputs_path):
    os.mkdir(outputs_path)

outputs_path_data = os.path.join(data_path, 'outputs', 'data')
if not os.path.exists(outputs_path_data):
    os.mkdir(outputs_path_data)

parameter_file = glob(parameters_path + "/*.csv", recursive = True)
print('parameter_file:', parameter_file)

if len(parameter_file) == 1 :
    file_path = os.path.splitext(parameter_file[0])
    print('Filepath:',file_path)
    filename=file_path[0].split("/")
    print('Filename:',filename[-1])

    parameters = pd.read_csv(os.path.join(parameters_path + '/' + filename[-1] + '.csv'))
    ssp = str(parameters.loc[1][1])
    year = parameters.loc[2][1]

if len(parameter_file) == 0 :
    ssp = (os.getenv('SSP'))
    year = (os.getenv('YEAR'))

print('SSP:',ssp)
print('Year:',year)

if ssp != "baseline" :
    # Identify the name of the folder containing the zipped UDM documents  
    udm_data = glob(inputs_path + "/*.zip", recursive = True)
    file_path = os.path.splitext(udm_data[0])
    print('Filepath:',file_path)
    filename=file_path[0].split("/")
    print('Filename:',filename[-1])

    # Create a filepath to that folder
    udm_path = os.path.join(inputs_path, filename[-1])
    print('udm_path:',udm_path)

    # Identify input polygons and shapes (boundary of city, and OS grid cell references)
    boundary_1 = glob(boundary_path + "/*.*", recursive = True)
    print('clip:', boundary_1[0])
    dst1=os.path.join(udm_path, 'out_cell_build_type.asc')
    print('Input1:', dst1)
    dst2=os.path.join(udm_path, 'out_cell_dph.asc')
    print('Input2:', dst2)
    dst3=os.path.join(udm_path, 'out_cell_tile_type.asc')
    print('Input3:', dst3)
    raster_output_clip1 = os.path.join(required_path, 'out_cell_build_type_clip.tif')
    raster_output_clip1b = os.path.join(required_path, 'out_cell_build_type.asc')
    print('Output1:', raster_output_clip1)
    raster_output_clip2 = os.path.join(required_path, 'out_cell_dph_clip.tif')
    raster_output_clip2b = os.path.join(outputs_path, 'out_cell_dph_clip.asc')
    print('Output2:', raster_output_clip2)
    raster_output_clip3 = os.path.join(required_path, 'out_cell_tile_type_clip.tif')
    raster_output_clip3b = os.path.join(required_path, 'out_cell_tile_type.asc')
    print('Output3:', raster_output_clip3)

    print('Running raster clip')
    round_extents = 1000

    # read in shapefile
    t = gpd.read_file(boundary_1[0])
    # get bounding box for shapefile
    bounds = t.geometry.total_bounds

    if round_extents is not False:
        print('Rounding extents')
        print(bounds, round_extents)
        bounds = round_bbox_extents(bounds, round_extents)

    print('Using bounds:', bounds)
    # run clip
    print(dst1)
    print(raster_output_clip1)
    subprocess.run(["gdalwarp", "-te", str(bounds[0]), str(bounds[2]), str(bounds[1]), str(bounds[3]), dst1, raster_output_clip1,  "-t_srs", "EPSG:27700"])

    subprocess.run(["gdalwarp", "-te", str(bounds[0]), str(bounds[2]), str(bounds[1]), str(bounds[3]), dst2, raster_output_clip2, "-t_srs", "EPSG:27700"])

    subprocess.run(["gdalwarp", "-te", str(bounds[0]), str(bounds[2]), str(bounds[1]), str(bounds[3]), dst3, raster_output_clip3,  "-t_srs", "EPSG:27700"])


    subprocess.run(['gdal_translate', '-a_srs', 'EPSG:27700', raster_output_clip1, raster_output_clip1b])
    subprocess.run(['gdal_translate', '-a_srs', 'EPSG:27700', raster_output_clip2, raster_output_clip2b])
    subprocess.run(['gdal_translate', '-a_srs', 'EPSG:27700', raster_output_clip3, raster_output_clip3b])


    parameters_path = os.path.join(inputs_path,'parameters')

    if len(parameter_file) == 1 :
        file_path = os.path.splitext(parameter_file[0])
        print('Filepath:',file_path)
        filename=file_path[0].split("/")
        print('Filename:',filename[-1])

        src = parameter_file[0]
        print('src:',src)
        dst = os.path.join(outputs_path,filename[-1] + '.csv')
        print('dst,dst')
        shutil.copy(src,dst)
        
    # run urban fabric generator tool
    # make output dir if not exists
    build_type_ras = os.path.join(required_path, 'out_cell_build_type.asc')
    tile_type_ras = os.path.join(required_path, 'out_cell_tile_type.asc')
    urban_fabric_raster = os.path.join(outputs_path, 'data', 'out_uf.asc')
    #tiles_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Tiles'))
    #subprocess.run(['generate_urban_fabric', '-i', '/data/inputs/out_cell_dph_clip.asc', '-o', urban_fabric_raster])
    #subprocess.run(['ufg_fabric', '-ib', build_type_ras, 'it', tile_type_ras, '-of', urban_fabric_raster, '-tp', tiles_path])
    subprocess.run(['ufg_fabric', '-b', build_type_ras, '-t', tile_type_ras, '-f', urban_fabric_raster])

    print('*** Ran UFG ***')
    print(urban_fabric_raster,':',os.path.isfile(urban_fabric_raster))
    print('*** Going to run raster to vector ***')
    # run raster to vector tool
    subprocess.run(['raster_to_vector', '-i', '/data/outputs/data/out_uf.asc', '-o',
                    os.path.join(outputs_path, "urban_fabric.gpkg"), '-f' 'buildings,roads,greenspace'])

    # in an old version the data is stored in the wrong place. zip into a suitable output location
    zipObj = ZipFile(os.path.join(outputs_path, f'{ssp}-{year}-urban_fabric.zip'), 'w')

    print('searching for output')
    for root, dirs, files in walk('/data'):
        #print(root, files)
        for file in files:
            print(file)
            file_extension = file.split('.')[-1]
            if file_extension == 'gpkg':
                if file == 'buildings.gpkg' or file=='roads.gpkg' or file== 'greenspace.gpkg':
                    print(join(root, file))
                    os.chdir(root)
                    zipObj.write(file)
                    os.remove(file)
    zipObj.close()

    # to save disk space, zip out_uf.asc and delete the raw file
    # zip_file(output_data_dir, 'out_uf.asc')
    os.remove(join(outputs_path, 'data', 'out_uf.asc'))

    print('*** Ran R2V ***')
