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
    meas_raw = relationship('Aqt_raw', backref='loc', lazy=True)
    meas = relationship('Aqt', backref='loc', lazy=True)
    


class Sensor(Base):
    __tablename__ = 'Sensor'

    id = Column(Integer, primary_key=True)
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
    no2_bias = Column(Float, default=0)
    no_bias = Column(Float, default=0)
    co_bias = Column(Float, default=0)
    o3_bias = Column(Float, default=0)
    pm10_bias = Column(Float, default=0)
    pm25_bias = Column(Float, default=0)
    no2_state = Column(Integer, default = 1)
    no_state = Column(Integer, default = 1)
    co_state = Column(Integer, default = 1)
    o3_state = Column(Integer, default = 1)
    pm10_state = Column(Integer, default = 1)
    pm25_state = Column(Integer, default = 1)
    temp_state = Column(Integer, default = 1)
    rh_state = Column(Integer, default = 1)
    pres_state = Column(Integer, default = 1)
    ws_state = Column(Integer, default = 1)
    wd_state = Column(Integer, default = 1)
    rain_state = Column(Integer, default = 1)
    meas_raw = relationship('Aqt_raw', backref='sensor', lazy=True)
    meas = relationship('Aqt', backref='sensor', lazy=True)


class Aqt_raw(Base):
    __tablename__ = 'Aqt_raw'

    id = Column(Integer, primary_key=True)
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
    ws = Column(Float)
    wd = Column(Float)
    rain = Column(Float)
    loc_id = Column(Integer, ForeignKey('Location.id'), nullable=False)
    sensor_id = Column(Integer, ForeignKey('Sensor.id'), nullable=False)
    
    
class Aqt(Base):
    __tablename__ = 'Aqt'

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
    ws = Column(Float)
    wd = Column(Float)
    rain = Column(Float)
    no2_flag = Column(Integer, default=0)
    no_flag = Column(Integer, default=0)
    co_flag = Column(Integer, default=0)
    o3_flag = Column(Integer, default=0)
    pm10_flag = Column(Integer, default=0)
    pm25_flag = Column(Integer, default=0)
    temp_flag = Column(Integer, default=0)
    rh_flag = Column(Integer, default=0)
    pres_flag = Column(Integer, default=0)
    ws_flag = Column(Integer, default=0)
    wd_flag = Column(Integer, default=0)
    rain_flag = Column(Integer, default=0)
    
    
    
# ini = pd.read_csv('iniFile.csv', sep= '\t', index_col=0)
# import pandas as pd
# from sqlalchemy import create_engine
# ini_HOPE = pd.read_csv('iniFile_HOPE.csv', sep= '\t', index_col=0)

# path = f'postgresql://{ini.loc["user"][0]}:{ini.loc["pw"][0]}@{ini.loc["host"][0]}/{ini.loc["database"][0]}'
# path = f'postgresql://{ini_HOPE.loc["user"][0]}:{ini_HOPE.loc["pw"][0]}@{ini_HOPE.loc["host"][0]}/{ini_HOPE.loc["database"][0]}'

# engine = create_engine(path)
# Aqt.__table__.create(engine)
# Base.metadata.create_all(engine)