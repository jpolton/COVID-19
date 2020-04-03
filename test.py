#!/usr/bin/env python
# coding: utf-8

# Test plotting regions from web links



from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes # inset plot
from mpl_toolkits.axes_grid1.inset_locator import mark_inset # inset plot

import matplotlib.pyplot as plt # plotting
import matplotlib.cm as cm   # colormap functionality
import matplotlib.colors as mcolors # make new colormap
import os # make animation using system call "convert"
import datetime
import numpy as np
import geopandas as gpd
import pandas as pd # read in CSV data

import covid19_fns as c19

class ReportingRegion_shp:

    #global covid

    data = None
    url_head = ["https://ons-inspire.esriuk.com/arcgis/rest/services/Administrative_Boundaries/Local_Authority_Districts_December_2019_Boundaries_UK_BUC/MapServer/0/query?where=UPPER(lad19cd)%20like%20'%25",
                "https://ons-inspire.esriuk.com/arcgis/rest/services/Administrative_Boundaries/Counties_December_2019_Boundaries_EN_BFC/MapServer/0/query?where=UPPER(cty19cd)%20like%20'%25",
                "https://ons-inspire.esriuk.com/arcgis/rest/services/Administrative_Boundaries/Counties_and_Unitary_Authorities_December_2019_Boundaries_UK_BUC2/MapServer/0/query?where=UPPER(ctyua19cd)%20like%20'%25",
                "https://ons-inspire.esriuk.com/arcgis/rest/services/Health_Boundaries/Local_Health_Boards_April_2019_Boundaries_WA_BUC/MapServer/0/query?where=UPPER(lhb19cd)%20like%20'%25"]
    url_key = ['lad19cd', 'cty19cd', 'ctyua19cd', 'lhb19cd']
    url_nam = ['lad19nm', 'cty19nm', 'ctyua19cd', 'lhb19nm']

    url_tail = "%25'&outFields=*&outSR=4326&f=json"

    def __init__(self, ONScode):
        self.ONScode = str(ONScode)
        #self.date_time = date_time
        #self.value = np.NaN

        # load ONScode geometry
        if self.ONScode[0].upper() == 'S':
            file = 'DATA/SG_NHS_HealthBoards_2019/SG_NHS_HealthBoards_2019.shp'
            shp = gpd.read_file(file).to_crs("EPSG:4326") # Lots of region (in degrees)
            self.shp = shp[ shp['HBCode'] == ONScode ] # extract one region
            # ONS code region name
            #self.name = self.shp.loc[ self.shp['HBCode'] == ONScode ].HBName.values[0]
            self.name = self.shp.HBName.values[0]

        elif self.ONScode[0].upper() == 'N':
            file = 'DATA/OSNI_Open_Data__Largescale_Boundaries__Local_Government_Districts_2012/OSNI_Open_Data__Largescale_Boundaries__Local_Government_Districts_2012.shp' # https://www.opendatani.gov.uk/dataset/osni-open-data-largescale-boundaries-local-government-districts-2012
            shp = gpd.read_file(file).to_crs("EPSG:4326") # Lots of region (in degrees)
            self.shp = shp[ shp['LGDCode'] == ONScode ] # extract one region
            # ONS code region name
            #self.name = self.shp.loc[ self.shp['LGDCode'] == ONScode ].LGDNAME.values[0]
            self.name = self.shp.LGDCode.values[0]

        else: # load from url API query
            url = ReportingRegion_shp.url_head[0] + self.ONScode + ReportingRegion_shp.url_tail
            print(url)
            self.shp = gpd.read_file(url)

            url_count = 0
            while self.shp.empty:
                url_count = url_count + 1
                print('url_count: ',url_count)
                url=ReportingRegion_shp.url_head[url_count] + self.ONScode + ReportingRegion_shp.url_tail
                self.shp = gpd.read_file(url).to_crs("EPSG:4326") # degrees
                if url_count == len(ReportingRegion_shp.url_head ):
                    print('count: {}, ONS code: {} not found'.format(url_count, self.ONScode))


            # ONS code region name
            self.name = self.shp[ReportingRegion_shp.url_nam[url_count]].values[0]
        self.shp.name = self.name
        self.shp.ONScode = self.ONScode

    def plot(self):
        self.shp.boundary.plot()
        plt.title(self.name)
        plt.show()

    def print(self):
        print(f"{self.ONScode} : {self.name}")


def add_value(data, region, date_time):
    """
    r[ONScode] = add_value(covid, r[ONScode] , date_time)
    """
    region.value = np.NaN

    # Find the valie for the date_time and ONScode
    region.value = data.loc[date_time, region.ONScode]
    if type(region.value) is str:
        region.value = int(region.value)
    region.shp['value'] = region.value # add a new column so plotting colour works

    return region




def load_tomwhite_covid_new():
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
    covid_raw = pd.read_csv(url,index_col=3,parse_dates=[0], date_parser=mydateparser)

    covid_raw['AreaCode'].replace('', np.nan, inplace=True)
    covid_raw.dropna(subset=['AreaCode'], inplace=True)

    #covid = covid.reset_index()
    covid = covid_raw.pivot(index='Date', columns='AreaCode', values='TotalCases' )
    #covid = covid.pivot(index='Date', columns='Area', values='TotalCases' )

    """
    ## Find rows where NaNs are lurking
    is_NaN = covid.isnull()
    row_has_NaN = is_NaN.any(axis=1); rows_with_NaN = covid[row_has_NaN]
    rows_with_NaN
    """

    return covid_raw, covid




def make_colormap(type='log', N=11):
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

    # Make a new colormap by adding colours together
    blu_cmap=plt.cm.get_cmap('Blues', (N+1) // 2 )
    red_cmap=plt.cm.get_cmap('Reds',  (N+1) // 2 )
    pla_cmap=plt.cm.get_cmap('plasma', N+1 )
    rnb_cmap=plt.cm.get_cmap('rainbow', N+1 )

    white_pal = np.array([[1., 1., 1., 1.]])
    #grey_pal = np.array([[.8, .8, .8, 1.]])

    ## stack colors together: Blue and Red
    #colors_new = np.vstack(( white_pal, blu_cmap(np.linspace(0.25, 0.75, 5)), red_cmap(np.linspace(0.25, 1, 5)) ))
    #colors_new = np.vstack(( white_pal, pla_cmap(np.linspace(1, 0, N)) ))
    #colors_new = np.vstack(( white_pal, rnb_cmap(np.linspace(0, 1, N)) ))
    colors_new = np.vstack(( rnb_cmap(np.linspace(0, 1, N)) ))

    # create new colormap
    my_cmap = mcolors.ListedColormap( colors_new )

    my_cmap.set_over('black')
    my_cmap.set_under('gray')

    return my_cmap



def find_max_in_region(geodf,region):
    """
    Find the largest cases value within a specified region and days list
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


    #print(boundary.geometry)
    return region_geodf.value.max() # Max over region




def snapshot_plot(geodf_final,geodf,date_time,region,maxval=20.):
    """
    NEED TO UPDATE

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
    datestrfname = date_time.strftime("%Y%m%d") # monotonic increasing number for days

    #sourcestr = 'data source: www.gov.uk/government/publications/coronavirus-covid-19-number-of-cases-in-england'
    sourcePHEstr = 'data source: www.gov.uk/government/publications/covid-19-track-coronavirus-cases'
    sourcePHWstr = 'phw.nhs.wales/news/public-health-wales-statement-on-novel-coronavirus-outbreak'
    sourceGoogstr = 'compiled: www.lpchong.com/post/covid19-confirmed-cases-in-england-by-upper-tier-local-authority-daily'
    sourceGITstr = 'code: github.com/jpolton/COVID-19'
    sourceDATAstr = 'data: github.com/tomwhite/covid-19-uk-data'

    # Set the font dictionaries (for plot title and axis titles)
    kw_source_label = {'fontname':'Arial', 'size':'6', 'color':'black', 'weight':'normal',
                'horizontalalignment': 'right', 'verticalalignment':'top'}
    kw_sourcegit_label = {'fontname':'Arial', 'size':'6', 'color':'black', 'weight':'normal',
                'horizontalalignment': 'left', 'verticalalignment':'top'}
    kw_date_label = {'fontname':'Arial', 'size':'16', 'color':'black', 'weight':'bold',
                'horizontalalignment': 'left', 'verticalalignment':'bottom'}

    # Make a colormap with ticks and labels for the given max value. Using a logscale
    #my_colormap, my_ticks, my_ticklabels = make_colormap2(maxval)

    N = 13 # Number of rectangular colorbar elements

    fig, ax = plt.subplots(1, 1) # dummy figure
    plt.rcParams['figure.figsize'] = (10.0, 6.0) # dummy figure

    fig, ax = plt.subplots(1, 1)
    plt.rcParams['figure.figsize'] = (10.0, 6.0)
    # plot the boundaries from a static datagrame (from final date)
    geodf_final.boundary.plot( ax=ax, linewidth=0.25, color='k' ) # make boundaries grey when there are more reported areas

    colorbar_extend_str = 'min'
    geodf.plot(column='value', ax=ax, legend=False,
            missing_kwds={'color': 'lightgray'},
            cmap=make_colormap(type='log',N=N),
            norm=mcolors.LogNorm(vmin=1, vmax=maxval) )



    # Edit and present colorbar
    axx=plt.gca()
    if region['name'] == 'London':
        orientation_str='horizontal'
        titlestr = 'COVID-19 total confirmed cases for London by local authority'
    elif region['name'] == 'Wales':
        titlestr = 'COVID-19 total confirmed cases for Wales by reporting region'
        orientation_str='vertical'
    elif region['name'] == 'Scotland':
        titlestr = 'COVID-19 total confirmed cases for Scotland by Health Board'
        orientation_str='vertical'
    elif region['name'] == 'NW':
        #titlestr = 'COVID-19 total confirmed cases for NW England and Wales by local authority'
        titlestr = 'COVID-19 total confirmed cases for NW England by local authority'
        orientation_str='vertical'
    else:
        #titlestr = 'COVID-19 total confirmed cases for England and Wales by local authority'
        titlestr = 'COVID-19 total confirmed cases by reporting district'
        orientation_str='vertical'

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
    cb.set_ticklabels( [str(i) for i in ticks] )

    ax.set_xlim(region['xlim'])
    ax.set_ylim(region['ylim'])

    ax.set_title(titlestr)
    ax.text(region['date_loc'][0], region['date_loc'][1], datestr, **kw_date_label)
    #ax.text(region['xlim'][1], region['ylim'][0], sourcePHEstr, **kw_source_label )
    #ax.text(region['xlim'][1], region['ylim'][0], sourcePHEstr+'\n'+sourceGoogstr, **kw_source_label )
    ax.text(region['xlim'][1], region['ylim'][0], sourceDATAstr, **kw_source_label )
    ax.text(region['xlim'][0], region['ylim'][0], sourceGITstr, **kw_sourcegit_label )

    ax.axis('off')


    if region['name'] == 'UK': # London zoom
        axins1 = zoomed_inset_axes(ax, zoom=4, bbox_to_anchor=(0,0.2,1,1),bbox_transform=ax.transAxes,loc='center right', axes_kwargs={'xticks':[], 'yticks':[]}) # shift anchor so inset is up a bit.
        axins2 = zoomed_inset_axes(ax, zoom=1, loc='upper left', axes_kwargs={'xticks':[], 'yticks':[]}) # shetland
        #axins = zoomed_inset_axes(ax, 4, loc='center right')
        geodf_lon = geodf[geodf['lad19cd'].str.contains("E09", na=False)] # datafrane for Greater London
        geodf_she = geodf_final[geodf_final['HBCode'].str.contains("S08000026", na=False)] # datafrane for Shetland
        minx1,miny1,maxx1,maxy1 = geodf_lon.geometry.total_bounds
        minx2,miny2,maxx2,maxy2 = geodf_she.geometry.total_bounds

        axins1.set_xlim(minx1, maxx1)
        axins1.set_ylim(miny1, maxy1)

        axins2.set_xlim(minx2, maxx2)
        axins2.set_ylim(miny2, maxy2)

        mark_inset(ax, axins1, loc1=2, loc2=4, fc="none", ec="0.5")
        #mark_inset(ax, axins2, fc="none", ec="0.5")

        ## Plot zoom window
        geodf_final.boundary.plot( ax=axins1, linewidth=0.1, color='k' ) # make boundaries grey when there are more reported areas
        geodf_final.boundary.plot( ax=axins2, linewidth=0.1, color='k' ) # make boundaries grey when there are more reported areas

        #r['S08000026'].shp.plot(ax= axins, edgecolor='black', color='white' )
        geodf_lon.plot(column='value', ax=axins1, legend=False,
                    missing_kwds={'color': 'lightgray'},
                    cmap=make_colormap(type='log',N=N),
                    norm=mcolors.LogNorm(vmin=1, vmax=maxval) )

        geodf_she.plot(column='value', ax=axins2, legend=False,
                    missing_kwds={'color': 'lightgray'},
                    cmap=make_colormap(type='log',N=N),
                    norm=mcolors.LogNorm(vmin=1, vmax=maxval) )

        plt.setp(axins1.get_xticklabels(), visible=False)
        plt.setp(axins1.get_yticklabels(), visible=False)
        plt.setp(axins2.get_xticklabels(), visible=False)
        plt.setp(axins2.get_yticklabels(), visible=False)

    #fig.tight_layout()
    fname = 'FIGURES/COVID-19_'+region['name']+'_'+datestrfname+'.png'
    print('Saving %s'%fname)
    plt.savefig(fname, dpi=150)

    return

def find_the_ONScodes_by_country(country_lst,data_raw):
    """
    INPUT:
        country_lst = ['England', 'Wales']. List of strings, name of country (string) in database.
        data - pandas table of data (Orgin: TomWhite. URL: https://github.com/tomwhite/covid-19-uk-data/blob/master/data/covid-19-cases-uk.csv)
    OUTPUT:
        ONScdes - array of ONScode strings

    ONScodes = find_the_ONScodes_by_country('Scotland',covid_raw)
    """
    count = 0
    for country_str in country_lst:
        count = count + 1
        codes = covid_raw.loc[covid_raw['Country'] == country_str].AreaCode.unique()
        if count == 1:
            ONScodes = codes
        else:
            #ONScodes.append(codes)
            ONScodes = np.hstack((codes,ONScodes))

    return ONScodes

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days) + 1):
        yield end_date - datetime.timedelta(n)

##########################################################################################################################
## Now do the main routine stuff
if __name__ == '__main__':

    # # Define Regions for plotting
    region_UK = {'name': 'UK', 'country_lst':['England','Wales','Northern Ireland','Scotland'],
                                'xlim':[-9,2], 'ylim':[50,60], 'date_loc':[-0.5, 59.] }
    region_Eng = {'name': 'EnglandWales',  'country_lst':['England','Wales'],
                                'xlim':[-6,2], 'ylim':[50,56], 'date_loc':[0, 55.5] }
    region_NW = {'name': 'NW',  'country_lst':['England','Wales'],
                                'xlim':[-3.4,-1.9], 'ylim':[52.8,53.9], 'date_loc':[-3.35, 53.8] }
    region_Lon = {'name': 'London',  'country_lst':['England'],
                                'xlim':[-0.6,0.5], 'ylim':[51.3,51.7], 'date_loc':[0.25,51.65] }
    region_Sco = {'name': 'Scotland', 'country_lst':['Scotland'],
                                'xlim':[-8,0.], 'ylim':[54,61], 'date_loc':[-7.95,59.5] }
    region_Wal = {'name': 'Wales', 'country_lst':['Wales'],
                                'xlim':[-5.5,-2.5], 'ylim':[51.25,53.5], 'date_loc':[-5.45,53.4] }
    region_NI = {'name': 'Northern Ireland', 'country_lst':['Northern Ireland'],
                                'xlim':[-9,-5], 'ylim':[54,55.5], 'date_loc':[-8.95, 55.4] }

    regions = [region_Eng, region_NW, region_Lon, region_Sco]
    regions = [ region_Eng]
    regions = [ region_NI]
    regions = [ region_UK]

    # Define the date range. Use 2-digit strings.
    #  These will be the column labels for the case data
    #  The COVID-19 source data has labels of the form 'dd/mm'
    #days = ['07', '08', '09', '10', '11', '12', '13', '14','15', '16']


country_lst = [region['country_lst'] for region in regions]
if len(regions) > 1:
    print('Need to update the country ONScodes are sought for if plotting multiple regions')

#days = [datetime.datetime(2020, 3, i) for i in range(7,31+1)]
#days = [datetime.datetime(2020, 3, i) for i in range(28,31+1)]
days = daterange(datetime.datetime(2020, 3, 7), datetime.datetime(2020, 4, 3) )

# load the raw COVID19 data
covid_raw, covid = load_tomwhite_covid_new()

# Extra the ONScodes for the region of interest
ONScodes = find_the_ONScodes_by_country(regions[0]['country_lst'],covid_raw)

if(0):
    # Define the polygon regions as class instanaces
    r = dict() # Store all the regions in a dictionary
    for i in range( len(ONScodes) ):
        ONScode = ONScodes[i]
        print('count: {}, ONScode: {}'.format(i,ONScode))
        r[ONScode] = ReportingRegion_shp( ONScode )


#date_time = datetime.datetime(2020,3,30)


# REVIEW:
df_final = None

for date_time in days: # reverse order

    gdf = None
    df = None

    for i in range( len(ONScodes) ):
        ONScode = ONScodes[i]
    #if name[0] != 'S': # Don't have the shape files for Scotland
        #print('count: {}, ONScode: {}'.format(i,ONScode))
        #r[ONScode] = ReportingRegion_shp( ONScode )
        r[ONScode] = add_value(covid, r[ONScode] , date_time)
        #r1.shp.plot(ax = ax, column='value' , legend=False, cmap = 'jet')
        r[ONScode].print()
        print('count:',i)
        if gdf is None:
            gdf = r[ONScode].shp
        else:
            gdf = gpd.GeoDataFrame( pd.concat([gdf, r[ONScode].shp]),  crs="EPSG:4326")


        # Take rows where value is not NaN
        df = gdf[gdf['value'].notna()]
        #df.reset_index(inplace=True)
        #df = df.to_crs("EPSG:4326") # degrees


    # Save the first (last) datafraem to plot the boundaries for all frames.
    try:
        if df_final == None:
            df_final = df
    except:
        pass

    for region in regions:
        maxval = find_max_in_region(df,region) # Find the max value to construct the colorscale
        print('maxval',maxval)
        maxval = max(maxval, 10)
        try:
            snapshot_plot(df_final,df,date_time,region,maxval)
        except:
            pass

    #plt.show()
    plt.close('all')


if len(days)>6:

    print('My imageMagick is broken, so to make an animated gif copy and paste:')
    print('convert -geometry 2048x2048 -loop 0 -delay 100 COVID-19_%s_??.png COVID-19_%s.gif'%(region['name'],region['name']))

print("convert -geometry 2048x2048 -loop 0 -delay 100 `ls -t COVID-19_UK*png` COVID-19_UK.gif")

        #covid = covid.pivot(index='Area', columns='Date', values='TotalCases' )


    # # Make regional plots for each day and each region
    #plot_panel(datetime.datetime(2020,3,8))
    #plot_frames_to_file(geodf,region_Eng,days)
