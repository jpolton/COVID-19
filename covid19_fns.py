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


def make_colormap(type='lin', N=11):
    """
    make a suitable colorbar
    If linear
        white = 0, 5 darkening blue then 5 darkening red. Then set_over=black.
        11 color blocks + one over block
    If log

    Useage:
    my_cmap = make_colormap() # returns a linear colormap for 11 colours
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

    if type == 'lin':
        # Make a new colormap by adding colours together
        blu_cmap=plt.cm.get_cmap('Blues', 6)
        red_cmap=plt.cm.get_cmap('Reds', 6)

        white_pal = np.array([[1., 1., 1., 1.]])
        #grey_pal = np.array([[.8, .8, .8, 1.]])

        ## stack colors together: White, Blue and Red
        colors_new = np.vstack(( white_pal, blu_cmap(np.linspace(0.25, 1, 5)), red_cmap(np.linspace(0.25, 1, 5)) ))

        # create new colormap
        my_cmap = mcolors.ListedColormap( colors_new )

        my_cmap.set_over('black')
        #my_cmap.set_under('white')
    elif type == 'log':
        # Make a new colormap by adding colours together
        blu_cmap=plt.cm.get_cmap('Blues', (N+1) // 2 )
        red_cmap=plt.cm.get_cmap('Reds',  (N+1) // 2 )

        white_pal = np.array([[1., 1., 1., 1.]])
        #grey_pal = np.array([[.8, .8, .8, 1.]])

        ## stack colors together: Blue and Red
        #colors_new = np.vstack(( blu_cmap(np.linspace(0.25, 0.75, 5)), red_cmap(np.linspace(0.25, 1, 5)) ))
        colors_new = np.vstack(( white_pal, blu_cmap(np.linspace(0.25, 0.75, 5)), red_cmap(np.linspace(0.25, 1, 5)) ))

        # create new colormap
        my_cmap = mcolors.ListedColormap( colors_new )

        my_cmap.set_over('black')
        my_cmap.set_under('white')

    return my_cmap


def single_frame_plot(geodf,date_time,region,maxval=20.):
    """
    Draw and save a map frame for a given day and region.
    Example usage:
        region_Lon = {'name': 'London',  'xlim':[-0.6,0.5], 'ylim':[51.2,51.8], 'date_loc':[0.2,51.75] }
        date_time = datetime.datetime(2020,3,5)
        maxval = 10.
        single_frame_plot(geodf,date_time,region_Lon,maxval)
    --> FIGURES/COVID-19_London_13.png
    """

    #datestr = daystr + " March"
    datestr = date_time.strftime("%a %d %b")  # datetime
    daystr =  date_time.strftime("%d")

    #sourcestr = 'data source: www.gov.uk/government/publications/coronavirus-covid-19-number-of-cases-in-england'
    sourcePHEstr = 'data source: www.gov.uk/government/publications/covid-19-track-coronavirus-cases'
    sourcePHWstr = 'phw.nhs.wales/news/public-health-wales-statement-on-novel-coronavirus-outbreak'
    sourceGoogstr = 'compiled: www.lpchong.com/post/covid19-confirmed-cases-in-england-by-upper-tier-local-authority-daily'
    sourceGITstr = 'code: github.com/jpolton/COVID-19'
    # Set the font dictionaries (for plot title and axis titles)
    kw_source_label = {'fontname':'Arial', 'size':'6', 'color':'black', 'weight':'normal',
                'horizontalalignment': 'right', 'verticalalignment':'top'}
    kw_sourcegit_label = {'fontname':'Arial', 'size':'6', 'color':'black', 'weight':'normal',
                'horizontalalignment': 'left', 'verticalalignment':'top'}
    kw_date_label = {'fontname':'Arial', 'size':'16', 'color':'black', 'weight':'bold',
                'horizontalalignment': 'left', 'verticalalignment':'bottom'}

    # Make a colormap with ticks and labels for the given max value. Using a logscale
    #my_colormap, my_ticks, my_ticklabels = make_colormap2(maxval)

    colormap_type = 'log' # 'lin' # 'log' WIP.
    N = 13 # Number of rectangular colorbar elements

    fig, ax = plt.subplots(1, 1) # dummy figure
    plt.rcParams['figure.figsize'] = (10.0, 6.0) # dummy figure

    fig, ax = plt.subplots(1, 1)
    plt.rcParams['figure.figsize'] = (10.0, 6.0)

    geodf.boundary.plot( ax=ax, linewidth=0.25, color='k' ) # make boundaries grey when there are more reported areas
    if colormap_type == 'lin':
        colorbar_extend_str = 'max'
        geodf.plot(column=date_time, ax=ax, legend=False,
                vmin=0, vmax=maxval,
                missing_kwds={'color': 'lightgray'},
                cmap=make_colormap() )
    elif colormap_type == 'log':
        colorbar_extend_str = 'min'
        geodf.plot(column=date_time, ax=ax, legend=False,
                missing_kwds={'color': 'lightgray'},
                cmap=make_colormap(type='log',N=N),
                norm=mcolors.LogNorm(vmin=1, vmax=maxval) )



    # Edit and present colorbar
    axx=plt.gca()
    if region['name'] == 'London':
        orientation_str='horizontal'
        titlestr = 'COVID-19 total confirmed cases for LONDON by local authority'
    elif region['name'] == 'NW':
        #titlestr = 'COVID-19 total confirmed cases for NW England and Wales by local authority'
        titlestr = 'COVID-19 total confirmed cases for NW England by local authority'
        orientation_str='vertical'
    else:
        #titlestr = 'COVID-19 total confirmed cases for England and Wales by local authority'
        titlestr = 'COVID-19 total confirmed cases for England by local authority'
        orientation_str='vertical'
    #if region['name'] == 'London':
    #    cb=plt.colorbar(axx.collections[1], extend=colorbar_extend_str, orientation='horizontal')
    #    cb.ax.set_xlabel('Number of confirmed cases')
    #else:
    #    cb=plt.colorbar(axx.collections[1], extend=colorbar_extend_str, orientation='vertical')
    #    cb.ax.set_ylabel('Number of confirmed cases')

    if colormap_type == 'log':
        # Find base such that int(base**(N-1) = maxval
        base = np.e**(np.log(maxval) /(N))
        ticks = [int(base**i) for i in range(N+2) ]
        ticks = list(set(ticks))
        ticks.sort()
        ticks = ticks[0:N+1]
        print('Ticks: ',ticks)

        cb=plt.colorbar(axx.collections[1], extend='max',
                                #norm=mcolors.LogNorm(vmin=0, vmax=maxval),
                                ticks=ticks,
                                boundaries=ticks,
                                spacing='proportional',
                                orientation=orientation_str)

        #cb.set_ticks(ticks)
        cb.set_ticklabels( [str(i) for i in ticks] )

    ax.set_xlim(region['xlim'])
    ax.set_ylim(region['ylim'])
    #ax.set_xlim([-6,2])
    #ax.set_ylim([50,56])

    ax.set_title(titlestr)
    ax.text(region['date_loc'][0], region['date_loc'][1], datestr, **kw_date_label)
    #ax.text(region['xlim'][1], region['ylim'][0], sourcePHEstr, **kw_source_label )
    ax.text(region['xlim'][1], region['ylim'][0], sourcePHEstr+'\n'+sourceGoogstr, **kw_source_label )
    ax.text(region['xlim'][0], region['ylim'][0], sourceGITstr, **kw_sourcegit_label )

    ax.axis('off')
    #fig.tight_layout()
    fname = 'FIGURES/COVID-19_'+region['name']+'_'+daystr+'.png'
    print('Saving %s'%fname)
    plt.savefig(fname, dpi=150)

    return



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



def load_shapefile_old():
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

    shp['merge'] = None
    # Join Hackney and City of London
    iHCoL = shp.index[ (shp['lad17nm'] == 'Hackney') | (shp['lad17nm'] == 'City of London')  ].tolist()
    shp.loc[ iHCoL, 'merge'] = 'HCoL'
    # Merge into a new geodf
    shp2 = shp.dissolve(by='merge')
    # Relable place names
    shp2 = shp2.replace('City of London', 'Hackney and City of London')
    # Tidy up and concat
    shp = shp.drop(iHCoL)
    shp3 = gpd.GeoDataFrame(pd.concat([shp,shp2], ignore_index=True), crs=shp.crs)

    # Set index to be the regional name
    shp3 = shp3.set_index('lad17nm')

    # Before plotting the data, first change the Coordinate Reference System to one that uses degrees, for plotting ease
    #imd = imd.to_crs("EPSG:3395") # metres
    shp3 = shp3.to_crs("EPSG:4326") # degrees
    #print(shp.crs)
    return shp3

def load_shapefile():
    """
    load Local Authorities Upper Tier shape file data.
    Do some merging and postprocessing to match COVID19 data as best as possible.
    Example usage of data:
    shp.lad19nm[shp.lad19nm == 'Wirral']
    """
    # Load shape file data
    shapefile = 'DATA/shapefile3/Counties_and_Unitary_Authorities_December_2017_Full_Clipped_Boundaries_in_UK.shp'
    # Read the data
    print('Load shapefile data from %s'%shapefile)
    shp = gpd.read_file(shapefile)
    shp['merge'] = None

    # A couple of regions need to be merged as the counts data is presented for joint regions.
    # Join Bournemout and Poole polygons. Find the indices
    iBCP = shp.index[ (shp['ctyua17nm'] == 'Bournemouth') | (shp['ctyua17nm'] == 'Poole')  ].tolist()
    shp.loc[ iBCP, 'merge'] = 'BCP' # Christchurch is missing from the shapefile and is in the Dorset polygon.
    # Join Cornwall and Scilly polygons. Find the indices
    iCIoS = shp.index[ (shp['ctyua17nm'] == 'Isles of Scilly') | (shp['ctyua17nm'] == 'Cornwall')  ].tolist()
    shp.loc[ iCIoS, 'merge'] = 'CIoS'
    # Join Hackney and City of London
    iHCoL = shp.index[ (shp['ctyua17nm'] == 'Hackney') | (shp['ctyua17nm'] == 'City of London')  ].tolist()
    shp.loc[ iHCoL, 'merge'] = 'HCoL'
    # Merge into a new geodf
    shp2 = shp.dissolve(by='merge')
    # Relable place names
    shp2 = shp2.replace('Bournemouth','Bournemouth, Christchurch and Poole')
    print('NB Christchurch region is folded into Dorset')
    shp2 = shp2.replace('Cornwall', 'Cornwall and Isles of Scilly')
    shp2 = shp2.replace('City of London', 'Hackney and City of London')
    # Tidy up and concat
    shp = shp.drop(iCIoS).drop(iBCP).drop(iHCoL)
    shp3 = gpd.GeoDataFrame(pd.concat([shp,shp2], ignore_index=True), crs=shp.crs)


    # Set index to be the regional name
    shp3 = shp3.set_index('ctyua17nm')

    # Before plotting the data, first change the Coordinate Reference System to one that uses degrees, for plotting ease.
    #  This is really slow
    #imd = imd.to_crs("EPSG:3395") # metres
    shp3 = shp3.to_crs("EPSG:4326") # degrees
    #print(shp.crs)
    return shp3


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
    fname = 'DATA/Covid-19/COVID19-UK - Summary.csv'
    #fname = 'DATA/Covid-19/COVID19-England - Summary.csv'
    print('Load COVID-19 data from %s'%fname)
    covid = pd.read_csv(fname).set_index('Unnamed: 0')
    # Relabel colums and convert to datetime object
    for col in covid.columns:
        #covid = covid.rename( columns={ col: col+'/2020'} )
        covid = covid.rename( columns={ col: datetime.datetime.strptime( "2020/"+col, "%Y/%d/%m")  } )
    #covid.columns = pd.to_datetime(covid.columns)
    covid.columns = pd.to_datetime(covid.columns)

    return covid


def load_tomwhite_covid():
    """
    load in CSV data for confirmed cases per day and region.
    load data from TomWhite GitHub:


    Date	Country	AreaCode	Area	TotalCases
    2020-03-05	England	E09000002	Barking and Dagenham	0

    Pivot the data to rows of placenames and columns of dates
    """

    url = 'https://raw.githubusercontent.com/tomwhite/covid-19-uk-data/master/data/covid-19-cases-uk.csv'
    print('Load COVID-19 data from %s'%url)

    mydateparser = lambda x: datetime.datetime.strptime(x, "%Y-%m-%d")
    covid = pd.read_csv(url,index_col=3,parse_dates=[0], date_parser=mydateparser)
    covid = covid.reset_index()
    covid = covid.pivot(index='Area', columns='Date', values='TotalCases' )
    covid = covid.drop('awaiting clarification').drop('Awaiting confirmation')
    try:
        covid = covid.drop('Resident outside Wales').drop('Residential area to be confirmed')
    except:
        pass
    # Drop first two date columns with incomplete data
    covid.drop(covid.columns[[0, 1]], axis=1, inplace=True)
    # Patch a data
    """
    ## Find rows where NaNs are lurking
    is_NaN = covid.isnull()
    row_has_NaN = is_NaN.any(axis=1); rows_with_NaN = covid[row_has_NaN]
    rows_with_NaN
    """

    covid.loc['Cornwall and Isles of Scilly']['2020-03-08'] = covid.loc['Cornwall']['2020-03-08'];  #  3 cases
    covid = covid.drop('Cornwall').drop('Isles of Scilly')

    covid.loc['Bournemouth, Christchurch and Poole']['2020-03-07'] = covid.loc['Poole']['2020-03-07']
    covid = covid.drop('Poole').drop('Bournemouth')

    covid.loc['Hackney and City of London']['2020-03-08'] = covid.loc['Hackney']['2020-03-08'];  #  3 cases
    covid = covid.drop('Hackney').drop('City of London')

    ## Remove Scotland for Now
    """
    rows_with_NaN

    Date                             2020-03-07 2020-03-08 2020-03-09 2020-03-10  ... 2020-03-13 2020-03-14 2020-03-15 2020-03-16
    Area                                                                          ...
    Borders                                 NaN        NaN        NaN        NaN  ...          3          5          7          7
    Dumfries and Galloway                   NaN        NaN        NaN        NaN  ...        NaN        NaN        NaN          1
    Highland                                NaN        NaN        NaN        NaN  ...        NaN          1          2          2
    Shetland                                NaN        NaN          2          2  ...          6         11         11         15
    """
    covid = covid.dropna().astype(int) # nasty nan's stopped the data being interpreted as int on reading in.
    return covid

def plot_logy_with_fit( days, val, label='label for legend', col='g', ndays=13):
    """
    plot the variable against time on logy axis
    Plot a straight line fit on logy axis
    ndays - last ndays to fit data to
    """

    idays = np.arange(len(days))

    plt.semilogy( days, val, 'o', label=label , color=col)

    p = np.polyfit(idays[-ndays::] , np.log( val[val.index[-ndays::]] ), 1)
    double_rate_str = '{0:3.1f}'.format(np.log(2)/p[0])
    plt.semilogy(days[val.index[-ndays::]], np.exp(p[0] * idays[-ndays::] + p[1]),
            '--', color=col, label='Fitted x2 rate = '+double_rate_str+' days')

    return plt


def load_tomwhite_uktotals():
    """
    load in CSV data for UK deaths.
    load data from TomWhite GitHub:

    Date	Tests	ConfirmedCases	Deaths
    2020-01-25	31	0	0

    totals = load_tomwhite_uktotals()
    Pivot the data to rows of placenames and columns of dates
    """

    url = 'https://raw.githubusercontent.com/tomwhite/covid-19-uk-data/master/data/covid-19-totals-uk.csv'
    print('Load COVID-19 data from %s'%url)

    mydateparser = lambda x: datetime.datetime.strptime(x, "%Y-%m-%d")
    totals = pd.read_csv(url,index_col=3,parse_dates=[0], date_parser=mydateparser)
    totals = totals.reset_index()
    #totals = totals.pivot(index='Area', columns='Date', values='TotalCases' )

    return totals


def load_geodataframe(days):
    """
    1. Load local authority boundary data in geopanda dataframe
    2. Load covid-19 confirmed cases by day bdy local authority data
    3. Add the confirmed cases data as new columns (per day) to the geopandas
    dataframe.

    Useage:
    days = ['07', '08', '09', '10', '11', '12', '13']
    geodf = load_geodataframe(days)
    geodf.loc['Wirral']
    """

    # Load local authority boundary shapefile data in a geodataframe
    if(1): #region['name'] == 'London': # use a shapefile that doesn't have the larger home counties in so that only Greater London (smaller regions) are plotted
        print('Using old shapefile, smaller regions')
        print('Hackney and City o L issue')
        geodf = load_shapefile_old()
    else:
        geodf = load_shapefile()

    # Load covid-19 confirmed cases by day bby local authority data
    covid = load_covid()
    #covid = load_tomwhite_covid()


    # Add the count to the boundary shapefile, as a new column
    print('Add COVID-19 data to geodataframe')
    #print('Assume the column headers are dates of the form 07/03')
    #for day in days:
        #geodf[day] = covid[day+'/03']    print('Assume the column headers are dates of the form 07/03')
    print('Assume the column headers are datetime entries')
    for day in days:
        geodf[day] = covid[day]

    return geodf

def plot_frames_to_file(geodf, regions, days):
    """
    days = ['07', '08', '09', '10', '11', '12', '13']
    regions = [ {'name': 'NW', 'xlim':[-3.4,-1.9], 'ylim':[52.8,53.9], 'date_loc':[-3.35, 53.8] } ]
    Useage:     plot_all_frames_to_file(geodf,regions,days)

    """
    for region in regions:

        files = []
        ofile = 'COVID-19_'+region['name']+'.gif'

        maxval = find_max_in_region(geodf,region,days) # Find the max value to construct the colorscale
        print('Max val %d'%maxval)

        for date_time in  days:
            daystr =  date_time.strftime("%d")
            single_frame_plot(geodf,date_time,region,maxval)
            files.append(ofile.replace('.gif','')+'_'+daystr+'.png')

        if len(days)>6:
            plt.close('all')

            print('My imageMagick is broken, so to make an animated gif copy and paste:')
            print('convert -geometry 2048x2048 -loop 0 -delay 100 COVID-19_%s_??.png COVID-19_%s.gif'%(region['name'],region['name']))

        # Make the animated gif and clean up the files
        #make_gif(files,ofile,delay=20)

        #for f in files:
        #    os.remove(f)

    return

def find_max_in_region(geodf,region,days):
    """
    Find the largest cases value within a specified region and days list
    days = ['07', '08', '09', '10', '11', '12', '13']
    region_Lon = {'name': 'London',  'xlim':[-0.6,0.5], 'ylim':[51.2,51.8], 'date_loc':[0.2,51.75] }
    maxval = find_max_in_region(geodf,region_Lon,days)
    """
    from shapely.geometry import Polygon # Find max in region

    ymin,ymax = region['ylim']
    xmin,xmax = region['xlim']
    lat_point_list = [ymin, ymax, ymax, ymin, ymin]
    lon_point_list = [xmin, xmin, xmax, xmax, xmin]

    polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
    # Define the region's boundary as a geodataframe (Coodinate Reference System in DEGREES)
    boundary_geodf = gpd.GeoDataFrame(index=[0], crs="EPSG:4326", geometry=[polygon_geom])

    # Now find the small polygons within this boundary
    region_mask = geodf.within(boundary_geodf.loc[0, 'geometry'])
    region_geodf = geodf.loc[region_mask]

    max_over_time_per_polygon = region_geodf[days].max(axis=1)

    #print(boundary.geometry)
    return max_over_time_per_polygon.max() # Max over time and region

def doubling(days,doubling_period):
    """
    calculate function that doubles every 'doubling_period' days
    fn(t+dt) = 2.fn(t), for doubling period dt.
    exp(alpha(t + dt)) = 2.exp(alpha.t)
    exp(alpha.dt) = 2
    dt = log 2 / alpha, where alpha is the slope of the straight line of the data in log space.

    If dt = 4 days, alpha = log2/4

    """
    nt = len(days)
    fn = np.zeros(nt)*np.NaN
    alpha = np.log(2)/doubling_period
    for i in range(1,nt):
        fn[i] = np.e**(i*alpha)
    return fn

def extract_timeseries(geodf,days):
    """
    Extract and plot the growth rates of reported cases
    """
    kw_source_label = {'fontname':'Arial', 'size':'6', 'color':'black', 'weight':'normal',
                'horizontalalignment': 'right', 'verticalalignment':'top'}
    kw_sourcegit_label = {'fontname':'Arial', 'size':'6', 'color':'black', 'weight':'normal',
                'horizontalalignment': 'left', 'verticalalignment':'top'}

    names = geodf.index

    nt = len(days)
    nn = len(names)
    time_series = np.zeros((nn,nt))*np.nan

    for n in range(nn): # over names
        for i in range(nt): # over days
            #day = days[i]
            time_series[n,i] = geodf.loc[names[n]][days[i]]

    # plot timeseries on log scale
    threshold_to_plot = 30 # activate plotting
    fig, ax = plt.subplots(1, 1)
    plt.rcParams['figure.figsize'] = (10.0, 6.0)
    for n in range(nn):
        if (time_series[n,-1]>threshold_to_plot) and (time_series[n,0]>1):
            plt.semilogy( days, time_series[n,:], label=names[n] )


    plt.semilogy(days, 5*doubling(days,2), 'k', linewidth=2, label='doubling rate = 2 day' )
    plt.semilogy(days, 5*doubling(days,3), 'k', linewidth=3, label='doubling rate = 3 days' )
    plt.semilogy(days, 5*doubling(days,5), 'k', linewidth=5, label='doubling rate = 5 days' )
    #plt.set_yscale('log')

    plt.legend(loc='best', # bbox_to_anchor=(-0.5, 0.95),
          ncol=2, fancybox=True, shadow=True)

    plt.xlabel('date')
    plt.title('Analysis of confirmed cases in England for 10 top regions')
    plt.ylabel('Total number of confirmed cases')
    #plt.legend(location='outer');

    sourcePHEstr = 'data source: www.gov.uk/government/publications/covid-19-track-coronavirus-cases'
    sourceGITstr = 'https://github.com/jpolton/COVID-19'

    plt.text(days[-1], 1, sourcePHEstr, **kw_source_label )
    plt.text(days[0], 1, sourceGITstr, **kw_sourcegit_label )


    fname = 'FIGURES/doubling_rate_England.png'
    print('Saving %s'%fname)
    plt.savefig(fname, dpi=150)


    return


def double_rate_uk_totals():
    totals = load_tomwhite_uktotals()

    sourceDATAstr = 'data: github.com/tomwhite/covid-19-uk-data'
    sourceGITstr = 'code: github.com/jpolton/COVID-19'

    # Set the font dictionaries (for plot title and axis titles)
    kw_sourcedata_label = {'fontname':'Arial', 'size':'8', 'color':'black', 'weight':'normal',
                'horizontalalignment': 'left', 'verticalalignment':'top'}
    kw_sourcegit_label = {'fontname':'Arial', 'size':'8', 'color':'black', 'weight':'normal',
                'horizontalalignment': 'right', 'verticalalignment':'top'}

    days = totals['Date']
    idays = np.arange(len(days))

    fig, ax = plt.subplots(1, 1)
    plt.rcParams['figure.figsize'] = (10.0, 6.0)

    plot_logy_with_fit( days, totals['Tests'], label='COVID-19 Tests', col='b', ndays=18)
    plot_logy_with_fit( days, totals['ConfirmedCases'], label='Confirmed Cases', col='g', ndays=18)
    plot_logy_with_fit( days, totals['Deaths'], label='Deaths', col='r', ndays=13)
    plt.xlim([datetime.datetime(2020,3,1), days[totals.index[-1]] ])
    plt.ylabel('Count')
    plt.xlabel('Date')
    plt.text(plt.gca().get_xlim()[0], plt.gca().get_ylim()[1], sourceGITstr, **kw_sourcedata_label )
    plt.text(plt.gca().get_xlim()[1], plt.gca().get_ylim()[1], sourceDATAstr, **kw_sourcegit_label )
    plt.title('COVID-19: Doubling rates for UK tests, confirmed cases and deaths')

    myFmt = DateFormatter("%d %b")
    ax.xaxis.set_major_formatter(myFmt)

    ## Rotate date labels automatically
    fig.autofmt_xdate()

    plt.legend()

    fname = 'FIGURES/uk_totals.png'
    print('Saving %s'%fname)
    plt.savefig(fname, dpi=150)

    plt.show()

    return
