# Urban Fabric Generator on DAFNI
[![build](https://github.com/OpenCLIM/urban_fabric_generator/workflows/build/badge.svg)](https://github.com/OpenCLIM/urban_fabric_generator/actions)


## Description
This repository establishes a docker container for running the Urban Fabric Generator Model.

## Usage
The urban fabric can be generated directly during the UDM model. However, for large spatial areas, creating the building and green space polygons is both
computationally time consuming and the output files are large. Therefore this second, stand alone model was created to generate urban fabric files from the
outputs of the UDM model, with the option for the user to clip the output raster file for the location of interest.

### Running this container
`docker run --name urbanfabricgenerator -v <your local path>/data:/data/inputs/data -t urbanfabricgenerator`

Outputs from the UDM model are currently written to the same directory.
