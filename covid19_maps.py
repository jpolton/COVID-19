#!/usr/bin/env python
# coding: utf-8

# # Mapping in Python with geopandas
#
# Trying out geopandas to colour shapefile polygons by field values.
# Here load a UK county council boundary shape file and a table of COVID-19 confirmed cases and plot.
#
"""

## Data sources

* shapefiles:
- Local Authority Districts (December 2017) Super Generalised Clipped Boundaries in Great Britain ``https://geoportal.statistics.gov.uk/datasets/local-authority-districts-december-2017-super-generalised-clipped-boundaries-in-great-britain/geoservice`` (This effectively masks non-metropolitan regions in the PHE covid19 data, as they report over larger regions in the non-metropolitan places.)
- Local Authority Districts (December 2019) Boundaries UK BUC at 500m ``https://geoportal.statistics.gov.uk/datasets/local-authority-districts-december-2019-boundaries-uk-buc?geometry=-3.947%2C53.302%2C-0.591%2C53.872`` (This matches the PHE reporting regions for all but a couple of the reporting regions).


## Building a python environment

To get this to work I build a bespoke python environment:

conda create -n geo_env
conda activate geo_env
conda config --env --add channels conda-forge
conda config --env --set channel_priority strict
conda install python=3 geopandas jupyter matplotlib numpy seaborn pysal pandas

Then
conda activate geo_env


**author**: jpolton
**data**: 11 March 2020

**changelog**::

11 March: did it
12 March: add subregions
13 Mar: Broke ipython and spyder. Now just run as python script...
14 Mar: implement log scaling onto discrete integer values
16 Mar: generalise timestamp. Add Wales data.
"""



import matplotlib.pyplot as plt # plotting
import matplotlib.cm as cm   # colormap functionality
import matplotlib.colors as mcolors # make new colormap
from matplotlib.dates import DateFormatter # format x-axis dates

import os # make animation using system call "convert"
import datetime
import numpy as np
import geopandas as gpd
import pandas as pd # read in CSV data

import covid19_fns as c19
#%matplotlib inline
#get_ipython().run_line_magic('matplotlib', 'qt')


##########################################################################################################################
## Now do the main routine stuff
if __name__ == '__main__':
    print(__name__)
    # # Define Regions for plotting
    region_Eng = {'name': 'England', 'xlim':[-6,2], 'ylim':[50,56], 'date_loc':[0, 55.5] }
    region_NW = {'name': 'NW', 'xlim':[-3.4,-1.9], 'ylim':[52.8,53.9], 'date_loc':[-3.35, 53.8] }
    region_Lon = {'name': 'London',  'xlim':[-0.6,0.5], 'ylim':[51.3,51.7], 'date_loc':[0.25,51.65] }
    regions = [region_Eng, region_NW, region_Lon]

    # Define the date range. Use 2-digit strings.
    #  These will be the column labels for the case data
    #  The COVID-19 source data has labels of the form 'dd/mm'
    #days = ['07', '08', '09', '10', '11', '12', '13', '14','15', '16']

    days = [ datetime.datetime(2020,3,7),
                datetime.datetime(2020,3,8),
                datetime.datetime(2020,3,9),
                datetime.datetime(2020,3,10),
                datetime.datetime(2020,3,11),
                datetime.datetime(2020,3,12),
                datetime.datetime(2020,3,13),
                datetime.datetime(2020,3,14),
                datetime.datetime(2020,3,15),
                datetime.datetime(2020,3,16),
                datetime.datetime(2020,3,17),
                datetime.datetime(2020,3,18),
                datetime.datetime(2020,3,19),
                datetime.datetime(2020,3,20),
                datetime.datetime(2020,3,21),
                datetime.datetime(2020,3,22),
                datetime.datetime(2020,3,23),
                datetime.datetime(2020,3,24) ]

    geodf = c19.load_geodataframe(days)


    # # Make regional plots for each day and each region
    #plot_frames_to_file(geodf,regions,days) # All regions and all days
    #c19.plot_frames_to_file(geodf,[region_Eng],days) # A single region and all day
    c19.plot_frames_to_file(geodf,[region_Lon],days) # A single region and all day
    c19.plot_frames_to_file(geodf,[region_NW],days) # A single region and all day
    #c19.plot_frames_to_file(geodf,regions,[days[-1]]) # All regions, last day
    #plot_frames_to_file(geodf,[region_Lon],[days[-1]]) # All regions, last day

    #c19.plot_frames_to_file(geodf,[region_Lon],[datetime.datetime(2020,3,19)]) # A single region and day

    ## Plot the growth rate for reporting areas
    #extract_timeseries(geodf,days)

    ## Plot doubling rate of UK deaths
    #double_rate_uk_totals()
