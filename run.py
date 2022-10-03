import os
from shutil import copyfile
import subprocess
import datetime
from zipfile import ZipFile

# run UDM
subprocess.run(['python', '-m',  'openudm', '/data/inputs'])
print('*** Ran UDM ***')

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


def find_files():
    """
    Search all directories for any input files
    """

    suitable_extension_types = ['asc', 'tiff', 'geotiff', 'gpkg', 'csv']

    input_files = []

    for root, dirs, files in walk('/data'):
        print(root, files)
        for file in files:

            # check if extension acceptable
            #extension = file.split('.')[-1]
            #if extension in suitable_extension_types:
                # file is good and what we are looking for
            input_files.append(join(file))

    print(input_files)
    return input_files

print('*** Output files ***')
print(find_files())


# move files to output dir
result_data_dir = '/data/inputs'
output_data_dir = '/data/outputs/data'
buildings_data_dir = '/data/outputs/buildings'

# make output dir if not exists
os.makedirs(output_data_dir, exist_ok=True)

# copy the listed output files to the output location
files_to_copy = ['out_cell_dev.asc', 'out_cell_pph.asc', 'out_cell_dph.asc', 'out_cell_suit.asc', 'out_cell_overflow.csv']
for file_name in files_to_copy:
    copyfile(os.path.join(result_data_dir, file_name), os.path.join(output_data_dir, file_name))

print('*** Moved UDM output files ***')

# run urban fabric generator tool
# make output dir if not exists
os.makedirs(buildings_data_dir, exist_ok=True)
urban_fabric_raster = os.path.join(output_data_dir, 'out_uf.asc')
subprocess.run(['generate_urban_fabric', '-i', '/data/outputs/data/out_cell_dph.asc', '-o', urban_fabric_raster])

print('*** Ran UFG ***')

# run raster to vector tool
subprocess.run(['raster_to_vector', '-i', '/data/outputs/data/out_uf.asc', '-o',
                os.path.join(buildings_data_dir, "urban_fabric.gpkg"), '-f' 'buildings,roads,greenspace'])

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
