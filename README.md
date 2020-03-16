 # Track the UK spread of COVID-19: Mapping in Python with geopandas

The motivation was to learn how to do geospatial data handling and plotting in Python,
here [geopandas](https://geopandas.org). COVID-19 confirmed cases by region seemed like a suitable dataset to learn on. But perhaps to many the image outputs are of more interest than the methods used...

## Summary animations: Daily confirmed cases 7th-15th March

![Daily confirmed cases 7th-15th March](https://github.com/jpolton/COVID-19/blob/master/FIGURES/COVID-19_England.gif)

![Daily confirmed cases 7th-15th March](https://github.com/jpolton/COVID-19/blob/master/FIGURES/COVID-19_NW.gif)

![Daily confirmed cases 7th-15th March](https://github.com/jpolton/COVID-19/blob/master/FIGURES/COVID-19_London.gif)


## Data sources

* shapefiles:
  - Local Authority Districts (December 2017) Super Generalised Clipped Boundaries in Great Britain ``https://geoportal.statistics.gov.uk/datasets/local-authority-districts-december-2017-super-generalised-clipped-boundaries-in-great-britain/geoservice`` (This effectively masks non-metropolitan regions in the PHE covid19 data, as they report over larger regions in the non-metropolitan places.)
  - Local Authority Districts (December 2019) Boundaries UK BUC at 500m ``https://geoportal.statistics.gov.uk/datasets/local-authority-districts-december-2019-boundaries-uk-buc?geometry=-3.947%2C53.302%2C-0.591%2C53.872`` (This matches the PHE reporting regions for all but a couple of the reporting regions).


* Public Health England: ``https://www.gov.uk/government/publications/covid-19-track-coronavirus-cases`` UTLA cases table.

Might also look at the for following for tabulated, in time, data:
* ``https://github.com/emmadoughty/Daily_COVID-19/blob/master/COVID19_by_LA.csv``
* ``https://docs.google.com/spreadsheets/d/129bJR5Mgcr5qOQNc96CBWKFfjODToWKRiVKDEg5ybkU/edit#gid=1952384968``
* ``https://github.com/tomwhite/covid-19-uk-data/``


## Issues

* Some of the regions may not be accurately drawn if local authority boundaries have moved I.e. shapefile slightly out of date.


## Technical stuff

 **Aim:** Try out geopandas to colour shapefile polygons by field values.
 Here load a UK county council boundary shape file and tables of COVID-19 confirmed cases and plot.



### Python environment

 To get this code to work I build a bespoke python environment:

 `conda create -n geo_env
 conda activate geo_env
 conda config --env --add channels conda-forge
 conda config --env --set channel_priority strict
 conda install python=3 geopandas jupyter matplotlib numpy seaborn pysal pandas
 `

 Then
 ``conda activate geo_env``


 Or, trying the following to get Spyder working
 conda create --override-channels -c conda-forge -n covid19 python=3 geopandas jupyter matplotlib numpy seaborn pysal pandas spyder
 conda activate covid19

 But this didn't work for me. I couldn't get Spyder to work with geopandas :-(


 **author**: jpolton

 **date**: 11 March 2020
