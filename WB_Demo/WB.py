# -*- coding: utf-8 -*-
"""
Created on Fri Apr  4 11:09:01 2025

@author: Gaelen
"""


import pandas as pd
import numpy as np

import sys

sys.path.append(r'C:\Repo\GWProject_Bokeh')
import Bokeh_Util 

from bokeh.models import CustomJSTickFormatter, DataRange1d, Range1d, LinearAxis
from bokeh.plotting import figure, show, save
from bokeh.layouts import column, row
from bokeh.palettes import Colorblind
from bokeh.models import ColumnDataSource, LinearColorMapper, LinearAxis, CustomJS, Slider, ColorBar
from bokeh.models import HoverTool, GroupFilter,CDSView, Band, CustomJSTransform, DateRangeSlider
from bokeh.models import CustomJSTickFormatter
from bokeh.models import Div, InlineStyleSheet, Tooltip, HelpButton
from bokeh.models.dom import HTML
from bokeh.io import curdoc
import os

#where repo is cloned
os.chdir(r'C:\Repo\GWProject_Bokeh\WB_Demo')

#initialize dataset
df = pd.read_csv('Data.csv')
df['date'] = pd.to_datetime(df['date'])
df['AET'] = 0
df['Shallow Groundwater'] = 0
df['V'] = 0
df['Depth'] = 0
#Climate plot, not using for now.
cdf = pd.read_csv('ClimateData.csv').rename(columns={'PET':'cPET'})
cdf['date'] = pd.to_datetime(cdf['date'])
df= df.merge(cdf,how='inner',on='date')

#dummy/"manufactured" depth-volume relationship and surface-area volume relationship
import matplotlib.pyplot as plt
fig,ax = plt.subplots()
v = np.arange(0,5000,5)
d = 0.1*v**0.4
sa = v*1000/d
ax.plot(v,d)
ax.set_xlabel('Volume (ML)')
ax.set_ylabel('Mean Depth (m)')
fig,ax = plt.subplots()
ax.plot(v,sa/10000)
ax.set_xlabel('Volume (ML)')
ax.set_ylabel('Surface Area (Ha)')
stg_df = pd.DataFrame(data={'Volume':v,'Depth':d,'Surface Area':sa}).fillna(0) #this goes into the app 

#%%
src = ColumnDataSource(data = df)
stg_src = ColumnDataSource(stg_df)

title_div = Div(text='Reservoir Water Balance',stylesheets=[Bokeh_Util.getTheme('Aqua_Base')['DivTitle']])

with open(r'DescDiv.txt') as f:
    desc_str = f.read()

desc_div = Div(text=desc_str)

#main Water Balance Figure Diagram
fig = figure(height=500,width=1300,x_axis_type='datetime'
             ,y_range=[-100,100],title='Simulated Reservoir Water Balance')
fig.y_range.bounds=[-100,100]
fig.yaxis[0].axis_label = 'Outflow (-) / Inflow (+) Rate (ML/d)'
#alternate ticker, not using
# fig.yaxis[0].axis_label = 'Outflow (ML/d)   |    Inflow (ML/d)'
# from bokeh.models import CustomJSTickFormatter
# tck_fmt = CustomJSTickFormatter(code='''
#                                 return tick > 0 ? tick : tick*-1
#                                 ''')
# fig.yaxis[0].formatter = tck_fmt

#stackbars for inflows/outflows
in_rs = fig.vbar_stack(stackers=['Shallow Groundwater','Direct Precip','Runoff','Creek Inflow'],x='date'
                     ,color=Colorblind[6][0:4]
                     ,legend_label = ['Groundwater Inflow Rate (Simulated)','Direct Precipitation Inflow Rate (Observed)'
                                      ,'Runoff Inflow Rate (Simulated)','Creek Inflow Rate (Observed)']
                     ,source=src,width=pd.to_timedelta('1D')
                     )

out_rs = fig.vbar_stack(stackers=['AET','Dam Outflow','Seepage'],x='date'
                     ,color=Colorblind[7][4:7]
                     ,legend_label = ['Evaporation Outflow Rate (Simulated)','Dam Outflow Rate (Observed)','Groundwater Outflow Rate (Simulated)']
                     ,source=src,width=pd.to_timedelta('1D')
                     )

fig.x_range.range_padding = 0.01
fig.xaxis[0].axis_label='Year'

#depth and volume axes
fig.extra_y_ranges['d'] = Range1d(0,4
                                   ,bounds=(0,4)
                                  )
ax2 = LinearAxis(y_range_name='d',axis_label='Reservoir Depth (m)')
fig.add_layout(ax2,'right')
fig.line(x='date',y='Depth'
         ,line_color='blue',line_width=3,legend_label = 'Simulated Reservoir Depth (m)',source=src,y_range_name='d')
fig.line(x='date',y='Obs'
         ,line_color='blue',line_width=3, line_dash='dotted'
         ,legend_label = 'Observed Reservoir Depth (m)',source=src,y_range_name='d')
fig.extra_y_ranges['v'] = Range1d(0,5000
                                   # ,bounds=(-5000,5000)
                                  )
ax2 = LinearAxis(y_range_name='v',axis_label='Reservoir Volume (ML)')
fig.add_layout(ax2,'right')
fig.line(x='date',y='V'
         ,line_color='black',line_width=3,legend_label = 'Simulated Reservoir Volume (ML)',source=src,y_range_name='v',visible=False)

leg = fig.legend[0]
leg.click_policy = 'hide'
fig.add_layout(leg,'right')

#climate figure, not using
# cfig = figure(height=600,width=1600,x_axis_type='datetime'
#              ,y_range=[0,25],title='Climate',x_range=fig.x_range)

# cfig.extra_y_ranges['sp'] = Range1d(0,150)
# ax2 = LinearAxis(y_range_name='sp',axis_label='Snowpack (mm)')
# cfig.add_layout(ax2,'right')

# sr = cfig.varea(x='date',y1='snowpack',y2=0,fill_color='grey',legend_label='Snowpack (mm)'
#                 ,source=src,fill_alpha=0.25,y_range_name='sp')
# sm = cfig.vbar_stack(['snowmelt','rain'],x='date',width=pd.to_timedelta('1D')
#             ,fill_color=['cyan','blue'],fill_alpha=0.5,source=src,legend_label=['Snowmelt (mm)','Rain (mm)'],line_alpha=0)
# petr = cfig.line(x='date',y='cPET',line_color='salmon'
#                  ,legend_label = 'Potential Evapotranspiration (mm)',line_width=3,source=src)

#date range slider, not using in layout but is still getting passed to callback
#idea was it can be used to evaluate the water budget over arbitrary time range, but took out to try and keep app as simple as possible
pw = 65
dsl = DateRangeSlider(start=pd.to_datetime('Jan 1, 2019')
                      ,end=pd.to_datetime('September 29, 2023')
                      # ,step=pd.to_timedelta('1D')
                      ,value=[pd.to_datetime('Jan 1, 2019'),pd.to_datetime('September 29, 2023')]
                      ,width=1600-int(pw*2.8))


bd = Div(width=pw,text='') #padding div for making the slider align with the plot

#sliders and corresponding tooltips
ksl = Slider(value=-8,start=-9,end=-6,step=0.1,width=fig.width-200,title='Groundwater Outflow Coefficient (m/s)'
                          , format=CustomJSTickFormatter(code="return (10**tick).toExponential(2).toString()") 
                          )
kdesc = Tooltip(content=HTML("The volume of groundwater outflow leaving a reservoir is a function of reservoir depth, reservoir surface area, and material permeability. This slider controls that permeability."
            ),position='right')
khelp = HelpButton(tooltip=kdesc)

bsl = Slider(value=0.5,start=0,end=1.0,step=0.01,width=fig.width-200,title='Fraction of Catchment Recharge routed to Reservoir')
bdesc = Tooltip(content=HTML("Some fraction of recharge within the reservoir's catchment area will reach the reservoir as baseflow/interflow (the rest will travel deeper to more regional flow features). This slider controls that fraction."
            ),position='right')
bhelp = HelpButton(tooltip=bdesc)

#divs for the d3 canvas
d3_divTitle = Div(height=25,width=1000,text='Simulated Reservoir Water Balance: 2019-2023',stylesheets=[Bokeh_Util.getTheme('Aqua_Base')['DivTitle']])
d3_div = Div(text='',width=1000,height=500)

#read in js code
cb = CustomJS.from_file(path=r'cb.mjs', src=src,dsl=dsl,d3_div=d3_div
                        ,pl =Colorblind[7]
                        ,ksl = ksl, bsl = bsl, stg_src= stg_src)
#js code to trigger when slider values change
dsl.js_on_change('value',cb)
bsl.js_on_change('value',cb)
ksl.js_on_change('value',cb)

#load core js functions for html-template
with open(r'C:\Repo\GWProject_Bokeh\Bokeh_Util.js') as f:
    d3_util = f.read()

#build layout and write html
Bokeh_Util.save_html_wJSResources(bk_obj=column([title_div,
                                                  desc_div,
                                                 # row([bd,dsl]),
                                                 row([bsl,bhelp]),row([ksl,khelp]),fig,d3_divTitle,d3_div])
                                  , fname='WB.html'
                                  , resources_list_dict={'sources':['https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.0/d3.min.js'
                                                                    ,'https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js']
                                                          ,'scripts':[d3_util]}
                                  ,html_title='Reservoir Water Balance'
                                  ,theme=Bokeh_Util.getTheme('Aqua_Base')['yaml'])
#%%

