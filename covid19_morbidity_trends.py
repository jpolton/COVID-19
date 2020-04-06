#!/usr/bin/env python
# coding: utf-8

# # Mapping in Python with geopandas
#
# Trying out geopandas to colour shapefile polygons by field values.
# Here load a UK county council boundary shape file and a table of COVID-19 confirmed cases and plot.
#
"""
Plot change against number
What does it look like without smoothing?
"""


import matplotlib.pyplot as plt # plotting
import matplotlib.cm as cm   # colormap functionality
#import matplotlib.colors as mcolors # make new colormap
#from matplotlib.dates import DateFormatter # format x-axis dates

#import os # make animation using system call "convert"
import datetime
import numpy as np
#import geopandas as gpd
import pandas as pd # read in CSV data

#import covid19_fns as c19



##########################################################################################################################
## Now do the main routine stuff
if __name__ == '__main__':

    url = 'https://raw.githubusercontent.com/emmadoughty/Daily_COVID-19/master/Data/COVID19_by_day.csv'
    mydateparser = lambda x: datetime.datetime.strptime(x, "%d/%m/%Y")
    covid = pd.read_csv(url,parse_dates=[0], date_parser=mydateparser)
    color = covid['Date'].dt.dayofweek

    plt.close('all')
    fig, (ax2, ax1) = plt.subplots(2,1, figsize=(8,8))
    lg = ax2.scatter(covid['CumDeaths'], covid['NewDeaths'], c=color,
        cmap=cm.get_cmap('PiYG', 7),
        vmin = -0.5, vmax = 6.5 )
    ax2.set_ylabel('New Deaths')
    ax2.set_xlabel('Cumulative Deaths')
    ax2.set_yscale('linear')
    ax2.set_xscale('linear')

    ax2.set_title('UK COVID19: New daily deaths vs total deaths coloured by reported day')

    ax1.scatter(covid['CumDeaths'], covid['NewDeaths'], c=color,
            cmap=cm.get_cmap('PiYG', 7),
            vmin = -0.5, vmax = 6.5 )
    ax1.set_ylabel('New Deaths')
    ax1.set_xlabel('Cumulative Deaths')
    ax1.set_yscale('log')
    ax1.set_xscale('log')
    ax1.set_ylim([10,1000])
    ax1.set_xlim([10,5000])


    # Make new subplot for colorbar
    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.85, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(lg, cax=cbar_ax, ticks=np.arange(0,7) )

    #cbar = fig.colorbar(lg, ax=ax1, ticks=np.arange(0,7) )
    cbar.set_ticklabels([ 'M','T','W','Th','F','Sa','Su'])


    sourceEDstr = 'compiled: github.com/emmadoughty/Daily_COVID-19'
    sourceGITstr = 'code: github.com/jpolton/COVID-19'
    # Set the font dictionaries (for plot title and axis titles)
    kw_source_label = {'fontname':'Arial', 'size':'6', 'color':'black', 'weight':'normal',
                'horizontalalignment': 'right', 'verticalalignment':'top'}
    kw_sourcegit_label = {'fontname':'Arial', 'size':'6', 'color':'black', 'weight':'normal',
                'horizontalalignment': 'left', 'verticalalignment':'top'}

    #ax1.text( ax1.get_xlim()[0], ax2.get_ylim()[1], sourceGITstr, **kw_sourcegit_label )
    #ax1.text( ax1.get_xlim()[1], ax2.get_ylim()[1], sourceEDstr, **kw_source_label )

    ax2.text( ax2.get_xlim()[0], ax2.get_ylim()[1], sourceGITstr, **kw_sourcegit_label )
    ax2.text( ax2.get_xlim()[1], ax2.get_ylim()[1], sourceEDstr, **kw_source_label )

    plt.show()
