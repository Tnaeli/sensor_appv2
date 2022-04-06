# -*- coding: utf-8 -*-
"""
Created on Tue May  4 14:20:40 2021

@author: Taneli Mäkelä
"""
import numpy as np
import pandas as pd
import datetime
import plotly.express as px
import plotly.offline
import jinja2



def plotlyplot_line(df1, legend_layout='bottom'):
    color_map = ['#379f9b', '#f18931', '#006431', '#bd3429',
                 '#814494', '#d82e8a', '#74aa50', '#006aa7']
    x1 = df1.index[0]
    x2 = df1.index[-1] + datetime.timedelta(hours=3)
    df1 = df1.melt(ignore_index=False, var_name='variable', value_name='value')


    fig = px.line(df1, x=df1.index, y="value", color="variable", width=1000, height=700,
                  range_x=[x1, x2], template='ggplot2', color_discrete_sequence=color_map)
    
    if legend_layout == 'bottom':
        fig.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="right",
            x=0.95
        ))
    if legend_layout == 'rightside':
        pass
    
    fig.update_traces(patch={"line": {'width':4, 'color': 'grey'}}, selector={'legendgroup': 'Makelankatu'})
    fig.update_traces(patch={"line": {'width':4, 'color': 'grey'}}, selector={'legendgroup': 'Refenrenssi'})
    return fig

def plotlyplot_bar(df1):
    color_map = ['#379f9b', '#f18931', '#006431', '#bd3429',
                 '#814494', '#d82e8a', '#74aa50', '#006aa7']

    df1 = df1.melt(ignore_index=False, var_name='variable', value_name='value')

    fig = px.bar(df1, x=df1.index, y="value", color="variable", barmode = 'group', width=1000, height=700, 
                  template='ggplot2', color_discrete_sequence = color_map)

    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.4,
        xanchor="right",
        x=0.95
    ))
    horizontal_x0 =df1.index[0] - datetime.timedelta(days=1)
    horizontal_x1 =df1.index[-1] + datetime.timedelta(days=1)
    
    fig.add_shape(type="line",
        x0=horizontal_x0, y0=50, x1=horizontal_x1, y1=50,
        line=dict(color="black", width=4, dash="dashdot"))
    return fig

def plotlyplot_scatter(df1, x):
    color_map = ['#379f9b', '#f18931', '#006431', '#bd3429',
                 '#814494', '#d82e8a', '#74aa50', '#006aa7']

    df1 = df1.melt(ignore_index=False, var_name='variable', value_name='value', id_vars=[x])

    fig = px.scatter(df1, x=x, y='value', facet_col='variable', color_discrete_sequence=color_map,
                    facet_col_wrap=4, trendline ='ols', width=1000, height=1000)

    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.4,
        xanchor="right",
        x=0.95
        ))
    return fig


def createTable(df):
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
                     ('border-width', '1px'),
                     ('padding', '5px'),
                     ('background-color', 'white'),
                     ]
    
    
    styles = [dict(selector="th", props=th_props),
              dict(selector="td", props=td_props)]
    
    df.index.name = 'timestamp(date&time)'
    df_style = df.style.set_table_styles(styles).format("{:.1f}").set_precision(1)
    return df_style


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
    return data

def parse_station_data(data_path_stations):
    data = read_ilmanetcsv(data_path_stations)
    
    data.columns = ['_'.join(col) for col in data.columns.values]
    data[data==-9999] = np.nan
    return data

def create_station_graph_div(station_data, component):
    data = station_data.filter(like=component).shift(periods=-1, freq='H')
    data = data.resample('D', label='left').mean().iloc[1:, :].round(1)
    data = data.dropna(how='all', axis=1)
    data_columns = {'1_pm10': 'Leppavaara','3_pm10':'PM_Tikkurila' ,'4_pm10':'Mannerheimintie' ,'5_pm10': 'Kallio','6_pm10': 'Vartiokyla',
                '7_pm10': 'Luukki','8_pm10': 'Tikkurila','9_pm10': 'Lohja','10_pm10': 'Tapanila','11_pm10': 'P-Tapiola',
                '12_pm10': 'Hämeenlinnanväylä','13_pm10': 'Lentokenttä','14_pm10': 'Järvenpää','17_pm10': 'Ammassuo 2','18_pm10': 'Makelankatu',
                '20_pm10': 'Blominmaki'}
    data.rename(columns=data_columns, inplace = True)
    data_div = plotly.offline.plot(plotlyplot_bar(data), show_link=False, output_type='div')
    return data_div
    

def loadTemplate(path, template):
    templateLoader = jinja2.FileSystemLoader(searchpath=path)
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = template
    template = templateEnv.get_template(TEMPLATE_FILE)
    return template

    

def createReport(data_Aqt, data_path_stations, savePath, template_folder, template_name, station_id=None, online=True, kartta='sensorikartta.html', legend_layout='bottom'):
    components = ['no2', 'no', 'co', 'o3', 'pm10', 'pm25', 'rh', 'temp']
    
    station_data = parse_station_data(data_path_stations)
    pm10_div = create_station_graph_div(station_data, 'pm10')
    
    
    data_dict = {}
    for component in components:
        data = data_Aqt[[component, 'loc_id']]
        data = pd.pivot_table(data, values=component,
                              index=data.index, columns='loc_id')
        if online:
            data = data.resample('H', label='right').mean().round(1)
        if station_id != None:
            if component in ['no', 'no2', 'pm10', 'pm25', 'o3']:
                refData = station_data.filter(like=f'{station_id}_')
                data = pd.concat([data, refData.loc[:, f'{station_id}_{component}'].rename('Makelankatu')],axis=1)
        data_dict[component] = data
        
    
    
    figs = {}
    figs_D = {}

    for component, data in data_dict.items():
        figs[component] = plotlyplot_line(data, legend_layout=legend_layout)
        figs_D[component] = plotlyplot_bar(data.resample('D', label='left').mean())  
        
    
    divs = {}
    divs_D = {}
    for component, fig in figs.items():
        divs[component] = plotly.offline.plot(fig, show_link=False, output_type='div')
        
    for component, fig in figs_D.items():
        divs_D[component] = plotly.offline.plot(fig, show_link=False, output_type='div')
    

                 

    aika = datetime.datetime.today().strftime("%Y-%m-%d %H:%M")
    template = loadTemplate(template_folder, template_name)
    outputText = template.render(aika=aika, divs = divs, divs_D = divs_D, pm10_div=pm10_div, kartta=kartta)

        
    with open(savePath, 'w', encoding='utf-8') as report:
        report.write(outputText)


def create_colocation_report(data_Aqt, data_path_stations, savePath, template_folder, template_name, station_id=None):
    # components = ['no2', 'no', 'o3', 'co', 'pm10', 'pm25', 'rh', 'temp']
    components = ['no2','pm10', 'pm25', 'rh', 'temp']
    
    station_data = parse_station_data(data_path_stations)
    
    data_dict = {}
    for component in components:
        data = data_Aqt[[component, 'sensor_id']]
        data = pd.pivot_table(data, values=component,
                              index=data.index, columns='sensor_id')
        data = data.resample('H', label='right').mean().round(1)
        if station_id != None:
            if component in ['no', 'no2', 'pm10', 'pm25', 'o3']:
                refData = station_data.filter(like=f'{station_id}_')
                data = pd.concat([data, refData.loc[:, f'{station_id}_{component}'].rename('Referenssi')],axis=1)
        data_dict[component] = data
    
    figs = {}
    figs_scatter = {}
    for component, data in data_dict.items():
        figs[component] = plotlyplot_line(data)

    for component, data in data_dict.items():
        if component in ['no', 'no2', 'pm10', 'pm25', 'o3']:
            figs_scatter[component] = plotlyplot_scatter(data, 'Referenssi')
        
    divs = {}
    divs_scatter = {}
    for component, fig in figs.items():
        divs[component] = plotly.offline.plot(fig, show_link=False, include_plotlyjs=False, output_type='div')      

    for component, fig in figs_scatter.items():
        divs_scatter[component] = plotly.offline.plot(fig, show_link=False, include_plotlyjs=False, output_type='div')     
        
    aika = datetime.datetime.today().strftime("%Y-%m-%d %H:%M")
    template = loadTemplate(template_folder, template_name)
    outputText = template.render(aika=aika, divs = divs, divs_scatter = divs_scatter)

        
    with open(savePath, 'w', encoding='utf-8') as report:
        report.write(outputText)
        
        
def create_HOPE_report(data_Aqt, data_path_stations, savePath, template_folder, template_name, station_id=None, online=True, kartta='hopekartta.html', legend_layout='bottom'):
    components = ['no2', 'no', 'co', 'o3', 'pm10', 'pm25', 'rh', 'temp']
    
    station_data = parse_station_data(data_path_stations)
    pm10_div = create_station_graph_div(station_data, 'pm10')
    
    regions = {"Makelankatu":'Vallila',
                "Marian sairaala":'Jatkasaari1',
                "Lansisatamankatu 34":'Jatkasaari2',
                "Selkamerenkatu 3":'Jatkasaari2',
                "Valimerenkatu 5":'Jatkasaari2',
                "Tyynenmerenkatu 3":'Jatkasaari2',
                "Lansisatamankatu apt":'Jatkasaari2',
                "Hyvantoivonkatu 7":'Jatkasaari1',
                "Atlankatinkatu 5":'Jatkasaari1',
                "Atlantinkatu 18":'Jatkasaari1',
                "Tyynenmerenkatu 14":'Jatkasaari2',
                "Hernesaari":'Jatkasaari1',
                "Teollisuuskatu 23":'Vallila',
                "Teollisuuskatu 3":'Vallila',
                "Sturenkatu 22":'Vallila',
                "Hameentie 95":'Vallila',
                "Smear III":'Vallila',
                "Hameentie 115":'Vallila',
                "Pirjontie 43":'Pakila1',
                "Pakilantie 55":'Pakila1',
                "Kylakunnantie 19":'Pakila1',
                "Palosuontie 2":'Pakila2',
                "Elonkuja 3":'Pakila2',
                "Kansantie 37":'Pakila1',
                "Elontie 111":'Pakila2',
                "Sysimiehentie 44":'Pakila2'}
    
    def plotlyplot_line_hope(df1, regions):
        color_map = ['#379f9b', '#f18931', '#006431', '#bd3429',
                     '#814494', '#d82e8a', '#74aa50', '#006aa7']
        x1 = df1.index[0]
        x2 = df1.index[-1] + datetime.timedelta(hours=3)
        df1 = df1.melt(ignore_index=False, var_name='variable', value_name='value')
        df1['region'] = df1['variable']
        df1['region'] = df1['region'].replace(regions)
        
        y1=df1['value'].min() - 3
        y2=df1['value'].max() + df1['value'].max() * 0.1
    
        fig = px.line(df1, x=df1.index, y="value", color="variable", facet_row='region', width=1000, height=2100,
                      range_x=[x1, x2],range_y=[y1,y2], template='ggplot2', color_discrete_sequence=color_map)
        
        fig.update_traces(patch={"line": {'width':4, 'color': 'grey'}}, selector={'legendgroup': 'Makelankatu'})
        fig.update_traces(patch={"line": {'width':4, 'color': 'grey'}}, selector={'legendgroup': 'Refenrenssi'})
        return fig
    
    station_data = parse_station_data(data_path_stations)
    
    data_dict = {}
    for component in components:
        data = data_Aqt[[component, 'loc_id']]
        data = pd.pivot_table(data, values=component,
                              index=data.index, columns='loc_id')
        data = data.resample('H', label='right').mean().round(1)
        if station_id != None:
            if component in ['no', 'no2', 'pm10', 'pm25', 'o3']:
                refData = station_data.filter(like=f'{station_id}_')
                data = pd.concat([data, refData.loc[:, f'{station_id}_{component}'].rename('Makelankatu')],axis=1)
        data_dict[component] = data
    
    figs = {}
    figs_D = {}

    for component, data in data_dict.items():
        figs[component] = plotlyplot_line_hope(data, regions)
        figs_D[component] = plotlyplot_bar(data.resample('D', label='left').mean())  
        
    
    divs = {}
    divs_D = {}
    for component, fig in figs.items():
        divs[component] = plotly.offline.plot(fig, show_link=False, output_type='div')
        
    for component, fig in figs_D.items():
        divs_D[component] = plotly.offline.plot(fig, show_link=False, output_type='div')
    

                 

    aika = datetime.datetime.today().strftime("%Y-%m-%d %H:%M")
    template = loadTemplate(template_folder, template_name)
    outputText = template.render(aika=aika, divs = divs, divs_D = divs_D, pm10_div=pm10_div, kartta=kartta)

        
    with open(savePath, 'w', encoding='utf-8') as report:
        report.write(outputText)
        






# regions = {'Pirjontie43':'Pakila1', 'Elontie111':'Pakila1', 'Kylakunnantie19':'Pakila1', 'sysimiehentie44':'Pakila1',
#            'kansantie37':'Pakila2', 'palosuontie2':'Pakila2', 'pakilantie55':'Pakila2', 'elonkuja3':'Pakila2',
#            'hameentie95':'Vallila', 'hameentie115':'Vallila', 'sturenkatu22':'Vallila', 
#            'teollisuuskatu23':'Vallila', 'kumpulasmear':'Vallila', 'teollisuuskatu3':'Vallila',
#            'hyvantoivonkatu7':'Jatkasaari1', 'hernesaari':'Jatkasaari1' ,'mariansairaala':'Jatkasaari1', 'atlantinkatu14':'Jatkasaari1', 
#             'atlantinkatu5':'Jatkasaari1', 'lansisatamankatu4th':'Jatkasaari1',
#             'tyynenmerenkatu14':'Jatkasaari2', 'tyynenmerenkatu3':'Jatkasaari2', 'selkamerenkatu3':'Jatkasaari2',
#             'valimerenkatu5':'Jatkasaari2', 'lansisatamankatu':'Jatkasaari2'}