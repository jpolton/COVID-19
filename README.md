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
