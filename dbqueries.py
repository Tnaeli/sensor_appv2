# -*- coding: utf-8 -*-
"""
Created on Tue May  4 14:14:14 2021

@author: Taneli Mäkelä
"""
import pandas as pd
import numpy as np
import datetime
import requests
import xml.etree.ElementTree as ET
from database import Sensor_data, Sensor_data_raw, Sensor, Location, Sensor_data_60, Sensor_data_1440
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class AQTParser(object):
    '''
    AQTParser object is assigned to single Vaisala AQT-sensor and is used to 
    read data from Vaisala Beacon cloud database using API. Class has also
    methods to edit and flag data before storing it to database.
    Parsed data is stored in PostgreSQL-database in self.path variable to 
    table self.name.
    '''
    
    def __init__(self, loc_id, mogserial, apiKey, sensor_id, sensor_serial):
        self.loc_id = loc_id               # Table name for the database
        self.mogserial = mogserial
        self.apiKey = apiKey
        self.sensor_id = sensor_id
        self.sensor_serial = sensor_serial
        
    def loop_xml_file(self, root):
        childNodeList = {'timestamp':[],'meastype':[],'value':[]}
        for meas in root.iter("meas"):
            timestamp = meas.findtext("timestamp")
            meastype = meas.findtext("type")
            value = meas.findtext("value")
        
            childNodeList['timestamp'].append(timestamp)
            childNodeList['meastype'].append(meastype)
            childNodeList['value'].append(value)
            
        parsedDataFrame = pd.DataFrame(childNodeList)
        return parsedDataFrame

        
    
    #Parse data from Vaisala Beacon cloud database using API
    def parseFromBeacon(self, startTime):
        endTime = startTime + datetime.timedelta(days=7)
        payload = {'d': self.mogserial, 'k': self.apiKey, 't0': startTime.strftime("%Y-%m-%dT%H:%M:%S"), 
                   't1': endTime.strftime("%Y-%m-%dT%H:%M:%S"), 'c' : 90720}
        
        times = []
        times.append(datetime.datetime.now())
        print(f'start: {times[0]}')
        
        try:
            r = requests.get("http://beacon.vaisala.com/api/?", params=payload)
            if r.status_code == 200:
                times.append(datetime.datetime.now())
                print(f'Got response {(times[1] - times[0]).seconds}')
                root = ET.fromstring(r.content)
            else:
                print(datetime.datetime.now(), 'Error! Response status code:', r.status_code)
        except requests.exceptions.RequestException as e:  
            print (datetime.datetime.now(), payload['d'], e)
            
        
        parsedDataFrame = self.loop_xml_file(root)
        
        if parsedDataFrame.empty:
            try:
                payload = {'d': self.mogserial, 'k': self.apiKey, 't0': startTime.strftime("%Y-%m-%dT%H:%M:%S"), 't1': 
                           endTime.strftime("%Y-%m-%dT%H:%M:%S"), 's': f'AQT530-{self.sensor_serial}'}
                r = requests.get("https://wxbeacon.vaisala.com/api/xml?", params=payload)
                if r.status_code == 200:

                    times.append(datetime.datetime.now())
                    print(f'Got response {(times[1] - times[0]).seconds}')
                    root = ET.fromstring(r.content)
                else:
                    print(datetime.datetime.now(), 'Error! Response status code:', r.status_code)
            except requests.exceptions.RequestException as e:  
                print (datetime.datetime.now(), payload['d'], e)
            
            parsedDataFrame = self.loop_xml_file(root)
        
        parsedDataFrame = pd.pivot_table(parsedDataFrame, index='timestamp',
                                         columns='meastype', aggfunc='first')
        
        parsedDataFrame.columns = parsedDataFrame.columns.droplevel()
        data = parsedDataFrame.rename(columns={'Air Hum.': 'rh', 'Air Pres.':'pres', 'Air Temp.': 'temp',
                                        'CO': 'co', 'NO': 'no', 'NO2': 'no2', 'O3': 'o3', 'PM10': 'pm10', 
                                        'PM2.5': 'pm25','PM1': 'pm1', 'Wind Dir.': 'wd', 'Wind Speed': 'ws', 'Rain': 'rain',
                                        'Air temperature':'temp', 'Air pressure': 'pres', 'Relative humidity': 'rh'})

        data = data.apply(pd.to_numeric, errors = 'coerce')
        if not data.empty:
            if not 'pm1' in data.columns: 
                data['co'] = data['co'] * 1160
                data['no'] = data['no'] * 1247
                data['no2'] = data['no2'] * 1912
                data['o3'] = data['o3'] * 1996
                data['pm1'] = np.nan
            else: 
                data['co'] = data['co'] * 1.160
                data['no'] = data['no'] * 1.247
                data['no2'] = data['no2'] * 1.912
                data['o3'] = data['o3'] * 1.996
            data = data.round(2)
            
        times.append(datetime.datetime.now())
        print(f'Parsed data {(times[2] - times[1]).seconds}')
        
        return data
    
    #Apply correction factors and convert to ug/m3 (from ppm)
    def editBeaconData(self, data):
        data.index = pd.to_datetime(data.index, yearfirst = True).round('T')
        data = data.resample('T', label = 'left').first()
        data = data.tz_localize(tz='UTC')
        data = data.tz_convert('Europe/Helsinki')
        data = data.tz_localize(None)
        data = data.reset_index()

        return data
    
        
   
    #Inserting data to database after parsing, editing data and flagging. Returns True if no data was parsed
    def fetchAndEdit(self, starttime):
        
        # TODO: Syksyllä kellonjen siirto kaataa scriptin, koska koodi ei tiedä onko starttime kello 2-3 välillä kesäaikaa vai talviaikaa koska kellonaikoja on kahdet.
        starttime = (starttime + datetime.timedelta(seconds=30)).tz_localize(tz='Europe/Helsinki', ambiguous=False, nonexistent='shift_forward')
        starttime = starttime.tz_convert('UTC')
        starttime = starttime.tz_localize(None)
        
        data = self.parseFromBeacon(starttime)
        if data.empty == True:
            print('No data')
            return data
        else:
            data = self.editBeaconData(data)
            data['loc_id'] = self.loc_id
            data['sensor_id'] = self.sensor_id
            
            return data
        
        
def createSession(ini):
    path = f'postgresql://{ini.loc["user"][0]}:{ini.loc["pw"][0]}@{ini.loc["host"][0]}/{ini.loc["database"][0]}'
    engine = create_engine(path)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
        

def updateDatabase(session):
    # query active locations and sensors
    sensors = pd.read_sql_table('Sensor', con=session.bind)
    sensors = sensors[sensors.active == 1]
    if (sensors.serial.value_counts() > 1).any():
        return print(''''Warning! Found 2 or more sensors active with matching serials,
                     please set old duplicate sensors inactive''')

    for row in sensors.itertuples():        
        latest_timestamp = session.query(Sensor_data_raw).filter_by(
            sensor_id=row.id).order_by(Sensor_data_raw.timestamp.desc()).limit(1).first()
        if latest_timestamp != None:
            starttime = pd.Timestamp(latest_timestamp.timestamp)
        else:
            starttime = row.date_started
            if starttime > datetime.datetime.now(): # If start_date is in the future skip rest of the loop
                print(f'Measurements are not started yet. Date started is set to {starttime}')
                continue

        aqtObject = AQTParser(row.loc_id, row.mog, row.apikey, row.id, row.serial)
        data = aqtObject.fetchAndEdit(starttime)

        if not data.empty:
            data.to_sql('Sensor_data_raw', session.bind, index=False, if_exists=('append'))
            
            components = ['no2', 'no', 'co', 'o3', 'pm10', 'pm25', 'pm1']
            data = applyCorrection(sensors, data, components)
            data = flagErrorData(data)
            data.to_sql('Sensor_data', session.bind, index=False, if_exists=('append'))

    return 'Latest update {}'.format(pd.Timestamp(datetime.datetime.now()).round('T'))



def flagErrorData(data):
    df = data.copy()
    columnsToFlag = ['no2', 'no', 'o3', 'pm10', 'pm25', 'pm1', 'co', 'temp', 'rh']
    df = df.assign(**{'co_flag': 0, 'no_flag': 0, 'no2_flag': 0, 
                      'o3_flag': 0, 'pm10_flag': 0, 'pm25_flag': 0, 'pm1_flag': 0,
                      'rh_flag': 0, 'temp_flag': 0, 'pres_flag': 0})
    
    for column in columnsToFlag:
        if column in df.columns:
            #find consucutive values and flag
            # labels = df[column].diff().ne(0).cumsum()
            # df[[column + '_flag']] = (labels.map(labels.value_counts()) >= 40).astype(int)
            
            #find too high or low values and flag
            if column in ['no2', 'no', 'o3', 'pm10', 'pm25', 'pm1']:
                highValue = 1000
                lowValue = -5
            if column in ['co', 'rh']:
                highValue = 10000
                lowValue = -5
            if column == 'temp':
                highValue = 50
                lowValue = -40
        
            df.loc[(df[column] < lowValue) | (df[column] > highValue), column + '_flag'] = 2
    
    return df


def applyCorrection(sensors, data, components):
    df = data.copy()
    row = sensors[sensors.id == df.loc[0, 'sensor_id']]
    for component in components:
        slope = sensors.loc[sensors.id == row.id.values[0], component+'_slope'].values[0]
        intercept = sensors.loc[sensors.id == row.id.values[0], component+'_bias'].values[0]
        df[component] = df[component] * slope + intercept
    return df
    


def queryBetweenDates(session, sensors, locations, date1, date2):

    data = pd.read_sql(session.query(Sensor_data).filter(
        Sensor_data.timestamp.between(date1, date2)
    ).statement, session.bind)

    if data.empty:
        pass
    
    for  idx, row in sensors.iterrows():
        sensors.loc[idx, 'loc_id'] = locations.loc[row['loc_id'], 'name']

    legends = dict(zip(sensors.index.tolist(), sensors.name.tolist()))
    legends_loc = dict(zip(locations.index.tolist(), locations.name.tolist()))
    data['sensor_id'] = data['sensor_id'].replace(legends)
    data['loc_id'] = data['loc_id'].replace(legends_loc)

    data.index = data['timestamp']
    data = data.drop(columns='timestamp')
    data = data.sort_values(by=['timestamp', 'loc_id'], ascending=[True, True])

    return data

def queryBetweenDates_makelankatu(session, date1, date2):

    data = pd.read_sql(session.query(Sensor_data).filter(
        Sensor_data.timestamp.between(date1, date2)
    ).statement, session.bind)

    if data.empty:
        pass

    locs = pd.read_sql_table('Sensor', session.bind)
    legends = dict(zip(locs.id.tolist(), locs.name.tolist()))
    data['sensor_id'] = data['sensor_id'].replace(legends)

    data.index = data['timestamp']
    data = data.drop(columns='timestamp')
    data = data.sort_values(by=['timestamp', 'loc_id'], ascending=[True, True])

    return data



def updateDatabase_hour_avg(session):
    
    def count_validity(s):
        s_valid = s[s==0]
        not_valid = (len(s_valid) / 60 * 100) < 75
        return not_valid

    # query active locations and sensors
    sensors = pd.read_sql_table('Sensor', con=session.bind)
    sensors = sensors[sensors.active == 1]

    for row in sensors.itertuples():        
        latest_timestamp = session.query(Sensor_data_60).filter_by(
            sensor_id=row.id).order_by(Sensor_data_60.timestamp.desc()).limit(1).first()
        if latest_timestamp != None:
            starttime = pd.Timestamp(latest_timestamp.timestamp)
        else:
            starttime = pd.Timestamp(row.date_started)
            if starttime > datetime.datetime.now(): # If start_date is in the future skip rest of the loop
                print(f'Measurements are not started yet. Date started is set to {starttime}')
                continue
        end_time = pd.Timestamp(datetime.datetime.now()).floor('H') - datetime.timedelta(minutes=1)
        if end_time < starttime:
            print('No new data for hourly average calculation')
            continue
        
        new_values = pd.read_sql(session.query(Sensor_data).filter(
                                Sensor_data.timestamp.between(starttime, end_time),
                                Sensor_data.sensor_id == row.id).order_by(
                                    Sensor_data.timestamp).statement, session.bind)
        if not new_values.empty:
                                    
            new_values = new_values.fillna(value=np.nan)
            new_values.index = pd.to_datetime(new_values['timestamp'])
            new_values.drop(['id', 'timestamp', 'loc_id', 'sensor_id'], axis=1, inplace=True)
            new_values_flags = new_values.filter(like='flag')
            new_values = new_values[['no2', 'no', 'o3', 'pm10', 'pm25', 'pm1', 'co', 'temp', 'rh', 'pres']]
            
            new_values = new_values.resample('H', label='right').mean().round(2)
            new_values_flags = new_values_flags.resample('H', label='right').apply(count_validity)
            new_values = pd.concat([new_values, new_values_flags.astype(int)], axis=1)
            new_values['loc_id'] = row.loc_id
            new_values['sensor_id'] = row.id
            new_values = new_values.reset_index()
            new_values.to_sql('Sensor_data_60', session.bind, index=False, if_exists=('append'))
        else:
            print('No new data found for hourly average calculation')
        
        
def updateDatabase_day_avg(session):
    
    def count_validity(s):
        s_valid = s[s==0]
        not_valid = (len(s_valid) / 24 * 100) < 75
        return not_valid

    # query active locations and sensors
    sensors = pd.read_sql_table('Sensor', con=session.bind)
    # sensors = sensors[sensors.active == 1]


    for row in sensors.itertuples():        
        latest_timestamp = session.query(Sensor_data_1440).filter_by(
            sensor_id=row.id).order_by(Sensor_data_1440.timestamp.desc()).limit(1).first()
        if latest_timestamp != None:
            starttime = pd.Timestamp(latest_timestamp.timestamp) + datetime.timedelta(minutes=1)
        else:
            starttime = pd.Timestamp(row.date_started)
            if starttime > datetime.datetime.now(): # If start_date is in the future skip rest of the loop
                print(f'Measurements are not started yet. Date started is set to {starttime}')
                continue
        
        end_time = pd.Timestamp(datetime.datetime.now()).floor('D')
        if (end_time - datetime.timedelta(days=1)) < starttime:
            print('No new data for day average calculation')
            continue
        
        new_values = pd.read_sql(session.query(Sensor_data_60).filter(
                                Sensor_data_60.timestamp.between(starttime, end_time),
                                Sensor_data_60.sensor_id == row.id).order_by(
                                    Sensor_data_60.timestamp).statement, session.bind)
                                    
        new_values = new_values.fillna(value=np.nan)
        new_values.index = pd.to_datetime(new_values['timestamp'])
        new_values.drop(['id', 'timestamp', 'loc_id', 'sensor_id'], axis=1, inplace=True)
        new_values_flags = new_values.filter(like='flag')
        new_values = new_values[['no2', 'no', 'o3', 'pm10', 'pm25', 'pm1', 'co', 'temp', 'rh', 'pres']]
        
        new_values = new_values.resample('D', offset=1, label='left').mean().round(2)
        new_values_flags = new_values_flags.resample('D', offset=1, label='left').apply(count_validity)
        new_values = pd.concat([new_values, new_values_flags.astype(int)], axis=1)
        new_values['loc_id'] = row.loc_id
        new_values['sensor_id'] = row.id
        new_values.index = new_values.index.round('D').strftime('%Y-%m-%d')
        
        new_values = new_values.reset_index()
        new_values.to_sql('Sensor_data_1440', session.bind, index=False, if_exists=('append'))
        # break
    # return new_values

def delete_rows_between_dates(session, date1, date2, table):
    
    values = session.query(table).filter(table.timestamp.between(pd.Timestamp(date1), pd.Timestamp(date2)))
    df = pd.read_sql(values.statement, values.session.bind)
    values.delete(synchronize_session=False)
    session.commit()
    print(f'{len(df)} rows deleted between {date1} and {date2}')


# stmt = (
#     delete(Sensor_data_60).
#     where(Sensor_data_60.timestamp.between(pd.Timestamp('2022-02-22'), pd.Timestamp('2022-02-23')))
# )



# test = AQTParser(0, 'N3521230', '553ced636c594f54ba9c4267e8711f61', 30, 'T0510792')

# test_data = test.fetchAndEdit(pd.Timestamp('2022-02-21 08:00'))


# ini = pd.read_csv("C:\Koodit\sensor_appv2\IniFile.csv", sep= '\t', index_col=0)

# session = createSession(ini)

# delete_rows_between_dates(session, '2022-02-23', '2022-02-24', Sensor_data_60)

# sensors = pd.read_sql_table('Sensor', con=session.bind)

# test_data = updateDatabase_day_avg(session)

# test_data = test_data.reset_index()

# pd.Timestamp(datetime.datetime.now()).floor('D') - datetime.timedelta(minutes=1)