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
# conda install -c conda-forge descartes
#
# **author**: jpolton
# 
# **data**: 11 March 2020
# 
# **changelog**::
# 
# 11 March: did it
# 12 March: add subregions

# From: https://www.gov.uk/government/publications/covid-19-track-coronavirus-cases
# 
# Now have UTLA cases table:
# https://www.arcgis.com/home/item.html?id=b684319181f94875a6879bbc833ca3a6

# In[1]:


import matplotlib.pyplot as plt # plotting
import matplotlib.cm as cm   # colormap functionality
import matplotlib.colors as mcolors # make new colormap
import os # make animation using system call "convert"

import numpy as np
import geopandas as gpd
#import pysal as ps
import pandas as pd # read in CSV data


# In[2]:


#%matplotlib inline
#get_ipython().run_line_magic('matplotlib', 'qt')


# In[ ]:





# In[3]:


# Load spatial data


# In[4]:

root_dir = ''
root_dir = '/Users/jeff/GitHub/COVID-19/'
#root_dir = '/work/jelt/'

dir = root_dir + 'DATA/COVID-19/'

bdy_shp = root_dir + 'DATA/shapefile/Local_Authority_Districts_December_2017_Super_Generalised_Clipped_Boundaries_in_Great_Britain.shp'

# In[5]:


# Read the data
bdy = gpd.read_file(bdy_shp)

# Example usage to recover a region
bdy.lad17nm[bdy.lad17nm == 'Wirral']
# Set index to be the regional name
bdy = bdy.set_index('lad17nm')


# # load in CSV data
# 
# load in the field data with columns of place names and values. Set the place names to the be index so they can be easily added as a new column to the boundary shapefile
# 
# Expecting CSV data with columns: ``Upper Tier Local Authority`` and an integer date

# In[11]:


# My files
#covid = pd.read_csv(dir+'Covid-19/Merged-Table.csv').set_index('GSS_NM')


# In[12]:


# Google docs: https://docs.google.com/spreadsheets/d/129bJR5Mgcr5qOQNc96CBWKFfjODToWKRiVKDEg5ybkU/edit#gid=1952384968
#covid = pd.read_csv(dir+'Covid-19/COVID19-England - Summary.csv').set_index('Unnamed: 0')
covid = pd.read_csv(root_dir + 'DATA/Covid-19/COVID19-England - Summary.csv').set_index('Unnamed: 0')

# Have to trim unwanted fields at the bottom


# In[13]:

# Add the count to the boundary shapefile, as a new column

start_date_str = '07'
end_date_str = '12'

start_date = int(start_date_str)
end_date = int(end_date_str)

for day in np.arange(start_date, end_date+1):
    bdy[str(day).zfill(2)] = covid[str(day).zfill(2)+'/03']


# # Make plot
# Plot the data. First change the Coordinate Reference System to one that uses degrees, for plotting ease

# In[15]:


#imd = imd.to_crs("EPSG:3395") # metres
bdy = bdy.to_crs("EPSG:4326") # degrees
bdy.crs


# ## make a suitable colorbar

# In[16]:


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


# In[17]:


# Make a new colormap by adding colours together
blu_cmap=plt.cm.get_cmap('Blues', 6)
red_cmap=plt.cm.get_cmap('Reds', 6)

white_pal = np.array([[1., 1., 1., 1.]])
#grey_pal = np.array([[.8, .8, .8, 1.]])

## stack colors together
# White, Blue and Red
colors_new = np.vstack(( white_pal, blu_cmap(np.linspace(0.25, 1, 5)), red_cmap(np.linspace(0.25, 1, 5)) ))

# create new colormap
my_cmap = mcolors.ListedColormap( colors_new )


# In[ ]:





# # Three panel plot
# 

# In[17]:


def plot_panel(ax,daystr):
    if ax==ax3:
        bool_val = True
    else:
        bool_val = False
    bdy.boundary.plot( ax=ax, linewidth=0.5 )                    
    bdy.plot(column=daystr, ax=ax, legend=bool_val, missing_kwds={'color': 'lightgray'},              vmin=0, vmax=11 ,cmap=my_cmap )
    ax.set_xlim([-4,0])
    ax.set_ylim([52,55])
    ax.set_xlabel('longitude (deg)')
    ax.set_ylabel('latitude (deg)')
    ax.set_title(daystr + "March")

fig, (ax1, ax2, ax3) = plt.subplots(ncols=3, sharex=True, sharey=True)

plot_panel(ax1,'10')
plot_panel(ax2,'11')
plot_panel(ax3,'12')


# # Large single frame plot

# In[18]:


region = {'name': 'England', 'xlim':[-6,2], 'ylim':[50,56], 'date_loc':[0, 55.5] }
#region = {'name': 'NW', 'xlim':[-3.4,-1.9], 'ylim':[52.8,53.9], 'date_loc':[-3.35, 53.8] }
region = {'name': 'London',  'xlim':[-0.6,0.5], 'ylim':[51.2,51.8], 'date_loc':[0.2,51.75] }



def single_frame_plot(daystr,region=region):
    
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

    bdy.boundary.plot( ax=ax, linewidth=0.25, color='k' ) # make boundaries grey when there are more reported areas                    
    bdy.plot(column=daystr, ax=ax, legend=False, missing_kwds={'color': 'lightgray'},              vmin=0, vmax=11 ,cmap=my_cmap )
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
    plt.savefig(fname, dpi=1000)

    return

daystr = '11'
single_frame_plot(daystr)
#plt.close('all')


# In[19]:


plt.close('all')


# In[ ]:


# Or, using the function


# In[88]:


fig, ax3 = plt.subplots(1, 1)
plot_panel(ax3,'11') # If ax=ax3 it will plot a colorbar


# # Make movie

# In[29]:


def make_gif(files,output,delay=100, repeat=True,**kwargs):
    """
    Uses imageMagick to produce an animated .gif from a list of
    picture files.
    """

    os.system('convert -geometry 2048x2048 -delay %d -loop 0 %s %s'%(delay," ".join(files),output))
    
region = {'name': 'England', 'xlim':[-6,2], 'ylim':[50,56], 'date_loc':[0, 55.5] }

files = []
ofile = 'COVID-19_'+region['name']+'.gif'
for daystr in  ['07', '08', '09', '10', '11', '12']:
    
    single_frame_plot(daystr, region)
    files.append(ofile.replace('.gif','')+'_'+daystr+'.png')


# Make the animated gif and clean up the files
make_gif(files,ofile,delay=20)

#for f in files:
#    os.remove(f)


# In[ ]:





# In[ ]:





# In[30]:


plt.close('all')


# # Make regional plot

# In[62]:


region = {'name': 'England', 'xlim':[-6,2], 'ylim':[50,56], 'date_loc':[0, 55.5] }
region = {'name': 'NW', 'xlim':[-3.4,-1.9], 'ylim':[52.8,53.9], 'date_loc':[-3.35, 53.8] }
region = {'name': 'London',  'xlim':[-0.6,0.5], 'ylim':[51.2,51.8], 'date_loc':[0.2,51.75] }


files = []
ofile = 'COVID-19_'+region['name']+'.gif'
for daystr in  ['07', '08', '09', '10', '11', '12']:
    
    single_frame_plot(daystr,region)
    files.append('COVID-19_'+region['name']+'_'+daystr+'.png')



# In[ ]:





# In[31]:


# Manipulate the colorbar
fig, ax = plt.subplots(1, 1)
plt.rcParams['figure.figsize'] = (10.0, 6.0)

bdy.boundary.plot( ax=ax, linewidth=0.25, color='k' ) # make boundaries grey when there are more reported areas                    
bdy.plot(column=daystr, ax=ax, legend=False, missing_kwds={'color': 'lightgray'},          vmin=0, vmax=11 ,cmap=my_cmap )


axx=plt.gca()
plt.colorbar(axx.collections[1], )



# In[32]:


cb=plt.colorbar(axx.collections[1])

cb.ax.set_ylabel('Number of confirmed cases')


# In[ ]:





# In[ ]:





# In[ ]:





# # Widgets

# In[ ]:


import ipywidgets as widgets


# In[ ]:


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


# In[ ]:


widgets.interact(
    single_frame_plot,
    daystr=str(selection_date_slider)
);

