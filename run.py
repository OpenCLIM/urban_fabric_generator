import geopandas as gpd
import os
from shutil import copyfile
import subprocess
import datetime
from zipfile import ZipFile

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

# move files to output dir
result_data_dir = '/data/inputs'
output_data_dir = '/data/outputs/data'
buildings_data_dir = '/data/outputs/buildings'

# make output dir if not exists
os.makedirs(output_data_dir, exist_ok=True)
os.makedirs(buildings_data_dir, exist_ok=True)


# run urban fabric generator tool
# make output dir if not exists
build_type_ras = os.path.join(result_data_dir, 'out_cell_build_type.asc')
tile_type_ras = os.path.join(result_data_dir, 'out_cell_tile_type.asc')
urban_fabric_raster = os.path.join(output_data_dir, 'out_uf.asc')
tiles_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Tiles'))
#subprocess.run(['generate_urban_fabric', '-i', '/data/inputs/out_cell_dph_clip.asc', '-o', urban_fabric_raster])
subprocess.run(['ufg_fabric_from_coverage', '-ib', build_type_ras, 'it', tile_type_ras, '-of', urban_fabric_raster, '-tp', tiles_path])

print('*** Ran UFG ***')

# run raster to vector tool
subprocess.run(['raster_to_vector', '-i', '/data/outputs/data/out_uf.asc', '-o',
                os.path.join(buildings_data_dir, "urban_fabric.gpkg"), '-f' 'buildings,roads,greenspace'])

exit

# in an old version the data is stored in the wrong place. zip into a suitable output location
zipObj = ZipFile('/data/outputs/urban_fabric.zip', 'w')

print('searching for output')
for root, dirs, files in walk('/'):
    #print(root, files)
    for file in files:
        file_extension = file.split('.')[-1]
        if file_extension == 'gpkg':
            if 'buildings.gpkg' or 'roads.gpkg' or 'greenspace.gpkg' or 'urban_fabric.gpkg' in file:
                print(join(root, file))
                zipObj.write(join(root, file))
                os.remove(join(root, file))
zipObj.close()

# to save disk space, zip out_uf.asc and delete the raw file
zip_file(output_data_dir, 'out_uf.asc')

print('*** Ran R2V ***')
