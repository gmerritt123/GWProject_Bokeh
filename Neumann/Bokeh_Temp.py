# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 11:23:09 2024

@author: Gaelen
"""
import os
import sys

import numpy as np
from bokeh.plotting import figure, save, curdoc
from bokeh.models import CustomJS, HoverTool, ColumnDataSource, Slider, CustomJSTickFormatter, InlineStyleSheet, Div, Range1d
from bokeh.models import VeeHead, Arrow, Label
from bokeh.themes import Theme
from bokeh.layouts import column

wdir = r'C:\Repo\GWP_Work\Neumann' #when using in IDE locally
# wdir = os.path.dirname(os.path.realpath(__file__)) #when deploying

#style/theming loading
thm = Theme(filename=wdir+r'\\Bokeh_Styles.yaml') #read yaml file for some styling already hooked up
with open(wdir+'\\Bokeh_Styles.css','r') as f:
    css = f.read()
sl_style = InlineStyleSheet(css=css)

#slider layout
slider_dict = {
    'Q': Slider(title='Pumping rate (m³/s)', value=0, start=0, end=0.2, step = 0.001
                       ,format='0.000'
                       )
    ,'R':Slider(title='Radius from Well (m)',value=1,start=1,end=1000,step=1)
    ,'b': Slider(title='Aquifer thickness (m)',value=20 ,start=1, end=100, step = 0.01
                        ,format='0.00')

    ,'T':Slider(title='Aquifer Transmissivity (m²/s)',value = -2, start = -7, end = 0, step = 0.1
                        ,format=CustomJSTickFormatter(code="return (10**tick).toExponential(2).toString()") #handling log scale slider)
                        )
    ,'Ss':Slider(title='Specific Storage (1/m)',value = -4, start = -7, end = 0, step = 0.1
                        ,format=CustomJSTickFormatter(code="return (10**tick).toExponential(2).toString()") #handling log scale slider)
                        )
    ,'Sy':Slider(title='Specific Yield (dimensionless)',value = 0.2, start = 0.01, end = 0.5, step = 0.01
                        )
    }

#create figure
f = figure(height=800,width=800
           ,title='Neuman drawdown'
           # ,sizing_mode='stretch_both'
           ,x_axis_type='log'
           , y_axis_type='log'
           ,y_range=[0.01,10]
           ,x_range=[1,1e7]
           
           )

f.xaxis[0].axis_label = 'Time (s)'
f.yaxis[0].axis_label = 'Drawdown (m)'

#Theis Early datasource
et_src = ColumnDataSource(data={'dd': []
                             ,'t': []
                             }) #initialize completely empty, to be filled on first user action
#Theis late datasource
lt_src = ColumnDataSource(data={'dd': []
                             ,'t': []
                             }) #initialize completely empty, to be filled on first user action


src_dict = {'EarlyT':et_src
            ,'LateT':lt_src}

#theis renderers
etr = f.line(x='t',y='dd',line_color='blue',source=src_dict['EarlyT'],legend_label='Computed drawdown by early Theis')
ltr = f.line(x='t',y='dd',line_color='orange',source=src_dict['LateT'],legend_label='Computed drawdown by late Theis')


cb = CustomJS.from_file(path=wdir+r'\\cb.mjs', src_dict=src_dict,sl_dict=slider_dict,f=f)

#execute this callback when slider value changes
for sl in slider_dict.values():
    sl.js_on_change('value',cb)
    sl.stylesheets = [sl_style]
    sl.width=f.width
# f.x_range.range_padding=.9
# f.y_range.range_padding=.9

#layout
lo = column([sl for sl in slider_dict.values()]+[f]
            # ,sizing_mode = 'stretch_both'
            )


curdoc().theme = thm #assigns theme

save(lo,wdir+r'\\Theis_Testing.html',title='Theis Drawdown')

