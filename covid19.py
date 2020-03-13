#!/usr/bin/env python
# coding: utf-8

# # Mapping in Python with geopandas
#
# Trying out geopandas to colour shapefile polygons by field values.
# Here load a UK county council boundary shape file and a table of COVID-19 confirmed cases and plot.
#
# Data sources:
# * shapefile: ``https://geoportal.statistics.gov.uk/datasets/local-authority-districts-december-2017-super-generalised-clipped-boundaries-in-great-britain/geoservice``
# * public health england: ``https://www.gov.uk/government/publications/coronavirus-covid-19-number-of-cases-in-england/coronavirus-covid-19-number-of-cases-in-england``
#
# Might also look at for following for tabulated, in time, data:
# * ``https://github.com/emmadoughty/Daily_COVID-19/blob/master/COVID19_by_LA.csv``
# * ``https://docs.google.com/spreadsheets/d/129bJR5Mgcr5qOQNc96CBWKFfjODToWKRiVKDEg5ybkU/edit#gid=1952384968``
#
#
# To get this to work I build a bespoke python environment:
#
#
# `conda create -n geo_env
# conda activate geo_env
# conda config --env --add channels conda-forge
# conda config --env --set channel_priority strict
# conda install python=3 geopandas jupyter matplotlib numpy seaborn pysal pandas
# `
#
# Then
# ``conda activate geo_env``
#
#
# Or, trying the following to get Spyder working
# conda create --override-channels -c conda-forge -n covid19 python=3 geopandas jupyter matplotlib numpy seaborn pysal pandas spyder
# conda activate covid19
#
# But this didn;t work for me :-(
#
# **author**: jpolton
#
# **data**: 11 March 2020
#
# **changelog**::
#
# 11 March: did it
# 12 March: add subregions
# 13 Mar: Broke ipython and spyder. Now just run as python script...

# From: https://www.gov.uk/government/publications/covid-19-track-coronavirus-cases
#
# Now have UTLA cases table:
# https://www.arcgis.com/home/item.html?id=b684319181f94875a6879bbc833ca3a6


import matplotlib.pyplot as plt # plotting
import matplotlib.cm as cm   # colormap functionality
import matplotlib.colors as mcolors # make new colormap
import os # make animation using system call "convert"

import numpy as np
import geopandas as gpd
import pandas as pd # read in CSV data

#%matplotlib inline
#get_ipython().run_line_magic('matplotlib', 'qt')

## FUNCTIONS
############################################################################

def plot_panel(ax,daystr):
    """
    Basic panel plotting as geopandas does not do subplot nicely. Might be good
    for a N plus delta-N plot...

    Example usage:
        fig, (ax1, ax2, ax3) = plt.subplots(ncols=3, sharex=True, sharey=True)
        plot_panel(ax1,'10')
        plot_panel(ax2,'11')
        plot_panel(ax3,'12')
    """
    if ax==ax3:
        bool_val = True
    else:
        bool_val = False
    shp.boundary.plot( ax=ax, linewidth=0.5 )
    shp.plot(column=daystr, ax=ax, legend=bool_val, missing_kwds={'color': 'lightgray'},
                 vmin=0, vmax=11 ,cmap=make_colormap() )
    ax.set_xlim([-4,0])
    ax.set_ylim([52,55])
    ax.set_xlabel('longitude (deg)')
    ax.set_ylabel('latitude (deg)')
    ax.set_title(daystr + "March")

    return


def make_colormap():
    """
    make a suitable colorbar
    white = 0, darkening blue then darkening red. 11 colors

    Useage:
    my_cmap = make_colormap()
    """
    # ##

    # Make a new colormap by adding white to the end of an exisiting colormap
    if(0): # colormap from tab10
        tmp_cmap = cm.get_cmap('tab10')
        colors_orig = tmp_cmap(np.linspace(0, 1, 10))

        # swap some colors around
        colors_orig[[0, 7],:] = colors_orig[[7, 0],:]
        colors_orig[0,:] = [0.9 , 0.9, 1. , 1.]

        white_pal = np.array([[1., 1., 1., 1.]]) # For zero values on the end of colormap
        #grey_pal = np.array([[.8, .8, .8, 1.]])

        #print(colors_orig)
        #print(white_pal)

        ## stack colors together
        colors_new = np.vstack(( white_pal, colors_orig ))  # from tab10

        # create new colormap
        my_cmap = mcolors.ListedColormap( colors_new )

    # Make a new colormap by adding colours together
    blu_cmap=plt.cm.get_cmap('Blues', 6)
    red_cmap=plt.cm.get_cmap('Reds', 6)

    white_pal = np.array([[1., 1., 1., 1.]])
    #grey_pal = np.array([[.8, .8, .8, 1.]])

    ## stack colors together: White, Blue and Red
    colors_new = np.vstack(( white_pal, blu_cmap(np.linspace(0.25, 1, 5)), red_cmap(np.linspace(0.25, 1, 5)) ))

    # create new colormap
    my_cmap = mcolors.ListedColormap( colors_new )

    return my_cmap


def single_frame_plot(daystr,region):
    """
    Draw and save a map frame for a given day and region.
    Example usage:
        region_Lon = {'name': 'London',  'xlim':[-0.6,0.5], 'ylim':[51.2,51.8], 'date_loc':[0.2,51.75] }
        daystr = '13'
        single_frame_plot(daystr,region)
    --> FIGURES/COVID-19_London_13.png
    """

    datestr = daystr + " March"
    titlestr = 'COVID-19 confirmed cases by local authority (England)'
    sourcestr = 'data source: www.gov.uk/government/publications/coronavirus-covid-19-number-of-cases-in-england'

    # Set the font dictionaries (for plot title and axis titles)
    kw_source_label = {'fontname':'Arial', 'size':'6', 'color':'black', 'weight':'normal',
                'horizontalalignment': 'right', 'verticalalignment':'top'}
    kw_date_label = {'fontname':'Arial', 'size':'16', 'color':'black', 'weight':'bold',
                'horizontalalignment': 'left', 'verticalalignment':'bottom'}


    fig, ax = plt.subplots(1, 1)
    plt.rcParams['figure.figsize'] = (10.0, 6.0)

    geodf.boundary.plot( ax=ax, linewidth=0.25, color='k' ) # make boundaries grey when there are more reported areas
    geodf.plot(column=daystr, ax=ax, legend=False,
                missing_kwds={'color': 'lightgray'},
                  vmin=0, vmax=11 ,cmap=make_colormap() )
    # Edit and present colorbar
    axx=plt.gca()
    cb=plt.colorbar(axx.collections[1])
    cb.ax.set_ylabel('Number of confirmed cases')

    ax.set_xlim(region['xlim'])
    ax.set_ylim(region['ylim'])
    #ax.set_xlim([-6,2])
    #ax.set_ylim([50,56])

    ax.set_title(titlestr)
    ax.text(region['date_loc'][0], region['date_loc'][1], datestr, **kw_date_label)
    #ax.text(1.9, 50.0, sourcestr, **kw_label )
    ax.text(region['xlim'][1], region['ylim'][0], sourcestr, **kw_source_label )

    ax.axis('off')
    #fig.tight_layout()
    fname = 'FIGURES/COVID-19_'+region['name']+'_'+daystr+'.png'
    print('Saving %s'%fname)
    plt.savefig(fname, dpi=1000)

    return

def edit_colourbar():
    """
    Manipulate the colorbar
    Not used yet. Will probably implement as the colorbar is an issue
    """
    fig, ax = plt.subplots(1, 1)
    plt.rcParams['figure.figsize'] = (10.0, 6.0)

    shp.boundary.plot( ax=ax, linewidth=0.25, color='k' ) # make boundaries grey when there are more reported areas
    shp.plot(column=daystr, ax=ax, legend=False, missing_kwds={'color': 'lightgray'},
              vmin=0, vmax=11 ,cmap=make_colormap() )

    axx=plt.gca()
    plt.colorbar(axx.collections[1], )


    cb=plt.colorbar(axx.collections[1])

    cb.ax.set_ylabel('Number of confirmed cases')




def widgets_thing():
    """
    Aim to use widgets to control view date. Not tested.
    """
    import ipywidgets as widgets

    start_date_str = '07'
    end_date_str = '11'

    start_date = int(start_date_str)
    end_date = int(end_date_str)

    # Vary the day with a slider
    selection_date_slider = widgets.IntSlider(
        min=start_date,max=end_date,value=end_date-start_date+1,
        continuous_update=False,
        description='date',
        orientation='horizontal',
        layout={'width': '600px'}
    )

    widgets.interact(
        single_frame_plot,
        daystr=str(selection_date_slider)
    );


def make_gif(files,output,delay=100, repeat=True,**kwargs):
    """
    Uses imageMagick to produce an animated .gif from a list of
    picture files.
    """
    os.system('convert -geometry 2048x2048 -delay %d -loop 0 %s %s'%(delay," ".join(files),output))
    return



def load_shapefile():
    """
    load Local Authorities Upper Tier shape file data
    Example usage of data:
    shp.lad17nm[shp.lad17nm == 'Wirral']
    """
    # Load shape file data
    shapefile = 'DATA/shapefile/Local_Authority_Districts_December_2017_Super_Generalised_Clipped_Boundaries_in_Great_Britain.shp'

    # Read the data
    print('Load shapefile data from %s'%shapefile)
    shp = gpd.read_file(shapefile)

    # Set index to be the regional name
    shp = shp.set_index('lad17nm')

    # Before plotting the data, first change the Coordinate Reference System to one that uses degrees, for plotting ease
    #imd = imd.to_crs("EPSG:3395") # metres
    shp = shp.to_crs("EPSG:4326") # degrees
    #print(shp.crs)

    return shp



def load_covid():
    """
    load in CSV data for confirmed cases per day and region

    load in the field data with a column of place names and columns for values, each day.
    Set the place names to the be index so they can be easily added as a new column to the boundary shapefile
    """
    # When I used the confirmed cases file that I managed:
    #covid = pd.read_csv(dir+'Covid-19/Merged-Table.csv').set_index('GSS_NM')

    # Source Google docs: https://docs.google.com/spreadsheets/d/129bJR5Mgcr5qOQNc96CBWKFfjODToWKRiVKDEg5ybkU/edit#gid=1952384968
    # I export as CSV and manually trim unwanted fields at the bottom. I also don't use the first date column with non-integer values
    # Region names header is empty --> "Unnamed: 0" to set this as the data index
    fname = 'DATA/Covid-19/COVID19-England - Summary.csv'
    print('Load COVID-19 data from %s'%fname)
    covid = pd.read_csv(fname).set_index('Unnamed: 0')

    return covid


def load_geodataframe(days):
    """
    1. Load local authority boundary data in geopanda dataframe
    2. Load covid-19 confirmed cases by day bdy local authority data
    3. Add the confirmed cases data as new columns (per day) to the geopandas
    dataframe.

    Useage:
    days = ['07', '08', '09', '10', '11', '12', '13']
    geodf = add_to_geodataframe(days)
    """

    # Load local authority boundary shapefile data in a geodataframe
    geodf = load_shapefile()

    # Load covid-19 confirmed cases by day bby local authority data
    covid = load_covid()


    # Add the count to the boundary shapefile, as a new column
    print('Add COVID-19 data to geodataframe')
    print('Assume the column headers are dates of the form 07/03')
    for day in days:
        geodf[day] = covid[day+'/03']

    return geodf

def plot_frames_to_file(regions, days):
    """
    days = ['07', '08', '09', '10', '11', '12', '13']
    regions = [ {'name': 'NW', 'xlim':[-3.4,-1.9], 'ylim':[52.8,53.9], 'date_loc':[-3.35, 53.8] } ]
    Useage:     plot_all_frames_to_file(regions,days)

    """
    for region in regions:

        files = []
        ofile = 'COVID-19_'+region['name']+'.gif'
        for daystr in  days:

            single_frame_plot(daystr,region)
            files.append(ofile.replace('.gif','')+'_'+daystr+'.png')

            if len(days)>10:
                plt.close('all')


        # Make the animated gif and clean up the files
        #make_gif(files,ofile,delay=20)

        #for f in files:
        #    os.remove(f)

    return

##########################################################################################################################
## Now do the main routine stuff
if __name__ == '__main__':

    # # Define Regions for plotting
    region_Eng = {'name': 'England', 'xlim':[-6,2], 'ylim':[50,56], 'date_loc':[0, 55.5] }
    region_NW = {'name': 'NW', 'xlim':[-3.4,-1.9], 'ylim':[52.8,53.9], 'date_loc':[-3.35, 53.8] }
    region_Lon = {'name': 'London',  'xlim':[-0.6,0.5], 'ylim':[51.2,51.8], 'date_loc':[0.2,51.75] }
    regions = [region_Eng, region_NW, region_Lon]

    # Define the date range. Use 2-digit strings.
    #  These will be the column labels for the case data
    #  The COVID-19 source data has labels of the form 'dd/mm'
    days = ['07', '08', '09', '10', '11', '12', '13']

    geodf = load_geodataframe(days)


    # # Make regional plots for each day and each region
    #plot_frames_to_file(regions,days) # All regions and all days
    #plot_frames_to_file([region_NW],['13']) # A single region and day
    plot_frames_to_file(regions,[days[-1]]) # All regions, last day

    plt.show()
