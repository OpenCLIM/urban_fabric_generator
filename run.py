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

# Set up paths
data_path = os.getenv('DATA_PATH', '/data')
inputs_path = os.path.join(data_path, 'inputs')
outputs_path = os.path.join(data_path, 'outputs')
if not os.path.exists(outputs_path):
    os.mkdir(outputs_path)
buildings_path = os.path.join(outputs_path,'buildings')
if not os.path.exists(buildings_path):
    os.mkdir(buildings_path)


# run urban fabric generator tool
# make output dir if not exists
urban_fabric_raster = os.path.join(outputs_data, 'out_uf.asc')
subprocess.run(['generate_urban_fabric', '-i', '/data/inputs/data/out_cell_dph.asc', '-o', urban_fabric_raster])

print('*** Ran UFG ***')

# run raster to vector tool
subprocess.run(['raster_to_vector', '-i', '/data/outputs/data/out_uf.asc', '-o',
                os.path.join(buildings_path, "urban_fabric.gpkg"), '-f' 'buildings,roads,greenspace'])

# in an old version the data is stored in the wrong place. zip into a suitable output location
zipObj = ZipFile('/data/outputs/data/urban_fabric.zip', 'w')

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
