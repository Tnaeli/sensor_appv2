# -*- coding: utf-8 -*-
"""
Created on Tue May  4 14:11:23 2021

@author: Taneli Mäkelä
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
# Base.metadata.create_all(engine)

class Location(Base):
    __tablename__ = 'Location'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True, nullable=False)
    address = Column(Text)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    device = relationship('Sensor', backref='loc', lazy=True)
    meas_raw = relationship('Sensor_data_raw', backref='loc', lazy=True)
    meas = relationship('Sensor_data', backref='loc', lazy=True)
    


class Sensor(Base):
    __tablename__ = 'Sensor'

    id = Column(Integer, primary_key=True)
    device = Column(String(20), nullable=False)
    name = Column(String(20), nullable=False)
    loc_id = Column(Integer, ForeignKey('Location.id'), nullable=False)
    active = Column(Integer, nullable=False)
    serial = Column(String(20), nullable=False)
    mog = Column(String(20), nullable=False)
    apikey = Column(String(32), nullable=False)
    date_started = Column(DateTime, nullable=False)
    no2_slope = Column(Float, default=1)
    no_slope = Column(Float, default=1)
    co_slope = Column(Float, default=1)
    o3_slope = Column(Float, default=1)
    pm10_slope = Column(Float, default=1)
    pm25_slope = Column(Float, default=1)
    pm1_slope = Column(Float, default=1)
    no2_bias = Column(Float, default=0)
    no_bias = Column(Float, default=0)
    co_bias = Column(Float, default=0)
    o3_bias = Column(Float, default=0)
    pm10_bias = Column(Float, default=0)
    pm25_bias = Column(Float, default=0)
    pm1_bias = Column(Float, default=0)
    meas_raw = relationship('Sensor_data_raw', backref='sensor', lazy=True)
    meas = relationship('Sensor_data', backref='sensor', lazy=True)
    


class Sensor_data_raw(Base):
    __tablename__ = 'Sensor_data_raw'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    no2 = Column(Float)
    no = Column(Float)
    co = Column(Float)
    o3 = Column(Float)
    pm10 = Column(Float)
    pm25 = Column(Float)
    pm1 = Column(Float)
    temp = Column(Float)
    rh = Column(Float)
    pres = Column(Float)
    ws = Column(Float)
    wd = Column(Float)
    rain = Column(Float)
    loc_id = Column(Integer, ForeignKey('Location.id'), nullable=False)
    sensor_id = Column(Integer, ForeignKey('Sensor.id'), nullable=False)
    
    
class Sensor_data(Base):
    __tablename__ = 'Sensor_data'

    id = Column(Integer, primary_key=True)
    loc_id = Column(Integer, ForeignKey('Location.id'), nullable=False)
    sensor_id = Column(Integer, ForeignKey('Sensor.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    no2 = Column(Float)
    no = Column(Float)
    co = Column(Float)
    o3 = Column(Float)
    pm10 = Column(Float)
    pm25 = Column(Float)
    pm1 = Column(Float)
    temp = Column(Float)
    rh = Column(Float)
    pres = Column(Float)
    no2_flag = Column(Integer, default=0)
    no_flag = Column(Integer, default=0)
    co_flag = Column(Integer, default=0)
    o3_flag = Column(Integer, default=0)
    pm10_flag = Column(Integer, default=0)
    pm25_flag = Column(Integer, default=0)
    pm1_flag = Column(Integer, default=0)
    temp_flag = Column(Integer, default=0)
    rh_flag = Column(Integer, default=0)
    pres_flag = Column(Integer, default=0)
    
class Sensor_data_60(Base):
    __tablename__ = 'Sensor_data_60'

    id = Column(Integer, primary_key=True)
    loc_id = Column(Integer, ForeignKey('Location.id'), nullable=False)
    sensor_id = Column(Integer, ForeignKey('Sensor.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    no2 = Column(Float)
    no = Column(Float)
    co = Column(Float)
    o3 = Column(Float)
    pm10 = Column(Float)
    pm25 = Column(Float)
    pm1 = Column(Float)
    temp = Column(Float)
    rh = Column(Float)
    pres = Column(Float)
    no2_flag = Column(Integer, default=0)
    no_flag = Column(Integer, default=0)
    co_flag = Column(Integer, default=0)
    o3_flag = Column(Integer, default=0)
    pm10_flag = Column(Integer, default=0)
    pm25_flag = Column(Integer, default=0)
    pm1_flag = Column(Integer, default=0)
    temp_flag = Column(Integer, default=0)
    rh_flag = Column(Integer, default=0)
    pres_flag = Column(Integer, default=0)
    
class Sensor_data_1440(Base):
    __tablename__ = 'Sensor_data_1440'

    id = Column(Integer, primary_key=True)
    loc_id = Column(Integer, ForeignKey('Location.id'), nullable=False)
    sensor_id = Column(Integer, ForeignKey('Sensor.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    no2 = Column(Float)
    no = Column(Float)
    co = Column(Float)
    o3 = Column(Float)
    pm10 = Column(Float)
    pm25 = Column(Float)
    temp = Column(Float)
    rh = Column(Float)
    pres = Column(Float)
    no2_flag = Column(Integer, default=0)
    no_flag = Column(Integer, default=0)
    co_flag = Column(Integer, default=0)
    o3_flag = Column(Integer, default=0)
    pm10_flag = Column(Integer, default=0)
    pm25_flag = Column(Integer, default=0)
    pm1_flag = Column(Integer, default=0)
    temp_flag = Column(Integer, default=0)
    rh_flag = Column(Integer, default=0)
    pres_flag = Column(Integer, default=0)
    
    
class Wxt_data(Base):
    __tablename__ = 'Wxt_data'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    temp = Column(Float)
    rh = Column(Float)
    pres = Column(Float)
    ws = Column(Float)
    wd = Column(Float)
    rain = Column(Float)
    loc_id = Column(Integer, ForeignKey('Location.id'), nullable=False)
    sensor_id = Column(Integer, ForeignKey('Sensor.id'), nullable=False)
    temp_flag = Column(Integer, default=0)
    rh_flag = Column(Integer, default=0)
    pres_flag = Column(Integer, default=0)
    ws_flag = Column(Integer, default=0)
    wd_flag = Column(Integer, default=0)
    
class Wxt_data_60(Base):
    __tablename__ = 'Wxt_data_60'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    temp = Column(Float)
    rh = Column(Float)
    pres = Column(Float)
    ws = Column(Float)
    wd = Column(Float)
    rain = Column(Float)
    loc_id = Column(Integer, ForeignKey('Location.id'), nullable=False)
    sensor_id = Column(Integer, ForeignKey('Sensor.id'), nullable=False)
    temp_flag = Column(Integer, default=0)
    rh_flag = Column(Integer, default=0)
    pres_flag = Column(Integer, default=0)
    ws_flag = Column(Integer, default=0)
    wd_flag = Column(Integer, default=0)
    
class Wxt_data_1440(Base):
    __tablename__ = 'Wxt_data_1440'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    temp = Column(Float)
    rh = Column(Float)
    pres = Column(Float)
    ws = Column(Float)
    wd = Column(Float)
    rain = Column(Float)
    loc_id = Column(Integer, ForeignKey('Location.id'), nullable=False)
    sensor_id = Column(Integer, ForeignKey('Sensor.id'), nullable=False)
    temp_flag = Column(Integer, default=0)
    rh_flag = Column(Integer, default=0)
    pres_flag = Column(Integer, default=0)
    ws_flag = Column(Integer, default=0)
    wd_flag = Column(Integer, default=0)
    
    
#----------------------------

# import pandas as pd   
# ini = pd.read_csv("C:\Koodit\sensor_appv2\IniFile.csv", sep= '\t', index_col=0)
# from sqlalchemy import create_engine
# path = f'postgresql://{ini.loc["user"][0]}:{ini.loc["pw"][0]}@{ini.loc["host"][0]}/{ini.loc["database"][0]}'
# engine = create_engine(path)
# Base.metadata.create_all(engine)

# locations = pd.read_csv("C:\Koodit\database_files\Location.csv", header=0, sep=';')
# sensors = pd.read_csv("C:\Koodit\database_files\Sensor_testi.csv", header=0, sep=',')

# from sqlalchemy.orm import sessionmaker

# def createSession(ini):
#     path = f'postgresql://{ini.loc["user"][0]}:{ini.loc["pw"][0]}@{ini.loc["host"][0]}/{ini.loc["database"][0]}'
#     engine = create_engine(path)
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     return session

# session = createSession(ini)
# locations.to_sql('Location', session.bind, index=False, if_exists=('append'))
# sensors.to_sql('Sensor', session.bind, index=False, if_exists=('append'))



#----------------------------

# Aqt.__table__.create(engine)
