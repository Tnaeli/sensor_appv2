# -*- coding: utf-8 -*-
"""
Created on Tue May  4 14:24:10 2021

@author: Taneli Mäkelä
"""
import numpy as np
import pandas as pd
import datetime
import folium
from folium import Marker
from folium.features import DivIcon

def read_ilmanetcsv(data_path):
    def customDateTime(datestr):
        if '24:00' in datestr:
            datestr = datestr.replace('24:00', '00:00')
            return pd.to_datetime(datestr, format="%d.%m.%Y %H:%M") + datetime.timedelta(days=1)
        else:
            return pd.to_datetime(datestr, format="%d.%m.%Y %H:%M")
        
    data = pd.read_csv(data_path, header=[0,1,2], parse_dates=True)
    data = data.drop(columns=data.filter(like='22').columns)
    data.columns = data.columns.droplevel(1)
    data.iloc[:,0] = data.iloc[:,0].apply(customDateTime)
    data = data.set_index(data.iloc[:,0])
    data.index = pd.to_datetime(data.index, format="%d.%m.%Y %H:%M")
    data = data.apply(pd.to_numeric, errors='coerce')
    data = data.rename(columns=str.lower).rename(columns={'pm2_5': 'pm25'})
    data.sort_index(inplace=True)
    return data

def airQualityTable(data, source='beacon'):
    columns = ['no2', 'pm10', 'pm25', 'co', 'no', 'o3', 'temp', 'rh']
    columns_flag = ['co', 'no', 'no2', 'o3', 'pm10', 'pm25', 'temp', 'rh',
                         'co_flag', 'no_flag', 'no2_flag', 'o3_flag', 'pm10_flag', 'pm25_flag']
    flags = ['co_flag', 'no2_flag',
                  'o3_flag', 'pm10_flag', 'pm25_flag']

    th_props = [('border-collapse', 'separate'),
                     ('border-spacing', '10px'),
                     ('font-size', '14px'),
                     ('text-align', 'center'),
                     #              ('font-weight', 'bold'),
                     ('color', '#6d6d6d'),
                     ('background-color', '#edf5f0'),
                     ('border-style', 'solid'),
                     ('border-width', '3px'),
                     ('border-color', '#edf5f0'),
                     ('padding', '5px'),
                     ('border-collapse', 'separate'),
                     ]

    # Set CSS properties for td elements in dataframe
    td_props = [('border-collapse', 'separate'),
                     ('border-spacing', '10px'),
                     ('font-size', '14px'),
                     ('text-align', 'center'),
                     ('border-style', 'solid'),
                     ('border-width', '4px'),
                     ('padding', '5px'),
                     ('background-color', 'white'),
                     ]
    
    
    styles = [dict(selector="th", props=th_props),
              dict(selector="td", props=td_props)]

    def validHours(df):
        dfCount = df.resample('H', label='right').count()
        df = df.resample('H', label='right').mean()
        df.iloc[dfCount < 45] = np.nan
        df = df.dropna(how='all')
        df = df.round(1)
        return df

    def calcIndex(concentration, component):

        indexValuesDict = {'no2': [0, 40, 70, 150, 200, 1000],
                           'co': [0, 4000, 8000, 20000, 30000, 50000],
                           'pm10': [0, 20, 50, 100, 200, 1000],
                           'pm25': [0, 10, 25, 50, 75, 500],
                           'o3': [0, 60, 100, 140, 180, 1000], }

        concValues = indexValuesDict[component]
        indexValues = [0, 50, 75, 100, 150, 1000]

        if concentration <= 0 or np.isnan(concentration):
            index = 0
            return index

        for i in range(len(concValues)-1):

            if (concentration > concValues[i]) & (concentration <= concValues[i+1]):
                upperLim = concValues[i+1]
                lowerLim = concValues[i]

                indexHigh = indexValues[i+1]
                indexLow = indexValues[i]

                break
            if concentration > indexValuesDict[component][-1]:
                index = 1000
                return index

        index = (concentration - lowerLim) * (indexHigh -
                                              indexLow) / (upperLim - lowerLim) + indexLow

        return index

    def addIndex(df, source):
        if source == 'beacon':
            index_columns = ['no2', 'co', 'pm10', 'pm25']
        elif source == 'fmi_api':
            index_columns = ['no2', 'co', 'pm10', 'pm25', 'o3']

        for columnName in df.columns:
            if columnName in index_columns:
                name = columnName + '_index'
                df[name] = df[columnName].apply(
                    calcIndex, args=(columnName,)).round(1)
        if not df.filter(like='_index', axis=1).empty:
            df['aqindex'] = df.filter(like='_index', axis=1).apply(max, axis=1)
        return df
    

    def cellBorderColor(s):
        if source == 'beacon':
            index_columns = ['no2', 'co', 'pm10', 'pm25']
        elif source == 'fmi_api':
            index_columns = ['no2', 'co', 'pm10', 'pm25', 'o3']
        component = s.name
        colors = []
        
        if component not in index_columns:
            for value in s:
                colors.append('border-color: white')
            return colors
        else: 
            for value in s:
                indexValue = calcIndex(value, component)

                if (indexValue <= 50):
                    color = 'green'
                elif (indexValue > 50) & (indexValue <= 75):
                    color = 'yellow'
                elif (indexValue > 75) & (indexValue <= 100):
                    color = 'orange'
                elif (indexValue > 100) & (indexValue <= 150):
                    color = 'red'
                elif indexValue >= 150:
                    color = 'purple'

                colors.append('border-color: %s' % color)

            return colors

    def cellTextColor(s, flagData):
        flags = flagData[s.name + '_flag'] > 0
        flags = flags.map({True: 'color: red', False: 'color: black'}).tolist()

        return flags

    def markerColor(df):
        indexValue = df.aqindex[-1]

        if (pd.Timedelta(datetime.datetime.now() - df.index[-1]).total_seconds() / 3600) > 3:
            color = 'black'
            return color

        elif (indexValue <= 50):
            color = 'green'
        elif (indexValue > 50) & (indexValue <= 75):
            color = '#e1f00c'
        elif (indexValue > 75) & (indexValue <= 100):
            color = 'orange'
        elif (indexValue > 100) & (indexValue <= 150):
            color = 'red'
        elif indexValue >= 150:
            color = 'purple'

        return color

    def textColor(flags_df):
        if flags_df.tails(1).values.any() > 0:
            color = 'red'
        else:
            color = 'grey'
        return color
    
    if source == 'beacon':
        data = data[columns_flag]
        data = validHours(data.astype('float'))

        flagData = data[flags]
        data = data[columns]
        data = addIndex(data, source)
        
        if not data.empty:
            markerColor = markerColor(data)
            markerText = data.filter(like='_index').idxmax(axis=1)[-1].split('_')[0]
        else:
            markerColor = 'black'
            markerText = 'NA'
        
        # data = data[['pm10', 'no2', 'co', 'pm25', 'o3', 'no', 'temp', 'rh', 'aqindex']]
        
        data = data[data.columns[data.columns.isin(['pm10', 'no2', 'co', 'pm25', 'o3', 'no', 'temp', 'rh', 'aqindex'])]]
        data.index.name = 'timestamp(date&time)'

        df_style = data.style.set_table_styles(
            styles).format("{:.1f}").set_precision(1)

        df_style = df_style.apply(cellBorderColor)
        df_style = df_style.apply(cellTextColor, subset=[
                                  'no2', 'co', 'pm10', 'pm25', 'o3'], **{'flagData': flagData})
        return df_style, markerColor, markerText
    
    elif source == 'fmi_api':
        columns = ['pm10', 'no2','pm25', 'o3']
        data = addIndex(data.dropna(how='all', axis = 1).dropna(how='all'), source)
        if 'aqindex' in data.columns:
            markerColor = markerColor(data)
            markerText = data.filter(like='_index').idxmax(axis=1)[-1].split('_')[0]
        else:
            markerColor='#3bb3d1'
            markerText = ''
            
        data.index.name = 'timestamp(date&time)'
        data.drop(columns=data.filter(like='_index', axis=1).columns, inplace=True)
        if not data.empty:
            if 'indeksi' in data.columns:
                data.drop(columns='indeksi', inplace=True)
            df_style = data.style.set_table_styles(styles).format("{:.1f}").set_precision(1)
    
            df_style = df_style.apply(cellBorderColor)
            return df_style, markerColor, markerText
        else:
            return 'No data', markerColor, markerText


def airQualityMarker(lat, lon, markerText, markerColor, tooltip, table, sensor=True):
    

    if sensor:
        html =  '''<svg width="55" height="25">
                      <circle cx="10" cy="10" r="8"
                      stroke=''' + markerColor + ''' stroke-width="3" fill="white" fill-opacity=0.5 />
                      <text fill="#000000" font-size="12" x="22" y="58%%">%s</text>
                    </svg>'''% markerText,
        icon = DivIcon(icon_size=(25, 25), icon_anchor=(9, 9),
                       html=html)
    else:
        html = '''<svg width="55" height="25">
                      <rect x="1" y="2" rx="2" ry="2" width="16" height="16"
                      stroke=''' + markerColor + ''' stroke-width="3" fill="white" fill-opacity=0.5 />
                     <text fill="#000000" font-size="12" x="20" y="55%%">%s</text>
                 </svg>'''% markerText,
        icon = DivIcon(icon_size=(25, 25), icon_anchor=(9, 9),
                       html=html)


    if markerColor == 'grey':
        marker = Marker([lat, lon], tooltip=tooltip, icon=icon,
                        popup='<h3>' + tooltip + '</h3>' + 'No data')
        return marker

    else:
        if table == 'No data':
            marker = Marker([lat, lon], tooltip=tooltip, icon=icon,
                            popup='<h3>' + tooltip + '</h3>'+table)
        else:
            marker = Marker([lat, lon], tooltip=tooltip, icon=icon,
                            popup='<h3>' + tooltip + '</h3>'+table.render())

        return marker


def sensorsToMap(session, data, m, legend='Sensors'):
    sensorLocations = pd.read_sql_table('Location', con=session.bind).set_index('name')
    sensorMarkers = folium.FeatureGroup(legend)
    
    for loc_id in data['loc_id'].value_counts().index:
        if loc_id == 'Supersite':
            pass
        else:
            data_id1 = data[data['loc_id'] == loc_id]
            table, markerColor, markerText = airQualityTable(data_id1, source='beacon')
            
            marker = airQualityMarker(sensorLocations.loc[loc_id, 'lat'], sensorLocations.loc[loc_id, 'lon'], 
                                      markerText.upper(), markerColor, f'Sensori: {loc_id}', table, sensor=True)
            marker.add_to(sensorMarkers)
    sensorMarkers.add_to(m)
    return m


def stationsToMap(stationLocations, m,data_path_stations, legend='Stations'):
    data = read_ilmanetcsv(data_path_stations)
    stationMarkers = folium.FeatureGroup(legend)
    for idx, row in stationLocations.iterrows():
        dfRef = data[str(row['Siteno'])].iloc[-8:, :]
        dfRef.dropna(how='all', axis=1, inplace=True)
        
        table, markerColor, markerText = airQualityTable(dfRef, source='fmi_api')
        
        marker = airQualityMarker( row['LAT'],  row['LON'], 
                                  markerText.upper(), markerColor, 'Mittausasema : ' + row['Name'], table, sensor=False)
        marker.add_to(stationMarkers)
    stationMarkers.add_to(m)
        
    return m

def addEnfuserLayers(foliumMap):
    layerNames = ['aqi', 'pm10', 'pm25', 'no2', 'o3']
    time_now = pd.Timestamp(datetime.datetime.today())
    image_timestamp = f'{time_now.year}-{time_now.month:02d}-{time_now.day:02d}-{time_now.hour:02d}-00-00'
    for layer in layerNames:
        image = f'https://ilmanlaatukartta.hsy.fi/{layer}-output/{image_timestamp}.png'

        fg=folium.FeatureGroup(name=layer, show=False)
        bounds = [[60.1321, 24.58], [60.368, 25.1998]]
        folium.raster_layers.ImageOverlay(image, bounds, origin='upper', colormap=None, 
                                          mercator_project=False, pixelated=True, name='AQI', overlay=True, 
                                          control=True, show=True, opacity=0.5).add_to(fg)
        fg.add_to(foliumMap)