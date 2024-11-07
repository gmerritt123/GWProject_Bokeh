# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 16:00:51 2024

@author: Gaelen Merritt
"""
import os
os.chdir(r'C:\Projects\GWP')

import numpy as np
from bokeh.plotting import figure, save, curdoc
from bokeh.models import CustomJS, HoverTool, ColumnDataSource, Slider, CustomJSTickFormatter, InlineStyleSheet
from bokeh.themes import Theme
from bokeh.layouts import column

thm = Theme(filename='Aqua_Base.yaml') #read yaml file for some styling already hooked up

#alternatively write css to target specific elements and apply as inline stylesheet to widgets
sl_css =   '''div.bk-slider-title{
                font-family: arial;
                font-weight: bold;
                font-size: 10pt;
                color: #17648D;
                '''
sl_iss = InlineStyleSheet(css=sl_css)

#create figure
f = figure(height=600,width=800
           ,title='Infiltration Capacity'
           ,x_range=[0,86400]
           )
#underlying data is in seconds, but display in hours
f.xaxis[0].formatter = CustomJSTickFormatter(code="return (tick/3600).toFixed(0)")

f.xaxis[0].axis_label = 'Time (hours)'
f.yaxis[0].axis_label = 'Rate (cm/hr)'

#create a datasource, which will get updated when user moves sliders
src = ColumnDataSource(data={'t':np.linspace(1,86400,1000) #time
                             ,'I':np.zeros(1000) #infiltration capacity
                             ,'P':np.zeros(1000) #precipitation rate
                             ,'R':np.zeros(1000) #holds the bottom of runoff area
                             })

#using src as the underlying source, add 3 renderers that run off different columns in src
#area glyph to show precipitation (as area bound by P and 0)
prec_rend = f.varea(x='t',y1='P',y2=0,fill_alpha=0.5,source=src,legend_label='Precipitation') 
#area glyph to show runoff (as area between precip and infiltrative capacity)
ro_rend = f.varea(x='t',y1='R',y2='I',fill_alpha=0.5,fill_color='red',source=src, legend_label='Runoff')
#line glyph to show infiltrative capacity
inf_rend = f.line(x='t',y='I',source=src,legend_label='Infiltration Capacity',line_width=4)

#creates sliders for the adjustable parameters
slider_dict = {'P':Slider(value=0,start=0,end=20,step=0.01,title='Precipitation Rate (cm/hr)')
               ,'Fc':Slider(value=0,start=0,end=10,step=0.01,title='Equilibrium Infiltration Rate (cm/hr)')
               ,'F_ini':Slider(value=0,start=0,end=20,step=0.01,title='Initial Infiltration Rate (cm/hr)')
               ,'K':Slider(value=np.log10(1e-5)
                           ,start=-5, end=-3
                           , step=0.1
                           , format=CustomJSTickFormatter(code="return (10**tick).toExponential(2).toString()") #handling log scale slider
                           ,title='Decay Coefficient')
               }

#the javascript that executes when user moves a slider
cb = CustomJS(args=dict(slider_dict=slider_dict, src= src 
                        ) #args --> dict passing python things into javascript side
              ,code='''
              //define honrtonian infiltration function
              function hortonian_inf(fc,f0,k,t){
                  return fc + (f0-fc)*Math.exp(-1*k*t)
                  }
              //collect slider values
              var fc = slider_dict['Fc'].value
              var f_ini = slider_dict['F_ini'].value
              var k = 10**slider_dict['K'].value
              var p = slider_dict['P'].value
              //populate infiltration rate by mapping time array to hortonian infiltration function
              var inf_a = src.data['t'].map(x=>hortonian_inf(fc,f_ini,k,x))
              //populate precipitation as simply the slider value repeated by mapping time array to prec slider value
              var p_a = src.data['t'].map(x=>slider_dict['P'].value)
              //calculate the lower bounds of the runoff area, using an if statement (ternary operator for shorthand)
              //logic is IF prec > infiltrative capacity, set to prec, otherwise set to infiltrative capacity
              var ro_a = inf_a.map((x,i) => p > x ? p : x)
              //assign these arrays to the src
              src.data['I'] = inf_a
              src.data['P'] = p_a
              src.data['R'] = ro_a
              src.change.emit()
              '''
              )

#hook up the above js code to execute whenever a slider value changes, and also assign stylesheet while we're looping through
for v in slider_dict.values():
    v.stylesheets=[sl_iss]
    v.js_on_change('value',cb)

curdoc().theme = thm #assigns theme
#builds a layout
lo = column([f]+list(slider_dict.values()))
#saves to html
save(lo,r'C:\Projects\GWP\InfCap.html',title='Hortonian Infiltration')



